# Contributing to Felucca

Thanks for helping! To keep things easy to follow, please use the right place:

| What | Where |
|---|---|
| A bug you can reproduce | [Issues](https://github.com/hugelton/Felucca/issues/new/choose): one issue per bug |
| A feature idea or request | [Discussions › Ideas](https://github.com/hugelton/Felucca/discussions/categories/ideas) (no promise it will be added) |
| How to use it, or how something works | [Discussions › Q&A](https://github.com/hugelton/Felucca/discussions/categories/q-a) |
| Forks, mods, music, demos | [Discussions › Show and tell](https://github.com/hugelton/Felucca/discussions/categories/show-and-tell) |
| Anything else | [Discussions › General](https://github.com/hugelton/Felucca/discussions/categories/general) |

Feature requests posted as issues will be moved to Discussions or closed.

## Reporting a bug

Please include the Felucca version (hold HOME > ABOUT), your computer's OS and browser if the editor or
installer is involved, the steps to reproduce it, what you expected and what happened. A photo or a short
video helps.

## Pull requests

Pull requests are welcome, including AI-assisted ones, with the same bar for all:

- keep it small and focused on one thing;
- make sure you understand the change and can explain it;
- test it on a real FM-1;
- run `tests/run_tests.sh` (see [BUILDING.md](BUILDING.md));
- new files carry the GPL-3.0-only SPDX header.

By contributing you agree that your contribution is licensed under GPL-3.0-only.

The web editor and installer live in [Felucca-WebApp](https://github.com/hugelton/Felucca-WebApp).

## Bonszai development and upstream contributions

This section applies to the infrastructure branches of the FGUnited repositories. It must not
be copied into an upstream feature PR. The user requested this workflow on 13 October 2026.

| Repository / branch | Purpose |
| --- | --- |
| `fgunited/Felucca-PR:main` | Exact upstream base, initially Felucca 1.6 at `1727537624390cc3f9c7dff2456b43b3a8edb005`; update by fast-forward when possible. |
| `fgunited/Felucca-PR:upstream/<feature>` | One independently reviewable feature, branched from the upstream base. |
| `fgunited/Felucca-PR:precheck` | Preview controller, channel manifest, publication code and this procedure. |
| `fgunited/Felucca:custom-next` | Complete integration build: existing Bonszai additions plus selected new features. |
| `fgunited/Felucca:main` | Released complete Custom firmware. Promotion is a separate, explicit release step. |
| `gh-pages` in each repository | Generated persistent site state; never merge it into firmware or PR branches. |

### Feature development

1. Check current upstream, repository state and this procedure before changing firmware. Keep
   existing test candidates and the released Custom version available.
2. Start `upstream/<feature>` from the exact current upstream commit. Develop each feature once
   here, with focused tests, compatible defaults and documentation in the existing README,
   CREDITS or manual structure. Preserve original JIANT/Felucca attribution and GPL notices.
3. Existing feature branches and their open PRs are not rebased or force-pushed silently.
   Independent features start from upstream; unavoidable dependencies must be listed and
   introduced with a separate prerequisite PR or an explicitly stacked branch.
4. Register the feature's **full 40-character commit SHA** in
   `.github/preview-channels.json` on `precheck`. Add a unique id, title, description and
   `features/<feature>` path. Updating the manifest and pushing `precheck` triggers builds
   and tests. A moving source branch name is deliberately rejected.
5. Merge the same feature branch into `custom-next`; apply combination-specific fixes there.
   Do not reimplement the feature independently. Feed review changes back into both builds.
6. Run the existing complete firmware suite and relevant new tests. Add combination checks for
   automation, MIDI Learn, parameter locks, engine changes, project/preset round trips, external
   clock and worst-case multi-track FX load as appropriate. Do not overwrite unrelated golden
   renders or raise CPU budgets just to make tests pass.
7. Publish the isolated feature candidate and the complete Custom candidate. Perform the
   user's browser and FM-1 checks before upstream submission or Custom release. Automatic
   checks and browser performance do not establish FM-1 hardware stability.
8. Create one upstream PR per feature. The diff contains only feature code, tests and relevant
   documentation: no fork branding, site controller, channel manifest or release workflows.
   Web editor changes needing the official editor belong in `hugelton/Felucca-WebApp`.
9. On upstream acceptance, sync the upstream base and reconcile the Custom integration using
   the actual merge commit; avoid applying an accepted feature a second time.

### Preview and release channels

Each successful channel contains its matching firmware, USB installer, web editor and browser
emulator, built from one pinned source commit. Every page displays its channel and source SHA;
`build-info.json` and `SHA256SUMS` identify the artifacts. Emulator storage is isolated per source
commit so incompatible preview projects do not leak between builds. Browser saves from the
previous shared emulator storage remain there; they are not migrated or erased automatically.

- PR precheck: `https://fgunited.github.io/Felucca-PR/` (currently the step-recording candidate).
- Independent PR previews: `https://fgunited.github.io/Felucca-PR/features/<feature>/`.
- Upstream comparison: `https://fgunited.github.io/Felucca-PR/upstream/`.
- Complete released Custom reference: `https://fgunited.github.io/Felucca/`.
- Complete integration preview: `https://fgunited.github.io/Felucca/custom-next/`.
- Every channel has `webapp/try/`, `webapp/editor/`, `webapp/installer/` and `firmware/`.
- Exact build snapshots are retained at `builds/<channel-id>/<source-sha>/`. Other feature pages
  and previous snapshots survive later publications. Repository Actions artifacts are an
  additional download, not the permanent archive.

The controller's own commit is captured by `@workflow` only for `custom-next`; all other sources
are explicitly pinned. Keep the stable Custom source pinned to its released commit until the
user approves promotion. Never present an empty planned feature branch as an implemented feature.
To select another current PR candidate, update the root manifest entry and add/preserve its
`features/<feature>` alias; earlier feature routes remain available.

All registered channels must pass source builds, target checks, the complete host suite and
WebAssembly checks before any site is deployed. The infrastructure suite also verifies checksums,
channel preservation and source pinning. Hardware tests remain separately recorded. Optional
upstream checks such as the DaisySP comparison are subject to their documented dependencies;
the host CPU counter is platform-dependent, and target budgets are estimates, not real device timing.
On the Linux runner, host tests use `CC="cc -include stdint.h"`: upstream 1.6's drum stress test
uses `uint32_t` before including its standard header with PREEMPT. This supplies that header
without modifying firmware sources, disabling the stress test or changing its assertions.

Publication is serialized per repository. It loads `gh-pages`, verifies the new artifacts,
updates only their channels, retains immutable builds and deploys the whole site. Never use an
older standalone preview workflow to deploy just one subtree: that would erase other channels.
The channel controller replaces the legacy Custom publishers when `custom-next` is eventually
promoted to `main`. Keep GitHub Pages set to Actions and allow the relevant controller branch
(`precheck` or `custom-next`, later `main`) in the existing `github-pages` environment.

### Initial state and next integration step

- The previous Step Recording candidate remains pinned at
  `6ec3268bb7cc92a3edeb1080d2def765a103b768` (1.5.6-based). Existing feature branches are retained.
- New planned branches are `upstream/morph`, `upstream/phase-feedback` and `upstream/bytebeat`,
  starting from upstream 1.6. They contain no implementation yet.
- `custom-next` initially preserves the complete Bonszai 7 firmware from
  `2103e6fb669267fb4f2ea0901042a90313ee6f46`, adding only infrastructure and procedure changes.
- First synchronize the Custom firmware with upstream 1.6 in a separate integration change.
  The trial merge found real conflicts in sequencer, persistence, UI and tests; no conflicted
  firmware is published. Verify Bonszai behavior and reconcile overlapping upstream features
  (especially DOUBLE/HALF) before integrating new JIANT sound features.
- The released `1.5.1-bonszai-7` tag and existing upstream PR history are retained.

### First sound-feature candidate

`upstream/bytebeat` starts directly from upstream 1.6. Source `320be19afb0415e3a80c6c2fb57490b2e60d262b` appends LOFI BYTE/FLOAT (32 formulas each, two presets), preserving the five existing waves, preset indexes and the 111-parameter storage layout. Its installer, emulator and editor are at `https://fgunited.github.io/Felucca-PR/features/bytebeat/` after the complete channel workflow succeeds. Local upstream-reference renders, formula bounds/time-wrap, live-mode/retrigger, project/user-preset and UBSan tests pass; the 100-render regression has zero existing sound or health changes. MORPH and PHASE feedback remain separate, unimplemented branches.
