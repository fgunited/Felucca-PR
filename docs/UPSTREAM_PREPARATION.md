<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Combined upstream contribution

The complete feature set has been submitted as **one official upstream PR**:
[**hugelton/Felucca #234 — Add live parts, playback step recording and editable FX automation**](https://github.com/hugelton/Felucca/pull/234).

Opened on 11 October 2026 after explicit submission authorization and a successful
FM-1 hardware-test report. The PR is open and ready for review, with maintainers
allowed to edit the feature branch. It targets `hugelton/Felucca:main` from
`fgunited/Felucca-PR:upstream/fx-edge-editing`. No separate feature PRs were opened.
The [internal preparation draft](https://github.com/fgunited/Felucca-PR/pull/1)
is closed and links to the official PR.

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
files are excluded from the feature diff. Feature instructions are included in
the existing README; docs/ retains only the upstream image files.
Credit remains in README > Credits > Contributions as
[bonszaimusic](https://www.youtube.com/@bonszaimusic) /
[fgunited](https://github.com/fgunited).

## Submission and review

[CONTRIBUTING](https://github.com/hugelton/Felucca/blob/main/CONTRIBUTING.md)
and [discussion #60](https://github.com/hugelton/Felucca/discussions/60) welcome
AI-assisted contributions with explanation, tests and real FM-1 validation.
Development used AI-assisted coding. The maintainer recommends focused changes;
the author chooses one combined contribution for this coordinated live workflow.

1. Automated validation and the author's FM-1 hardware test are complete.
2. Official combined PR [#234](https://github.com/hugelton/Felucca/pull/234) is submitted and ready for review.
3. Use the recorded checks and hardware report for review.
4. Post the optional [Show and tell draft](SHOW_AND_TELL_DRAFT.md) only if requested.
5. Keep this preparation-notes branch and `validation/upstream` outside the PR.

## Exact-revision validation

Latest feature commit: `c821902e9b5210b6f5bb0a6a1ea694a9aa53cc60`.
The latest follow-up changes documentation only. Validation workflows explicitly
check out tested firmware commit `b192936ff5ce1c30f2dedf2b010d4cacd40a2186`;
workflow files live only on `validation/upstream`. Firmware, tests, web and build
sources are unchanged from that validated revision.

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

## Hardware validation

On 11 October 2026 at 18:25 Europe/Berlin, the author reported
**"Funktioniert alles"** after installing/testing the published Bonszai 7 build
on the FM-1. This completes the requested hardware-testing gate.
Bonszai 5 had previously been reported as tested; Bonszai 6 testing led to the
selective-deletion change now included in Bonszai 7.

This records the author's overall success report. No separate measurements or
individual checklist results are inferred. Automated regression cases cover
multiple takes of one FX, both deletion directions, fine timing, loop boundaries,
repeated/orphan edges, undo/redo, capture guards and live playback state.

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
FX code/tests. The author has reported successful hardware validation of the new build.
The single combined upstream contribution is submitted as PR #234; the internal
draft is closed. The official PR head is `c821902e9b5210b6f5bb0a6a1ea694a9aa53cc60`.
No official 1.5.2 release is claimed; release versioning remains the maintainer's decision.

## Documentation layout

The three added standalone guides were removed from the feature branch on
11 October 2026 to follow upstream's existing structure. README retains all
nine feature descriptions, usage gestures and key FX compatibility/deletion
semantics. No guide links remain. The PR diff contains 34 files; the final
follow-up changes only README and removes the three guides.
