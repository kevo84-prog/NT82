# Book 1A plan hashes after E26 / E25 (plan-v2.4-book1a-v1.3, weekly-dd-v1.1; Nov 4, 2026)

Code: commit e9813f4. Every plan header names the builder version, so every plan's sha256 changed; every sidecar
gains weekly_dd.status. 'text change' compares the plan text without that header line. The previous table
(plan v1.2) is in git history (`plan_hashes_2026-11-04.md` at commit 0070f95).

| folder | day | plan .txt sha256 | sidecar .json sha256 | weekly_dd status | plan .txt sha256 before (v1.2) | text change besides the header |
|---|---|---|---|---|---|---|
| plans_phase1 | 2025-10-22 | 37f0cb2a6e3325878bebfbc6ef9448504eb909e52b5d63ff6f031fcba23b75eb | a22c61fc36488f2be3fc35f7566bc6cf6898462cd85ed25df1be37a8bab2660a | AVAILABLE | 343074f781e6d018ff5d0ed926ce84406a1c5357d97f4f77959063ca43956c01 | none |
| plans_phase1 | 2025-10-23 | 3cdd9bcaf6a84b15dc3b04339ab0d18152f5f73d30f576d079884104ce567065 | da2f62f44f2cdd95073a87b6034c548f9ad99052e48e8be70c28a050094c34da | AVAILABLE | 013ffcac0fca8fb64f967a45ce12d168e6848cd5cde326afb0a51c8fec6b77b4 | none |
| plans_phase1 | 2025-10-24 | e10595f351e18b9b6b95f5fe895fc38a7982a46548742b3d77107a1b68698e3f | 8866735c8c750ae9a2240aac4f12cb6746e1dec721bdb65f80369a6f81a17ae9 | AVAILABLE | b5365b5c53ed950c010965add70a9f824e1569212a5dbc21c5d99d9bdac3c973 | none |
| plans_phase1 | 2025-10-27 | 572c670d71bce0e99e475331f8a1a990785dd02165e13e4bc756cf20ce3dc161 | 0ae565b467609c295790755230d34ce63d3742534104d6347e31c64c23c748e0 | AVAILABLE | 493dc74ddadef117e8aa0208dc00464e11f1cac7fd3f2cad11b22cf741b118ce | none |
| plans_phase1 | 2025-10-28 | 233bb4af49e8881026385b6514dce95c506160b8c87e2b300329ba5f59aca481 | 16a63bcd1ecff01c8f3c04a595021835cfd1eb7a52cff79f0fe2abf224333240 | AVAILABLE | abb86950ddf6031d89096a125651625ba5d8eaa4aaa114dd15f5b83f9349beae | none |
| plans_phase1 | 2025-10-29 | fd7c967457867fa657f1cb699ab5a06aba9f62970be266d60ace7dc014c6f5dd | fd4bbffa3c85089a308ec24cc25f6dbbc268298fa0b2685a695a496ee99adc76 | AVAILABLE | 42ad6bbecb3bce37261b5c0f58b2cc23e63ae58faafa17c1b59789c0c2d52ddd | none |
| plans_phase1 | 2025-10-30 | f9ebbb522f406bedf0b4bfe1640b614896c3aa2ee51084673442c2d7c4e41663 | 5268ebeb8cf61b4d103d86680f5f4bc120b615991dac62a50ae91417a26f3473 | AVAILABLE | 659856a82ab50157a22c3dc59a37e34b02c6d7d18fa70a02e361d5e2f12e7a56 | none |
| plans_phase1 | 2025-10-31 | fd31a0b77f8297bfd67b70fa0baf1a92fad20b22d18e57918cd00050173cca34 | fed6211aacdc4ee0ea4f0728a2eb8609dac7cfbe8d44a85c8bfe9d9ce27bdcb6 | AVAILABLE | 9f97774a7dd5af10bf7d68852a897f1588e41fe653488adaaf191fb9404fd116 | none |
| plans_phase1 | 2025-11-03 | 9ba6343f7261b1d3c8d87c5f4b89e2eaeafb27f83ee5daa23cc6310d17f06e9e | 1fc18299efe3cd092897b06789385d6b612e6af0e2ace6d20356b7a8661f5624 | AVAILABLE | d616c7bda2cd375223478e1aee8634cd1c85a9ac4b642497d7bbf1a8b07cfcdb | none |
| plans_phase1 | 2025-11-04 | a59f699dcd8b51c05c38868d99d8b1892c2b59ac2be8be86922dc60a1b653ccc | 007ec553e77e8526ed1d6dc35fc4cd93a494a5214b3d7363d1a2be17c3a9e85d | AVAILABLE | 687c8466189ace70b0f969ee18434e810dc1974f74d3c466cd9159366a846e1a | none |
| hand_checks | 2025-10-22 | 37f0cb2a6e3325878bebfbc6ef9448504eb909e52b5d63ff6f031fcba23b75eb | a22c61fc36488f2be3fc35f7566bc6cf6898462cd85ed25df1be37a8bab2660a | AVAILABLE | 343074f781e6d018ff5d0ed926ce84406a1c5357d97f4f77959063ca43956c01 | none |
| hand_checks | 2025-10-28 | 233bb4af49e8881026385b6514dce95c506160b8c87e2b300329ba5f59aca481 | 16a63bcd1ecff01c8f3c04a595021835cfd1eb7a52cff79f0fe2abf224333240 | AVAILABLE | abb86950ddf6031d89096a125651625ba5d8eaa4aaa114dd15f5b83f9349beae | none |
| hand_checks | 2025-10-31 | fd31a0b77f8297bfd67b70fa0baf1a92fad20b22d18e57918cd00050173cca34 | fed6211aacdc4ee0ea4f0728a2eb8609dac7cfbe8d44a85c8bfe9d9ce27bdcb6 | AVAILABLE | 9f97774a7dd5af10bf7d68852a897f1588e41fe653488adaaf191fb9404fd116 | none |
| hand_checks | 2025-11-04 | a59f699dcd8b51c05c38868d99d8b1892c2b59ac2be8be86922dc60a1b653ccc | 007ec553e77e8526ed1d6dc35fc4cd93a494a5214b3d7363d1a2be17c3a9e85d | AVAILABLE | 687c8466189ace70b0f969ee18434e810dc1974f74d3c466cd9159366a846e1a | none |
| hand_check_pack/plans | 2025-11-17 | c1a3f9d1e8268bd8fd22ea58ebd4fa3fddc1a17026af4b50a59ba7e02f3a6dd8 | 92623d2dd483a145177b50bc0f73a12f6845b141f3cdd257ff2a09668d1d6934 | AVAILABLE | fb458193a0103f03331100934db12a6433e4a5085024b7f7cc424469f762d290 | none |
| hand_check_pack/plans | 2025-11-18 | 2b590e4e85be4280f015a9bfb9966b5bd7b5afd6592ef87ada075051e15daeb2 | 5f6fffed2a1e8caedcc5d7aa9dc7b5f1da1913b2a9784b250acb251a0b5b2567 | AVAILABLE | ab04977397b5541f1e34dce0147b238ba14538f594ddaa7f86ae991ea6630953 | none |
| hand_check_pack/plans | 2025-11-19 | 254f2b64246313776b34d1c66578212794fd88a375f7e147a003d8a0f284dbba | 985af3a57480bb10d09d4eaedca14d8a387ff227f3d6b3f436d1db4ace4665b9 | AVAILABLE | c3f962fc46fb40d15fda71a5824353d9706ebc3b79943f7c14b1c14ae3ea54dc | none |

R4 rows checked against these files (P0.12 ledger + P0.11 candidates): 2070 rows, 0 with a wrong plan version or sha256.
