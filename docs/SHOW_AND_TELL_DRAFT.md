<!-- SPDX-License-Identifier: GPL-3.0-only -->
# Show and tell draft

**Suggested title:** Live workflow extensions for Felucca: parts, step recording and FX automation

Hi Leo and everyone,

I've been extending Felucca for my live workflow as **bonszaimusic / fgunited**.
The goal is to build and vary parts while the music keeps playing.

The additions are:

- Live A–D switching at track 1's loop boundary, keeping sounds and tempo.
- Saving parts during playback as RAM snapshots, committed after STOP.
- STEP REC at an independent cursor while the sequencer continues.
- Recording all fourteen FX-special keys with fine press/release timing.
- A project setting for the track that owns global FX automation.
- Independent FX ON/OFF step/fine editing for start and duration.
- Selective deletion of an FX ON + next OFF, or OFF + previous ON, including across the loop; one undo restores both.
- DUP x2 for steps, locks and automation, with a clean playback transition.
- Project INIT without rebooting.

The [prepared integration](https://github.com/fgunited/Felucca-PR/pull/1) uses
neutral Felucca versioning and includes the complete feature list. I intend to
submit **one combined upstream PR**, with the individual changes explained in
its description. The earlier feature branches are preparation checkpoints.

Development used AI-assisted coding. The exact source passed the
full firmware suite and WebAssembly tests; I tested the published Bonszai 7 build on my FM-1 on 11 October 2026 and confirmed
that everything works, including the latest workflow with selective FX deletion.

I read the guidance in discussion #60 and the update about Felucca's next phase.
I understand the preference for focused changes and am presenting these together
as a coordinated live workflow, with tests and user guides for review.

[bonszaimusic on YouTube](https://www.youtube.com/@bonszaimusic) ·
[fgunited on GitHub](https://github.com/fgunited)
