#!/usr/bin/env python3
"""Offline Android Boot v3/v4 sanity check: same kernel, modified ramdisk. NO device operations."""
import argparse,hashlib,struct,sys
from pathlib import Path

def desc(path):
    p=Path(path)
    b=p.read_bytes()
    if b[:8]!=b'ANDROID!' or len(b)<4096:
        raise ValueError(f'{p}: not an Android boot image')
    kernel_size,ramdisk_size=struct.unpack_from('<II',b,8)
    header_version=struct.unpack_from('<I',b,40)[0]
    if header_version not in (3,4):raise ValueError(f'{p}: unexpected header v{header_version}')
    offset=4096; k_end=offset+kernel_size
    r_start=(k_end+4095)//4096*4096;r_end=r_start+ramdisk_size
    if not kernel_size or not ramdisk_size or r_end>len(b):raise ValueError(f'{p}: missing or invalid kernel/ramdisk')
    return dict(file=str(p),size=len(b),sha256=hashlib.sha256(b).hexdigest(),kernel_size=kernel_size,
      ramdisk_size=ramdisk_size,header_version=header_version,
      kernel_sha256=hashlib.sha256(b[offset:k_end]).hexdigest(),
      ramdisk_sha256=hashlib.sha256(b[r_start:r_end]).hexdigest())

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--stock',required=True)
    ap.add_argument('--patched',required=True)
    a=ap.parse_args()
    try:s=desc(a.stock);p=desc(a.patched)
    except (OSError,ValueError) as e:print('STOP:',e);return 2
    print('STOCK:',s);print('PATCHED:',p)
    ok=(s['size']==p['size'] and s['header_version']==p['header_version'] and
      s['kernel_sha256']==p['kernel_sha256'] and s['ramdisk_sha256']!=p['ramdisk_sha256'])
    print('OFFLINE STRUCTURE CHECK:', 'PASS' if ok else 'FAIL — DO NOT FLASH')
    print('NOTE: a valid structure cannot guarantee successful boot.')
    return 0 if ok else 2
if __name__=='__main__':sys.exit(main())
