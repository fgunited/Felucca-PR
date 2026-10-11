<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Upstream preparation

This branch contains preparation notes only. Feature branches remain based on
hugelton/Felucca main at `ef1f561b6b105f20350f6b1eac0dc0789a357f00`.
They are a cumulative stack, not five independent PRs against main.

| Stage | Branch | Base for reviewing this stage |
| --- | --- | --- |
| Live launches and RAM saves | [upstream/live-parts](https://github.com/fgunited/Felucca-PR/tree/upstream/live-parts) | main |
| STEP REC during playback | [upstream/step-rec](https://github.com/fgunited/Felucca-PR/tree/upstream/step-rec) | upstream/live-parts |
| FX recording, owner track and project controls | [upstream/fx-automation](https://github.com/fgunited/Felucca-PR/tree/upstream/fx-automation) | upstream/step-rec |
| DUP x2 | [upstream/sequence-duplicate](https://github.com/fgunited/Felucca-PR/tree/upstream/sequence-duplicate) | upstream/fx-automation |
| Independent FX edge editing | [upstream/fx-edge-editing](https://github.com/fgunited/Felucca-PR/tree/upstream/fx-edge-editing) | upstream/sequence-duplicate |

The last branch is the complete integration reference. Its diff contains five
feature commits, 37 files, firmware changes, tests and user documentation.
It excludes fork release/Pages workflows and build-tool changes. The firmware
version remains upstream's v1.5.1; the maintainer chooses any release version.
README uses an Unreleased section. Detailed guides live in docs/.

Credit remains in README > Credits > Contributions as
[bonszaimusic](https://www.youtube.com/@bonszaimusic) /
[fgunited](https://github.com/fgunited), naming the contributed features.

## Submission approach

[CONTRIBUTING](https://github.com/hugelton/Felucca/blob/main/CONTRIBUTING.md)
and [Discussion #60](https://github.com/hugelton/Felucca/discussions/60)
welcome AI-assisted contributions, provided they are focused, understood,
tested on a real FM-1, and checked with tests/run_tests.sh.
[Show and tell](https://github.com/hugelton/Felucca/discussions/categories/show-and-tell)
is the recommended place to introduce forks, mods and demos.
[Discussion #230](https://github.com/hugelton/Felucca/discussions/230)
explains the maintainer's reduced pace of feature development.

1. Review the integration draft in this fork.
2. Complete and record the remaining hardware checks below.
3. Post the prepared Show and tell text if desired, asking which changes fit mainline.
4. Start with the live-parts PR. Submit further changes separately after agreeing scope.
   The FX stage currently also contains project INIT: isolate INIT into its own
   focused PR before sending that stage upstream. These are preparation branches,
   not a promise to submit the combined integration diff.
5. Rebase each accepted next stage on the actual updated upstream main.
   Do not merge this preparation-notes branch into a feature PR.

## Validation evidence

On 11 October 2026, 22 host test invocations passed on the five prepared source
stages, built with regenerated headers and the real repository sample assets:

- live parts: live_pattern_test, persistence_test, ui_test;
- STEP REC: live_pattern_test, step_play_test, ui_test;
- FX controls: fx_motion_test, editor_test, persistence_test, ui_test;
- DUP x2: duplicate_test, ui_test;
- complete integration: live_pattern_test, step_play_test, fx_motion_test,
  duplicate_test, fx_edit_test, motion_test, project_test, persistence_test,
  editor_test, ui_test.

The final firmware/test/emulator sources match the previously tested Bonszai 6
implementation except the version string, branding comments and trailing blank
lines. Its earlier complete GitHub firmware checks, sanitizers, WebAssembly
tests and target budget checks passed on
[1705498](https://github.com/fgunited/Felucca/commit/1705498662d426d8fb5663e334d7250ef1215461).
This is previous-implementation evidence, not a claim that the complete target
build or tests/run_tests.sh ran on this new fork. The exact prepared commit was subsequently validated successfully as recorded below.

New C test files carry GPL-3.0-only SPDX headers; new guide files use the same
identifier in an HTML comment.

## Exact PR validation completed

Both validation workflows completed successfully on 11 October 2026.
They live only on `validation/upstream` and explicitly check out the feature
commit `a1216c8a6c3d36e99edf6e42a93f5f0fef4e5226`.

- [Firmware build and complete tests/run_tests.sh](https://github.com/fgunited/Felucca-PR/actions/runs/38150874011):
  installable package built, ALL HOST TESTS PASSED, sanitizers/fuzz tests,
  UI renders, regressions and target budgets passed.
- [WebAssembly emulator build and tests](https://github.com/fgunited/Felucca-PR/actions/runs/38150873998):
  all host feature checks and emulator tests passed.
- Firmware artifact: `felucca-pr-a1216c8a6c3d` (966485-byte zip).
- Emulator artifact: `felucca-pr-emulator-a1216c8a6c3d` (401837-byte zip).

The PR branch and its diff retain no workflow files.
The user reports having tested Bonszai 5 on the FM-1; Bonszai 6 testing is
in progress. One observation confirms the documented current behavior:
EDIT on an FX row deletes every ON/OFF event for that effect on the selected
track. A more selective deletion action would be a separate change; it is
not included in this tested commit.

## Hardware checks still to document

- Save A–D during playback, launch them at track 1's boundary, then STOP and
  confirm the flash commits survive a restart.
- Enter chords with STEP REC while playback continues; switch to LIVE REC and disarm.
- Record short FX taps, latch and loop-crossing holds on the configured FX track,
  then change tracks, replay, move ON/OFF edges and test undo.
- Test DUP x2 on melodic/drum tracks, odd lengths and a running loop.
- Test project INIT while USB MIDI is connected, including cancel and confirm.
- Check external USB/TRS clock, audible timing, stuck notes/FX and playback continuity.

No final hardware validation or official 1.5.2 release is claimed.
