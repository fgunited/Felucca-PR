<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Show and tell draft

**Suggested title:** Live workflow extensions for Felucca: parts, step recording and FX automation

Hi Leo and everyone,

I've been extending Felucca for my live workflow as **bonszaimusic / fgunited**.
The goal is to build and vary parts while the music keeps playing.

The additions are:

- Live switching between A–D at track 1's loop boundary, keeping the current sounds and tempo.
- Saving separate parts during playback, with RAM snapshots committed automatically after STOP.
- STEP REC at an independent cursor while the sequencer continues.
- Recording the fourteen FX-special keys with their press/release timing.
- A project setting for the track that owns global FX automation.
- Independent step/fine-position editing of FX ON and OFF to change start and duration.
- DUP x2 for a track's steps, parameter locks and automation, including a clean transition during playback.
- Project INIT without rebooting.

I've prepared the code in [fgunited/Felucca-PR](https://github.com/fgunited/Felucca-PR/tree/upstream/fx-edge-editing),
based on current upstream main, with neutral Felucca versioning and documentation.
Development used AI-assisted coding. The complete firmware build/test suite and the WebAssembly build/tests pass
for the prepared commit. Final FM-1 listening/timing checks for the FX edge
editing are still being completed and documented before a review-ready PR.

I saw the guidance in discussion #60 and the update about Felucca's next phase.
If any of these changes fit mainline, I'd be happy to contribute them as small,
focused PRs, starting with live parts. The combined branch is an overview.

Which additions would be useful to consider first?

[bonszaimusic on YouTube](https://www.youtube.com/@bonszaimusic) ·
[fgunited on GitHub](https://github.com/fgunited)
