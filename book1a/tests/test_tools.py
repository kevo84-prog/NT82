import json
import os
import tempfile
import unittest
from pathlib import Path

from book1a import manifest, replay_diff


class TestManifest(unittest.TestCase):
    def test_build_and_compare(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "raw"; root.mkdir()
            (root / "a.dbn.zst").write_bytes(b"abc"); (root / "b.dbn.zst").write_bytes(b"xyz")
            ours = Path(d) / "ours.csv"
            self.assertEqual(manifest.build(root, ours), 2)
            ref = Path(d) / "ref.csv"
            ref.write_text("file,size_bytes,sha256\na.dbn.zst,3,ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\nc.dbn.zst,5,00\n")
            rep = Path(d) / "rep.md"
            r = manifest.compare(ours, ref, rep)
            self.assertEqual((r["missing"], r["extra"], r["differing"], r["hash_checked"]), (1, 1, 0, 1))
            self.assertIn("FAIL", rep.read_text())
            ref.write_text("file,size_bytes,sha256\na.dbn.zst,3,ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\nb.dbn.zst,3,\n")
            r = manifest.compare(ours, ref, rep)
            self.assertEqual((r["missing"], r["differing"]), (0, 0))
            self.assertIn("PASS", rep.read_text())
            ref.write_text("file,size_bytes,sha256\na.dbn.zst,4,\nb.dbn.zst,3,\n")
            self.assertEqual(manifest.compare(ours, ref, rep)["differing"], 1)
            # Book 1 gate 6 layout: relative path in 'file', size_mb rounded to 0.1
            (root / "big.dbn.zst").write_bytes(b"x" * 1_250_000)
            manifest.build(root, ours)
            ref.write_text("date,file,size_mb,session\n2025-10-22,raw\\block1\\big.dbn.zst,1.2,NORMAL\n2025-10-22,raw\\block1\\a.dbn.zst,0.0,NORMAL\n")   # round(1.25, 1) = 1.2, as data_integrity.py writes
            r = manifest.compare(ours, ref, rep)
            self.assertEqual((r["missing"], r["differing"]), (0, 0))
            ref.write_text("date,file,size_mb,session\n2025-10-22,raw\\block1\\big.dbn.zst,1.3,NORMAL\n")
            self.assertEqual(manifest.compare(ours, ref, rep)["differing"], 1)


class TestReplayDiff(unittest.TestCase):
    def test_identical_and_differing(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a", Path(d) / "b"; a.mkdir(); b.mkdir()
            (a / "ledger.csv").write_text("run_id,x,y\n1,0.1,2\n1,0.3,4\n")
            (b / "ledger.csv").write_text("run_id,x,y\n2,0.1,2\n2,0.3,4\n")
            (a / "f.json").write_text(json.dumps({"k": 1.0, "run_id": "a"})); (b / "f.json").write_text(json.dumps({"k": 1.0, "run_id": "b"}))
            self.assertEqual(replay_diff.diff_runs(a, b, ["run_id"]), {})
            self.assertNotEqual(replay_diff.diff_runs(a, b, []), {})
            (b / "ledger.csv").write_text("run_id,x,y\n2,0.1,2\n2,0.30000000000000004,4\n")
            r = replay_diff.diff_runs(a, b, ["run_id"])
            self.assertEqual(r["ledger.csv"]["status"], "VALUE_DIFF")
            self.assertEqual(r["ledger.csv"]["first"][0]["columns"], ["x"])
            (b / "extra.csv").write_text("a\n1\n")
            self.assertEqual(replay_diff.diff_runs(a, b, ["run_id"])["extra.csv"]["status"], "ONLY_IN_B")


if __name__ == "__main__":
    unittest.main()


class TestBook1RefCompare(unittest.TestCase):
    def test_match_differ_missing(self):
        from book1a import book1_ref_compare as C
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "pc"; (root / "jeron_engine").mkdir(parents=True); (root / "raw" / "sub").mkdir(parents=True)
            (root / "jeron_engine" / "fills.py").write_bytes(b"abc")            # match
            (root / "jeron_engine" / "arms.py").write_bytes(b"changed")         # differs
            (root / "raw" / "sub" / "gex_levels_block1.csv").write_bytes(b"xyz")  # found by name under --raw
            man = Path(d) / "MANIFEST.md"
            sha_abc = "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
            sha_xyz = "3608bca1e44ea6c4d268eb6db02260269892c0b42b86bbf1e77a6fa16c3c9282"
            man.write_text("| local path | Drive id | modifiedTime | bytes | sha256 |\n|---|---|---|---|---|\n"
                           f"| jeron_engine/fills.py | id1 | 2026-10-27T00:15:04.012Z | 3 | {sha_abc} |\n"
                           f"| jeron_engine/arms.py | id2 | 2026-10-26T16:07:12.825Z | 3 | {sha_abc} |\n"
                           f"| data/gex_levels_block1.csv | id3 | 2026-10-25T04:05:00.828Z | 3 | {sha_xyz} |\n"
                           f"| data/condition_NQ_MBO_2026-09.json (Drive name `condition.json`) | id4 | t | 3 | {sha_abc} |\n")
            rep = Path(d) / "rep.md"
            r = C.compare(man, root, rep, raw=root / "raw")
            self.assertEqual((r["files"], r["match"], r["differing"], r["missing"]), (4, 2, 1, 1))
            txt = rep.read_text()
            self.assertIn("FAIL", txt); self.assertIn("| jeron_engine/arms.py | **DIFFERS**", txt)
            self.assertIn("| data/condition_NQ_MBO_2026-09.json | **MISSING**", txt)
            (root / "jeron_engine" / "arms.py").write_bytes(b"abc")
            (root / "NQ_MBO_2026-09" / "GLBX-20260928-6GPK57A3YJ").mkdir(parents=True)
            (root / "NQ_MBO_2026-09" / "GLBX-20260928-6GPK57A3YJ" / "condition.json").write_bytes(b"abc")
            r = C.compare(man, root, rep, raw=root / "raw")
            self.assertEqual((r["match"], r["differing"], r["missing"]), (4, 0, 0))
            self.assertIn("PASS", rep.read_text())
