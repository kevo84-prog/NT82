# Book 1A Phase 3 deliverables sha256 (Nov 9, 2026)

Raw bytes on disk (the .md files are LF, as committed). Ledgers, attempts, stress ledgers, diagnostics and review files: Phase3_report.md section 9.

| file | bytes | sha256 |
|---|---|---|
| Phase3_report.md | 133405 | af3fdf3925d2489be446e09b409ae02532db4f7991c37eecb0d1ec7bf9b9bc16 |
| Phase3_change_list.md (unchanged) | 6188 | ff1e336ed695abc3f4b2102dc1d1ad504ad0ea18b09966ce54e6a02f761209aa |
| checker_input/Phase3_G4_checker_pack.zip | 144574 | d5235a1f55799448cc814d9f3c1392ddde5101c4b9cec7f6021bef63e4ead333 |
| checker_input/pack_manifest.json | 7394 | b669d8d06318635f3d3dae45b05c35d7dcfded0155b9851a0dadbf8453e94bf8 |
| checker_input/g4_sample.csv | 1649 | ee0aa154ad87ae28a81b2cc2ac957930ad149837434f02efee0314a2db19ddfa |
| runs/phase3_review/phase3_review.csv | 148911 | 1820a32a6cc142a2dee4d28962bd900d6147356a857ff1d21df506aaf7dc94bd |
| runs/phase3_compare/phase3_compare.json | 6856 | f318bbaae048f3467ed90f4b34931b72a6c3a026f480fd5ac9bf00f1f43f3492 |

## Report build files (added Nov 9, 2026)

Unchanged copies of `book1a/Phase3/runs/report_build/` (the git-ignored originals stay there), committed under
`Book1A/Phase3/report_build/`. `build_g4_pack.py` was written for its original place (`runs/report_build/`); it is
kept byte for byte, not edited. `tables.md` has CRLF line ends; `report_build/.gitattributes` (`* -text`, 8 bytes,
sha256 705fd4d6451a31d36b3df7de96f83f30ac976c9b4a6d1e51671d8e2f33e2d0da) keeps git from changing them, so the
committed bytes equal the hashes below.

| file | bytes | sha256 |
|---|---|---|
| report_build/build_phase3_report_md.py | 18369 | 1d850120b5a8e71bf54e4992aab6a10bded5c150d2e19776d9b074e6a450e0a4 |
| report_build/build_g4_pack.py | 3870 | b9314a746b690eb415477bdec96457bf861c755d8f93d09d55f7aa801a7b8acb |
| report_build/head.md | 8345 | 1fb340aaefc5ccfa19dafa7e61e69a7b10ae0f18b73c89a6de436f952932da73 |
| report_build/parts.md | 12556 | 2d0fe069833fe8085a3cf0e816eb533c153849c65183900af086c352ec74e389 |
| report_build/tables.md | 113398 | 4c6bdd4b85dd792e22e23966e582682b937ca88b7408ccf2d0c1bc45a714a7f9 |

## Diagnostics folders (book1a/Phase3/runs/)

- `phase3_diag_17ac9cd`: the registered diagnostics output (diag_phase1b at 17ac9cd, exit 0).
- `phase3_diag_partial_stopped_20261109`: the stopped first run at 8107c0f (exit 1), renamed and kept; not used.

## mj_alignment

The mj_alignment mapping in `build_phase3_report_md.py` is descriptive only and uses the registered grouping unchanged
(`Phase3_registration.md` line 74).
