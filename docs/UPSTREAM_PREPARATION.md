<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Combined upstream contribution

The submission is prepared as **one upstream PR containing the complete feature
list**, from `fgunited/Felucca-PR:upstream/fx-edge-editing` to
`hugelton/Felucca:main`. No separate feature PRs have been opened.
The existing [integration draft](https://github.com/fgunited/Felucca-PR/pull/1)
is internal to this fork. An official upstream PR has not yet been opened.

The earlier cumulative branches (live-parts, step-rec, fx-automation,
sequence-duplicate and fx-edge-editing) are preparation checkpoints. They are
not a submission series. Project INIT belongs to this combined contribution.

## Complete feature list

- Live A–D launches at track 1's loop boundary, retaining sounds, tempo and clock.
- Save parts during playback/recording as RAM snapshots, committed after STOP.
- STEP REC at an independent cursor during playback, switching to LIVE REC.
- Capture/replay all fourteen FX specials with fine press/release timing, latch and cross-loop holds.
- Project-level global FX TRACK T1–T4.
- Independent FX ON/OFF step and fine-position editing for start and duration.
- Delete one chronological FX pair: ON + next OFF, or OFF + previous ON; one undo restores both.
- DUP x2 for steps, parameter locks and automation, up to 64 steps, with a clean playback transition.
- Project INIT without rebooting.

README uses Unreleased; firmware retains upstream v1.5.1. The maintainer chooses
a release number. Fork branding, release/Pages workflows and CI-only validation
files are excluded from the feature diff. User guides are under docs/.
Credit remains in README > Credits > Contributions as
[bonszaimusic](https://www.youtube.com/@bonszaimusic) /
[fgunited](https://github.com/fgunited).

## Submission and review

[CONTRIBUTING](https://github.com/hugelton/Felucca/blob/main/CONTRIBUTING.md)
and [discussion #60](https://github.com/hugelton/Felucca/discussions/60) welcome
AI-assisted contributions with explanation, tests and real FM-1 validation.
Development used AI-assisted coding. The maintainer recommends focused changes;
the author chooses one combined contribution for this coordinated live workflow.

1. Validate the combined branch and record the remaining FM-1 checks below.
2. Open one upstream draft PR using the complete integration description.
3. Mark it ready when hardware testing is documented.
4. Post the optional [Show and tell draft](SHOW_AND_TELL_DRAFT.md) only if requested.
5. Keep this preparation-notes branch and `validation/upstream` outside the PR.

## Exact-revision validation

Latest feature commit: `b192936ff5ce1c30f2dedf2b010d4cacd40a2186`.
Validation workflows explicitly check out that source; workflow files live only
on `validation/upstream`.

- [Full firmware build and tests/run_tests.sh](https://github.com/fgunited/Felucca-PR/actions/runs/38153066247): passed, including the target build, full host suite, ASan/UBSan/fuzz tests, UI layouts and target budgets.
- [WebAssembly build and tests](https://github.com/fgunited/Felucca-PR/actions/runs/38153066252): passed.
- Local FX editing/deletion, FX recording, UI, DUP x2, persistence, motion and project tests: passed.
- Local ASan/UBSan FX tests: passed with LeakSanitizer disabled because /proc task data is inaccessible in this workspace. CI uses the normal sanitizer suite.
- Firmware artifact: `felucca-pr-b192936ff5ce` (967004-byte zip).
- Emulator artifact: `felucca-pr-emulator-b192936ff5ce` (402067-byte zip).
- Earlier source `a1216c8a6c3d36e99edf6e42a93f5f0fef4e5226` passed the full firmware and WebAssembly suites; it did not include selective deletion.

Selective deletion chooses chronological neighbours in the active loop, including
fine phase and wraparound, rather than original take identity. For ON 3, ON 5,
OFF 7, deleting OFF 7 removes ON 5 and leaves ON 3. Rows outside LEN are deleted
alone. Unfinished captures block edits on their track before undo is replaced.

## Hardware checks to document

The user reports testing Bonszai 5 on the FM-1. Bonszai 6 testing found the old
whole-effect deletion behavior; the latest change replaces it with selective
pair deletion and still needs hardware testing.

- Multiple takes of one FX: delete ON and OFF; verify other takes remain and one undo restores both.
- Same-step fine positions, loop-crossing pairs, repeated ON and orphan edges.
- Edit/delete during playback; verify timing, manual hold/latch, notes and external USB/TRS clock.
- Save A–D during playback, launch at the boundary, STOP and verify persistence after restart.
- STEP REC chords, mode switching/disarm, DUP x2 on melodic/drum/odd-length patterns.
- Project INIT with USB MIDI connected, including cancel and confirm.

Bonszai 7 was published after explicit authorization on 11 October 2026.
The immutable tag `1.5.1-bonszai-7` identifies main commit
`2103e6fb669267fb4f2ea0901042a90313ee6f46`.

- [Full main firmware checks](https://github.com/fgunited/Felucca/actions/runs/38154194629): passed.
- [Main emulator build/tests](https://github.com/fgunited/Felucca/actions/runs/38154194625): passed.
- [Release and Pages deployment](https://github.com/fgunited/Felucca/actions/runs/38154194622): passed.
- [Bonszai 7 release](https://github.com/fgunited/Felucca/releases/tag/1.5.1-bonszai-7).
- [USB installer](https://fgunited.github.io/Felucca/webapp/installer/) and
  [emulator](https://fgunited.github.io/Felucca/webapp/try/) were checked live:
  both identify Bonszai 7 and link the published source commit.
- The public installer firmware's SHA-256 matches the release asset:
  `2021a98294ddb36f8a191cd8fd5985c7f2a4bf6dfedae110f84d3d9e6efeac0f`.

The neutral upstream feature branch remains unchanged and contains the same
FX code/tests. Hardware validation of the new editing/deletion is still pending;
the single upstream contribution remains prepared as an internal draft.
No official upstream PR or 1.5.2 release is claimed.
