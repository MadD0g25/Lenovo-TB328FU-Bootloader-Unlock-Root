#!/usr/bin/env python3
"""Check exact tested RAM image checksums and sample stock/patched boot images, OFFLINE.
Run with --bundle local/V9/prepared_current ; never contacts an Android device.
"""
import argparse, hashlib, json, sys
from pathlib import Path
EXPECTED={
 'fdl1-boot-v9.bin': (60036,'f0b87ca029eec5ddd3cce7d654d733d182996989eb8e5c729f9748f72806964d'),
 'cboot-v9-S200162.bin':(909188,'fd2698c4f19e24840d70b6cae65f46d322918e5ba105795f306b11ad00622025'),
 'teecfg-ram.bin':(124052,'0e47a51ad7596f43597e16373817926f8f5524a0fa7557aa8feb846c8f47ec9b'),
 'trustos-ram.bin':(3489348,'29160f1f0a0e95619dc5a416daf2b2e8b5bc08037baf960cd3dafd5dc9180ed7'),
 'sml-ram.bin':(68900,'5e0e84e250ecf84dee588a58fde18054ddc8cf4da95c2404f26141868e19a5a5')}
STOCK='0d699f4ca7710f4c8f87dbc8c60b94e1621708d2bc5e474fdf0d013a25e89560'
PATCHED='5c99161ebcd93e0786421608a4dd1950a517db5e5e02229413daf9383c499cfd'
def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def check(path,size,wanted):
 if not path.is_file():print('MISSING',path);return False
 got=path.stat().st_size; hashval=digest(path)
 ok=(got==size and hashval==wanted)
 print(('PASS' if ok else 'FAIL'),path.name,'size',got,'sha256',hashval)
 return ok
def main():
 ap=argparse.ArgumentParser(description='TB328FU offline SHA-256 verifier; no USB or writing')
 ap.add_argument('--bundle',type=Path)
 ap.add_argument('--stock',type=Path)
 ap.add_argument('--patched',type=Path)
 a=ap.parse_args(); ok=True
 if not (a.bundle or a.stock or a.patched):ap.error('Provide --bundle and/or --stock and/or --patched')
 if a.bundle:
  for name,(size,h) in EXPECTED.items():ok=check(a.bundle/name,size,h) and ok
  m=a.bundle/'manifest.json'
  if m.is_file():
   try:
    data=json.loads(m.read_text(encoding='utf-8'))
    if not data.get('hardware_ready',False):print('FAIL: manifest hardware_ready is false');ok=False
    for name,(size,h) in EXPECTED.items():
     expected=data.get('files',{}).get(name,{})
     if expected.get('size')!=size or expected.get('sha256')!=h:
      print('FAIL: manifest inconsistent for',name);ok=False
   except (ValueError,OSError) as e:print('FAIL invalid manifest:',e);ok=False
  else:print('FAIL: missing manifest.json');ok=False
 if a.stock:ok=check(a.stock,67108864,STOCK) and ok
 if a.patched:ok=check(a.patched,67108864,PATCHED) and ok
 print('OFFLINE RESULT:', 'PASS' if ok else 'FAIL — STOP')
 return 0 if ok else 2
if __name__=='__main__':sys.exit(main())
