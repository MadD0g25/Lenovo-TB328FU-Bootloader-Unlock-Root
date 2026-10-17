#!/usr/bin/env python3
"""TB328FU exact-build RAM unlock experiment. Default operations are OFFLINE.

No command writes SPL/U-Boot partitions or erases userdata. Executing cboot
can write miscdata and can invalidate encrypted data. Hardware is unvalidated.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import threading
from datetime import datetime, timezone

FDL_SHA='a9cf547c81893023f0fc1cc919cbd4055bfc398a9007afcbba5607b76333383e'
UBOOT_SHA='83e7039a21c25688918a19fd8eb8770f1141b0dac8b84ba379df53bae4d3a05e'
CURRENT_FULL={'sml_a.bin':(1048576,'7ed64933234c97975b254a7a474bb6ad23cfea475fc04961c374b9ac120d412b'),
 'teecfg_a.bin':(1048576,'2fe1c28170cf622f7b7e109ea1ff96cd39763c120a6e1538effb7ba01293c3e5'),
 'trustos_a.bin':(6291456,'5207375f8ea1ec29b4976377e4ad0504f957d03b2b169e3685284ad2e321e29d')}
FIXED_GENERATED={'fdl1-boot-v9.bin':'f0b87ca029eec5ddd3cce7d654d733d182996989eb8e5c729f9748f72806964d',
 'fdl1-dl.bin':FDL_SHA,
 'fdl2-dl.bin':'3802b0fddfb8b7e9708974f260e957f784c6eb087c9ac737d352139067ac30c0',
 'cboot-v9-S200162.bin':'fd2698c4f19e24840d70b6cae65f46d322918e5ba105795f306b11ad00622025'}
PAYLOAD_HASHES={
 'sml_a.bin':'550b0992dab36e50e473bee154c024d21ddb768396e3f478ee0e8da632177f04',
 'teecfg_a.bin':'224a8c966765437188e776a8c0898b77344ba560db6ce279a070f774ca14544e',
 'trustos_a.bin':'84634a31233b485d31f6e65d552d627f5b9cc0a3a83e1b7c8a17216bbc2501d6'}
HEADER_BASE=0x9efffe00
HOOK=0x20ee0
CAVE=0x83990
SETTER=0x7932c
LOADS={'cboot-v9-S200162.bin':0x9efffe00,'teecfg-ram.bin':0x9403fe00,
       'trustos-ram.bin':0x9405fe00,'sml-ram.bin':0x93fffe00}

def sha(b):return hashlib.sha256(b).hexdigest()
def word(b,o):
    if o<0 or o+4>len(b):raise ValueError('Truncated word')
    return struct.unpack_from('<I',b,o)[0]
def read(p):
    p=Path(p)
    if not p.is_file() or p.stat().st_size>16*1024*1024:raise ValueError('Missing/oversize file: '+str(p))
    return p.read_bytes()
def savejson(p,v):Path(p).write_text(json.dumps(v,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')

def record_diff(before,after):
    a=read(before);b=read(after)
    if len(a)!=1048576 or len(b)!=1048576:raise ValueError('Both miscdata captures must be exactly 1 MiB')
    offsets=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    old=a[8192:8704];new=b[8192:8704]
    return dict(before_sha256=sha(a),after_sha256=sha(b),changed_bytes=len(offsets),
        first_64_changed_offsets=[hex(x) for x in offsets[:64]],
        sector_0x2000=dict(unchanged=old==new,changed_bytes=sum(x!=y for x,y in zip(old,new)),
                         before_all_zero=not any(old),after_all_zero=not any(new)),
        unlock_proven=False,note='Only stock boot verification can confirm an effective persistent unlock; record nonzero alone is insufficient')

def parse_image(b,require_hash=True):
    if len(b)<512 or b[:4]!=b'DHTB':raise ValueError('Not a complete DHTB image')
    n=word(b,48);end=512+n
    if n==0 or end>len(b):raise ValueError('Invalid payload bounds')
    computed=sha(b[512:end]);valid=b[8:40].hex()==computed
    if require_hash and not valid:raise ValueError('DHTB payload hash mismatch')
    if end+96>len(b):raise ValueError('Missing footer')
    magic=b[end:end+8]
    if magic not in (b'SIMGHDR\0',bytes(8)):raise ValueError('Unknown footer format')
    size,offset=struct.unpack_from('<QQ',b,end+16)
    if size!=n or offset!=512:raise ValueError('Unexpected signed payload mapping')
    footprint=end+96
    for i in (0x20,0x30,0x40,0x50):
        size,offset=struct.unpack_from('<QQ',b,end+i)
        if size:
            if not offset or offset>len(b) or size>len(b)-offset:raise ValueError('Certificate outside file')
            footprint=max(footprint,size+offset)
    return dict(size=len(b),payload_size=n,payload_sha256=computed,hash_matches=valid,
                footprint=footprint,footer_magic=magic.hex())

def signed_trim(b):
    h=parse_image(b)
    if any(b[h['footprint']:]):raise ValueError('Nonzero trailing data; refusing trim')
    return b[:h['footprint']]

def branch(src,dst,link=False):
    delta=dst-src
    if delta%4 or not -(1<<27)<=delta<(1<<27):raise ValueError('Branch out of range/alignment')
    return (0x94000000 if link else 0x14000000)|((delta>>2)&0x3ffffff)
def branch_target(src,w):
    if w>>26 not in (5,37):raise ValueError('Not B/BL')
    imm=w&0x3ffffff
    if imm&(1<<25):imm-=1<<26
    return src+imm*4
def movz64(reg,imm,shift=0):
    if reg not in range(31) or not 0<=imm<=65535 or shift not in (0,16,32,48):raise ValueError('Invalid MOVZ')
    return 0xd2800000|((shift//16)<<21)|(imm<<5)|reg

def patch_fdl1(b):
    if sha(b)!=FDL_SHA:raise ValueError('Wrong FDL1; exact SHA required')
    if b[0xac08:0xac14]!=bytes.fromhex('1f2003d5')*3 or word(b,0xae94)!=0x52802040:
        raise ValueError('FDL1 preconditions differ')
    out=bytearray(b)
    struct.pack_into('<I',out,0xac08,movz64(0,0x9406,16))
    struct.pack_into('<I',out,0xac0c,movz64(1,0x9404,16))
    struct.pack_into('<I',out,0xae94,0x52802080)
    return bytes(out)

def patch_uboot(b):
    if sha(b)!=UBOOT_SHA:raise ValueError('Wrong U-Boot; S200162 exact dump required')
    h=parse_image(b)
    if word(b,HOOK)!=0x94015e30 or b[CAVE:CAVE+28]!=bytes(28):raise ValueError('Hook or cave changed')
    if b[HOOK+4:HOOK+16]!=bytes.fromhex('f35341a9fd7bc3a800beb3d2'):raise ValueError('Epilogue differs')
    if word(b,SETTER)!=0xd10803ff or b'VerifiedBoot-UNLOCK' not in b:raise ValueError('Setter differs')
    # Refuse even a direct branch into the apparent padding selected for this
    # exact image. This cannot prove absence of all indirect/data references.
    for o in range(512,CAVE,4):
        w=word(b,o)
        if w>>26 in (5,37) and CAVE<=branch_target(o,w)<CAVE+28:
            raise ValueError('Existing direct branch into cave')
    original_call=branch_target(HOOK,word(b,HOOK))
    continuation=branch_target(HOOK+16,word(b,HOOK+16))
    stub=[branch(CAVE,original_call,True),0x52800020,branch(CAVE+8,SETTER,True),
          word(b,HOOK+4),word(b,HOOK+8),word(b,HOOK+12),branch(CAVE+24,continuation)]
    out=bytearray(b[:h['footprint']])
    struct.pack_into('<I',out,HOOK,branch(HOOK,CAVE))
    struct.pack_into('<7I',out,CAVE,*stub)
    # Integrity only. The original vendor RSA signature is now stale; this
    # image is solely for the RAM experiment through the bypassed FDL1.
    out[8:40]=hashlib.sha256(out[512:512+h['payload_size']]).digest()
    return bytes(out)

def assert_no_overlap(entries):
    spans=sorted((base,base+size,name) for name,base,size in entries)
    for a,b in zip(spans,spans[1:]):
        if a[1]>b[0]:raise ValueError('RAM overlap: '+a[2]+' / '+b[2])
    return spans

def build(backup,assets,output,reference_tos=None):
    backup=Path(backup).resolve();assets=Path(assets).resolve();output=Path(output).resolve()
    for source in (backup,assets):
        if output==source or source in output.parents:raise ValueError('Output must be outside input folders')
    if output.exists() and any(output.iterdir()):raise ValueError('Output must be empty/new')
    paths={n:backup/n for n in ['uboot_a.bin','sml_a.bin','teecfg_a.bin','trustos_a.bin']}
    if reference_tos:paths['trustos_a.bin']=Path(reference_tos).resolve()
    inputs={n:read(p) for n,p in paths.items()}
    fd=read(assets/'fdl1-dl.bin');dl=read(assets/'fdl2-dl.bin')
    if sha(dl)!='3802b0fddfb8b7e9708974f260e957f784c6eb087c9ac737d352139067ac30c0':raise ValueError('Wrong download FDL2')
    for n,wanted in PAYLOAD_HASHES.items():
        if parse_image(inputs[n])['payload_sha256']!=wanted:raise ValueError('Unreviewed secure payload: '+n)
    if not reference_tos:
        for n,(size,wanted) in CURRENT_FULL.items():
            if len(inputs[n])!=size or sha(inputs[n])!=wanted:
                raise ValueError('Current BACKUP1 image does not match the reviewed report: '+n)
    generated={'fdl1-boot-v9.bin':patch_fdl1(fd),'fdl1-dl.bin':fd,'fdl2-dl.bin':dl,
               'cboot-v9-S200162.bin':patch_uboot(inputs['uboot_a.bin']),
               'sml-ram.bin':signed_trim(inputs['sml_a.bin']),
               'teecfg-ram.bin':signed_trim(inputs['teecfg_a.bin']),
               'trustos-ram.bin':signed_trim(inputs['trustos_a.bin'])}
    spans=assert_no_overlap([(n,base,len(generated[n])) for n,base in LOADS.items()])
    manifest=dict(version=9,status='EXPERIMENTAL_NOT_HARDWARE_VALIDATED',
        hardware_ready=False if reference_tos else True,
        hardware_ready_meaning='Input completeness only, NEVER proof of successful unlocking',
        blocking_reason='Current BACKUP1 trustos is missing; reference image substituted for offline tests only' if reference_tos else None,
        generated_utc=datetime.now(timezone.utc).isoformat(),
        inputs={n:dict(size=len(v),sha256=sha(v),path=str(paths[n])) for n,v in inputs.items()},
        files={n:dict(size=len(v),sha256=sha(v)) for n,v in generated.items()},
        ram_spans=[dict(start=a,end=b,file=n) for a,b,n in spans],
        uboot_patch=dict(hook=HOOK,cave=CAVE,setter=SETTER,rsa_signature_valid=False,
            note='Apparent zero padding, no direct B/BL refs; all indirect uses not disproved'),
        warning='Executing cboot can persist miscdata changes and invalidate encrypted user data')
    output.mkdir(parents=True,exist_ok=True)
    for n,v in generated.items():(output/n).write_bytes(v)
    savejson(output/'manifest.json',manifest)
    return manifest

def validate_bundle(folder):
    folder=Path(folder).resolve();m=json.loads(read(folder/'manifest.json'))
    expected={'fdl1-boot-v9.bin','fdl1-dl.bin','fdl2-dl.bin','cboot-v9-S200162.bin','sml-ram.bin','teecfg-ram.bin','trustos-ram.bin'}
    if m.get('version')!=9 or set(m.get('files',{}))!=expected:raise ValueError('Unexpected bundle files')
    data={n:read(folder/n) for n in expected}
    for n,b in data.items():
        if len(b)!=m['files'][n]['size'] or sha(b)!=m['files'][n]['sha256']:raise ValueError('Bundle corrupted: '+n)
        if n in FIXED_GENERATED and sha(b)!=FIXED_GENERATED[n]:raise ValueError('Unreviewed executable: '+n)
    assert_no_overlap([(n,base,len(data[n])) for n,base in LOADS.items()])
    if m.get('hardware_ready'):
        for original,n in [('sml_a.bin','sml-ram.bin'),('teecfg_a.bin','teecfg-ram.bin'),('trustos_a.bin','trustos-ram.bin')]:
            size,wanted=CURRENT_FULL[original];b=data[n]
            if len(b)>size or sha(b+bytes(size-len(b)))!=wanted:
                raise ValueError('Current secure image check failed: '+n)
    return m

def capture_command(assets,output,spd):
    assets=Path(assets).resolve();output=Path(output).resolve()
    cmd=[str(Path(spd).resolve()),'--wait','120','exec_addr','0x3ee8',
        'fdl',str(assets/'fdl1-dl.bin'),'0x5500','fdl',str(assets/'fdl2-dl.bin'),'0x9efffe00','exec',
        'path',str(output),'r','uboot_a','r','sml_a','r','teecfg_a','r','trustos_a','r','misc','r','miscdata',
        'partition_list',str(output/'partition-current.xml'),'exit']
    return cmd

def capture(assets,output,spd,execute=False):
    assets=Path(assets).resolve();output=Path(output).resolve()
    for n in ['fdl1-dl.bin','fdl2-dl.bin']:
        if sha(read(assets/n))!=FIXED_GENERATED[n]:raise ValueError('Unreviewed download loader: '+n)
    cmd=capture_command(assets,output,spd)
    print(subprocess.list2cmdline(cmd))
    if not execute:
        print('OFFLINE capture plan only.');return 0
    if output.exists():raise ValueError('Capture output must be a new folder; no backups overwritten')
    if not Path(spd).is_file():raise ValueError('spd_dump missing')
    print('This executes privileged download loaders, requests reads only, and does not reset automatically.')
    if input('Type AUTORISER LECTURE V9: ')!='AUTORISER LECTURE V9':raise ValueError('Cancelled')
    output.mkdir(parents=True)
    print('Power off, unplug, and use the known physical BootROM combination when waiting.')
    input('Press Enter to start: ')
    with (output/'capture.log').open('w',encoding='utf-8') as f:
        p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,cwd=output,timeout=300)
    if p.returncode:raise ValueError('Capture transport failed; inspect capture.log')
    for n in ['uboot_a.bin','sml_a.bin','teecfg_a.bin','trustos_a.bin','misc.bin','miscdata.bin']:
        b=read(output/n)
        if not b or not any(b):raise ValueError('Missing/zero capture: '+n)
    print('Capture complete. No unlock or reset performed.');return 0

def command(folder,spd):
    folder=Path(folder).resolve()
    # After the first FDL1 auto-exec, repeated `fdl` transfers each finish
    # with END_DATA but do not execute. SML must be last. `send` deliberately
    # omits END_DATA in this spd_dump source, so it is not used here.
    return [str(Path(spd).resolve()),'--wait','120','exec_addr','0x3ee8',
        'fdl',str(folder/'fdl1-boot-v9.bin'),'0x5500',
        'fdl',str(folder/'cboot-v9-S200162.bin'),'0x9efffe00',
        'fdl',str(folder/'teecfg-ram.bin'),'0x9403fe00',
        'fdl',str(folder/'trustos-ram.bin'),'0x9405fe00',
        'fdl',str(folder/'sml-ram.bin'),'0x93fffe00','exec']

# The known Windows build loads custom_exec_no_verify_3ee8.bin from the
# working directory. The original V9 launched it with an unpredictable cwd.
# All files/hashes below were checked against the ORIGINAL working package.
KNOWN_SPD_FILES={
    'spd_dump.exe':'407d1f64e8cba64bbc5baaee8f8dbea067c06c724f5b0dcc13966780b45ad451',
    'custom_exec_no_verify_3ee8.bin':'3def40ed711d28233fd9c9a577558d2943fcda28638bb30307f0e6357f336ce1',
    'Channel9.dll':'79edbd9e4ae5d1d8b572d8663eb921069736ef0b7ee661920d3cde9855bc3d4f',
    'Channel.ini':'f6a4d42665246d87b5704db77b0691ba68ab3b8a9f4456bd41c4131e5ec18645',
}
def preflight_spd(spd):
    exe=Path(spd).resolve()
    if exe.name.lower()!='spd_dump.exe':raise ValueError('Expected spd_dump.exe')
    for name,wanted in KNOWN_SPD_FILES.items():
        file=exe.parent/name
        if not file.is_file():raise ValueError('STOP: missing required tool dependency: '+str(file))
        if sha(read(file))!=wanted:raise ValueError('STOP: incorrect tool version or modified dependency: '+str(file))
    return exe

def run_streamed(cmd,cwd,logfile,timeout=240):
    # Stream live progress AND save evidence, so a user can see the waiting
    # prompt before physically connecting the tablet. Never mark timeout success.
    import subprocess
    result={}
    with logfile.open('w',encoding='utf-8') as f:
        proc=subprocess.Popen(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,bufsize=0)
        def drain():
            for raw in iter(proc.stdout.readline,b''):
                line=raw.decode('utf-8',errors='replace')
                print(line,end='',flush=True)
                f.write(line);f.flush()
        thread=threading.Thread(target=drain,daemon=True)
        thread.start()
        try:
            code=proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            print('STOP: spd_dump did not finish before timeout; terminating process.')
            proc.kill();proc.wait();code=124
        thread.join(timeout=5)
    return code

def execute_hardware(folder,spd,adb):
    m=validate_bundle(folder)
    if not m.get('hardware_ready'):raise ValueError('BLOCKED: '+str(m.get('blocking_reason')))
    # Verify original tool/dependencies before any hardware interaction.
    spd_exe=preflight_spd(spd)
    values={}
    for prop in ['ro.product.model','ro.build.version.incremental','ro.boot.slot_suffix','ro.boot.flash.locked']:
        p=subprocess.run([adb,'shell','getprop',prop],capture_output=True,text=True,timeout=15,check=True)
        values[prop]=p.stdout.strip()
    if values['ro.product.model']!='TB328FU' or 'S200162' not in values['ro.build.version.incremental'] or values['ro.boot.slot_suffix']!='_a' or values['ro.boot.flash.locked']!='1':
        raise ValueError('Device identity/state differs: '+str(values))
    print('EXPERIMENTAL: cboot will attempt a persistent lock-record write. ALL USER DATA MAY BECOME INACCESSIBLE.')
    if input('After personal backup, type AUTORISER V9 PERTE DONNEES: ')!='AUTORISER V9 PERTE DONNEES':raise ValueError('Cancelled')
    print('Power off fully and disconnect. Then enter the known physical BootROM key combination when waiting.')
    input('Press Enter to start waiting for BootROM: ')
    log=Path(folder)/('hardware-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'.log')
    print('Live spd_dump output follows; wait for Waiting for dl_diag before connecting USB.')
    code=run_streamed(command(folder,spd_exe),cwd=spd_exe.parent,logfile=log,timeout=240)
    print('Transport exit:',code,'Log:',log)
    print('NO SUCCESS CLAIM. Check stock Android lock state and a fresh miscdata read. No automatic wipe/reset.')
    return code

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='action',required=True)
    p=sub.add_parser('audit');p.add_argument('file',type=Path)
    p=sub.add_parser('record');p.add_argument('before',type=Path);p.add_argument('after',type=Path);p.add_argument('--output',type=Path)
    p=sub.add_parser('build');p.add_argument('--backup',required=True,type=Path);p.add_argument('--assets',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--reference-tos',type=Path)
    p=sub.add_parser('capture');p.add_argument('--assets',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--spd',required=True,type=Path);p.add_argument('--execute',action='store_true')
    for name in ['plan','run']:
        p=sub.add_parser(name);p.add_argument('--bundle',required=True,type=Path);p.add_argument('--spd',required=True,type=Path)
        if name=='run':p.add_argument('--execute',action='store_true');p.add_argument('--adb',default='adb')
    a=ap.parse_args(argv)
    try:
        if a.action=='record':
            result=record_diff(a.before,a.after)
            if a.output:
                if a.output.resolve() in (a.before.resolve(),a.after.resolve()):raise ValueError('Refusing to overwrite input')
                savejson(a.output,result)
            print(json.dumps(result,indent=2));return 0
        if a.action=='audit':
            b=read(a.file)
            result=dict(size=len(b),sha256=sha(b),all_zero=not any(b),image=None if not any(b) else parse_image(b,False))
            print(json.dumps(result,indent=2));return 1 if not any(b) else 0
        if a.action=='build':
            print(json.dumps(build(a.backup,a.assets,a.output,a.reference_tos),indent=2));return 0
        if a.action=='capture':return capture(a.assets,a.output,a.spd,a.execute)
        m=validate_bundle(a.bundle)
        print('STATUS:',m['status'],'input completeness:',m['hardware_ready'])
        print(subprocess.list2cmdline(command(a.bundle,a.spd)))
        if a.action=='run' and a.execute:return execute_hardware(a.bundle,a.spd,a.adb)
        print('OFFLINE PLAN ONLY; no process/device invoked.');return 0
    except (OSError,ValueError,KeyError,struct.error,subprocess.SubprocessError) as exc:
        print('STOP: '+str(exc),file=sys.stderr);return 2

if __name__=='__main__':sys.exit(main())
