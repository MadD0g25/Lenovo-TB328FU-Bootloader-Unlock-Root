#!/usr/bin/env python3
"""Read-only self-tests of documented SHA-256s, source presence and intended safety stops."""
from pathlib import Path
import importlib.util,sys,unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('verifier',ROOT/'tools/verify/verify_package.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class RepoTests(unittest.TestCase):
 def test_hash_count(self):self.assertEqual(len(v.EXPECTED),5)
 def test_v9_source_present(self):self.assertTrue((ROOT/'tools/v9/sources/tb328fu_v9.py').is_file())
 def test_docs(self):
  for n in ['README.md','README.fr.md','docs/en/UNLOCK.md','docs/fr/DEVERROUILLAGE.md','docs/en/ROOT.md','docs/fr/ROOT.md']:
   self.assertTrue((ROOT/n).is_file(),n)
 def test_original_runner_blocks_other_firmware(self):
  src=(ROOT/'tools/v9/sources/tb328fu_v9.py').read_text(encoding='utf-8')
  self.assertIn("values['ro.product.model']!='TB328FU'",src)
  self.assertIn("values['ro.boot.slot_suffix']!='_a'",src)
  self.assertIn("'ro.boot.flash.locked'",src)
 def test_no_auto_erase_in_runner_command(self):
  spec=importlib.util.spec_from_file_location('v9',ROOT/'tools/v9/sources/tb328fu_v9.py')
  mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
  c=mod.command(ROOT/'local/V9/prepared_current',ROOT/'local/spd_dump/spd_dump.exe')
  self.assertEqual(c.count('fdl'),5)
  for prohibited in ('write_part','erase_part','w_force','reset'):self.assertNotIn(prohibited,c)
if __name__=='__main__':unittest.main()
