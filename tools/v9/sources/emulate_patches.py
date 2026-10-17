#!/usr/bin/env python3
"""Emulate only V9 glue instructions. No SoC/TEE/USB emulation or unlock proof."""
import json
from pathlib import Path
import struct
from tb328fu_v9 import patch_fdl1,patch_uboot,read,HEADER_BASE,HOOK,CAVE,SETTER,word,branch_target

def run(reference):
    from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
    from unicorn.arm64_const import UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X19,UC_ARM64_REG_X20,UC_ARM64_REG_X29,UC_ARM64_REG_X30,UC_ARM64_REG_SP,UC_ARM64_REG_PC
    r=Path(reference);results={}
    for n,b in [('V7',read(r/'fdl1-boot-S200162-RAM-EXPERIMENTAL.bin')),('V9',patch_fdl1(read(r/'fdl1-dl.bin')))]:
        u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(0,0x20000);u.mem_write(0x5500,b)
        u.mem_map(0x200000,0x2000);u.mem_map(0x94000000,0x1000)
        u.reg_write(UC_ARM64_REG_X0,0x5500);u.reg_write(UC_ARM64_REG_X1,0x93fffe00)
        u.reg_write(UC_ARM64_REG_X19,0x93fffe00);u.reg_write(UC_ARM64_REG_X29,0x200100)
        u.reg_write(UC_ARM64_REG_SP,0x200100)
        seen=[]
        def hook(uc,addr,size,user):
            if addr==0x94000000:
                seen.append(dict(entry=hex(addr),x0=hex(uc.reg_read(UC_ARM64_REG_X0)),x1=hex(uc.reg_read(UC_ARM64_REG_X1))))
                uc.emu_stop()
        u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x5500+0xac08,0,count=30)
        if not seen:raise AssertionError('SML entry not reached in '+n)
        results[n]=seen[0]
    assert results['V9']['x0']=='0x94060000' and results['V9']['x1']=='0x94040000'
    assert results['V7']['x0']=='0x5500' and results['V7']['x1']=='0x93fffe00'
    b=patch_uboot(read(r/'uboot_a.bin'));u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(0x9efff000,0x200000);u.mem_write(HEADER_BASE,b)
    u.mem_map(0x200000,0x2000);u.reg_write(UC_ARM64_REG_SP,0x200100)
    u.mem_write(0x200100,struct.pack('<6Q',0x1111,0x2222,0x3333,0x4444,0,0))
    original=branch_target(CAVE,word(b,CAVE));exit_off=branch_target(CAVE+24,word(b,CAVE+24));seen=[]
    def trace(uc,addr,size,user):
        off=addr-HEADER_BASE
        if off in (original,SETTER):
            seen.append(dict(call=hex(off),x0=hex(uc.reg_read(UC_ARM64_REG_X0))))
            # STUBBED external functions. Not the real TEE or U-Boot functions.
            uc.reg_write(UC_ARM64_REG_X0,0)
            uc.reg_write(UC_ARM64_REG_PC,uc.reg_read(UC_ARM64_REG_X30))
        elif off==exit_off:uc.emu_stop()
    u.hook_add(UC_HOOK_CODE,trace);u.emu_start(HEADER_BASE+HOOK,0,count=40)
    assert seen[-1]==dict(call=hex(SETTER),x0='0x1')
    assert u.reg_read(UC_ARM64_REG_SP)==0x200130
    assert u.reg_read(UC_ARM64_REG_X19)==0x3333 and u.reg_read(UC_ARM64_REG_X20)==0x4444
    assert u.reg_read(UC_ARM64_REG_PC)==HEADER_BASE+exit_off
    results['cboot_glue']=dict(stubbed_calls=seen,continuation=hex(exit_off),stack_restored=True,
        final_x0=hex(u.reg_read(UC_ARM64_REG_X0)))
    results['limitations']='External calls stubbed. No SML/TrustOS execution, no signature acceptance or device success proven.'
    return results

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('reference',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args();result=run(a.reference);text=json.dumps(result,indent=2)
    print(text)
    if a.output:a.output.write_text(text+'\n',encoding='utf-8')
