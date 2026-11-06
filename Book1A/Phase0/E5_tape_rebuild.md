# E5: Book 1's tapes kept; two days rebuilt from raw to confirm them (Nov 4, 2026)

Kyron, Nov 4: keep Book 1's tapes. Rebuild Nov 5 and Dec 15, 2025 from raw with the original `mbo_tape` settings,
confirm the raw files and settings match Book 1's, compare sha256, and if they differ compare the records.

## Raw files (same as Book 1 used)

| tape | raw file Book 1 used | how we know | bytes | sha256 (now) | sha256 in the Phase 0 manifest (P0.2) |
|---|---|---|---|---|---|
| `tape_20251105` | `raw\block1\nq_mbo_20251021_20260421\GLBX-20261022-JHKARNQBGK\glbx-mdp3-20251105.mbo.dbn.zst` | the only Nov 5 MBO file; continuous NQ.v.0 (CLAUDE.md "Build more with ... --day"); front id 158704 | 351,604,367 | 3de3199c...a3423 | 3de3199c...a3423 (equal) |
| `tape_20251215` | `raw\block1\nq_roll_NQH6_mbo_20251214_20251216\GLBX-20261024-RPVR3FBG76\glbx-mdp3-20251215.mbo.dbn.zst` | `backtest\phase3\build_tapes.py` (ROLL_DAYS Dec 14-16 use the NQH6 roll files) and its log line "done 2025-12-15 <- nq_roll_NQH6_mbo_20251214_20251216/..., front id 42002475, trades so far 220,612" | 308,983,258 | e78a7898...cc90f | e78a7898...cc90f (equal) |

## Settings (same as Book 1 used)
- `jeron_engine\mbo_tape.py` today = `book1_ref\jeron_engine\mbo_tape.py` (sha256 30db566a...0fc2) = the version at
  Book 1 commit 83939ac. No change since (`git diff 83939ac` empty).
- Nov 5's tape was written Oct 25, before 83939ac; the earlier version (aa0ad2f) differs only by the optional
  `end_ns` / `end_ct` cutoff, which is off for both days (no cutoff; Book 1 used one only for Feb 4, 2026).
- Call: `mbo_tape.day_tape(<raw file>, <out dir>, None)` = `build(front_only=True, header=False, time_field="ts_event")`,
  front contract = the most traded instrument id in the first chunk. databento 0.87.0 in both Pythons.
- Rebuilt into `K:\Databento_BackTesting\Book1A\e5_tapes\` (outside git; Book 1's `tapes\` untouched), with
  `Book1A\.venv` Python.

## Result

| tape | .csv.gz sha256 Book 1 | .csv.gz sha256 rebuilt | decompressed sha256 (both) | records Book 1 / rebuilt |
|---|---|---|---|---|
| `tape_20251105` | b83db8ff...1ccc | 6bed67d1...47f1 | b26e98f0...bd68 (equal) | 399,566 / 399,566 |
| `tape_20251215` | 333c7c1a...1e63 | 571c70e8...ba74 | 09a41f11...1291 (equal) | 220,612 / 220,612 |

The `.csv.gz` files differ only in the gzip wrapper (it stores the file name and write time). The decompressed tapes
are byte-identical, so every record is the same: timestamp, price, bid, ask, size, aggressor flag, and their order.
**No substantive difference.** E5 closed: Book 1A keeps Book 1's tapes.
