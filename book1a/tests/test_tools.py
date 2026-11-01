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
