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

Repository roles were clarified by the user on 13 October 2026: **Custom is the default
home for new features and experiments. Felucca-PR is reserved for explicitly selected
official upstream contributions.** General preparation does not select a feature for upstream.

| Repository / branch | Purpose |
| --- | --- |
| `fgunited/Felucca:feature/<feature>` | Develop and test an isolated Custom feature or experiment. |
| `fgunited/Felucca:custom-next` | Complete integration of Bonszai and new Custom features, with its own installer/emulator/editor. |
| `fgunited/Felucca:main` | Released complete Custom firmware; promotion is a separate explicit release step. |
| `fgunited/Felucca:upstream-base/1.6` | Exact upstream 1.6 source tree for independent experiments and later extraction. |
| `fgunited/Felucca-PR:main` | Clean upstream base, currently `1727537624390cc3f9c7dff2456b43b3a8edb005`. |
| `fgunited/Felucca-PR:upstream/<feature>` | One feature explicitly selected for an official upstream PR, with only its code/tests/docs. |
| `fgunited/Felucca-PR:precheck` | Installer/emulator/editor controller for selected PR preparations and the upstream comparison. |
| `gh-pages` in each repository | Generated site state; never merge it into firmware or feature branches. |

### Default feature workflow

1. Inspect current upstream, Custom state and this procedure. Keep released firmware and
   existing selected PR preparations available.
2. Develop a new feature on `fgunited/Felucca:feature/<feature>`; use a suitable verified base
   and focused commits so its patch can later be extracted independently. A JIANT experiment
   does not start in Felucca-PR merely because it might eventually be contributable.
3. Preserve original attribution/GPL notices and defaults. Test sound behavior, parameter
   locks/automation, engine changes and project/user-preset compatibility as relevant.
4. Integrate the same patch into `custom-next`, with combination fixes in that integration
   branch. Register an isolated experiment under `features/<feature>` in the **Custom repo's**
   manifest if useful. The full Custom preview stays at `custom-next/`.
5. Build/test before publishing. Every preview has firmware, USB installer, emulator and
   matching editor built from one exact source SHA. Record hardware results separately.
6. **Only after the user explicitly selects that feature for an official upstream contribution**,
   extract its focused commits onto the clean upstream base in Felucca-PR. List unavoidable
   dependencies; exclude Bonszai branding, unrelated features, deployment infrastructure and
   channel manifests from the feature diff.
7. Register that selected PR-preparation SHA in Felucca-PR's manifest. Its isolated
   installer/emulator/editor supports review and hardware testing before submission. Preserve
   existing feature branches/PRs; do not silently rebase or force-push them.
8. Submit one official upstream PR per selected feature only after the agreed review and
   hardware checks. Official editor changes belong in `hugelton/Felucca-WebApp`.
9. Keep review fixes in Custom and the selected PR candidate in sync. After upstream acceptance,
   sync the upstream base and reconcile against the actual accepted commit to avoid duplication.

### Channels and publication

| Preview | URL |
| --- | --- |
| Stable complete Custom | `https://fgunited.github.io/Felucca/` |
| Complete Custom development version | `https://fgunited.github.io/Felucca/custom-next/` |
| Isolated Custom experiments | `https://fgunited.github.io/Felucca/features/<feature>/` |
| Selected official PR preparation | `https://fgunited.github.io/Felucca-PR/` (currently playback step recording) |
| Additional selected official PR preparations | `https://fgunited.github.io/Felucca-PR/features/<feature>/` |
| Unchanged upstream comparison | `https://fgunited.github.io/Felucca-PR/upstream/` |

Each channel has `webapp/installer/`, `webapp/try/`, `webapp/editor/`, `firmware/`,
`build-info.json` and `SHA256SUMS`. Headers show channel and source SHA. Emulator storage
is isolated per repository/channel/source SHA. Published snapshots remain under
`builds/<channel-id>/<source-sha>/`; other channels are preserved. A failed complete build
publishes nothing. Source refs are full commit SHAs; only the full Custom channel uses
`@workflow`. Stable Bonszai 7 remains pinned until an explicit release promotion.

The controller runs firmware/memory/target checks, the complete host source suite and
WebAssembly/native checks before publication. Linux host tests use `CC="cc -include stdint.h"`
for upstream 1.6's drum stress test; assertions are not disabled. Transient SDK download
failures are retried without changing test requirements. Relevant `github-pages` deployment
branches (`precheck` and `custom-next`) are already authorized; preserve their existing rules.

### BYTE/FLOAT allocation correction

BYTE/FLOAT was prematurely implemented in Felucca-PR before being selected for upstream.
**No official upstream PR was opened.** Its code/tests are preserved as a Custom experiment:

- `fgunited/Felucca:feature/bytebeat`: `472eb6997a26656176068f04c0473b45a8fc5d2e`.
- Experiment preview: `https://fgunited.github.io/Felucca/features/bytebeat/` after successful CI.
- Complete combination: `fgunited/Felucca:custom-next`, preview at `custom-next/`.
- Felucca-PR's BYTE/FLOAT preview entry is withdrawn. Its previously planned `upstream/bytebeat`
  branch is restored to the exact upstream 1.6 tree in `48fe98a821a7f258c9e12f5efa1581eb16203df7`
  without rewriting history; it is inactive and is not an official PR candidate.
- `upstream/morph` and `upstream/phase-feedback` in Felucca-PR are empty planned placeholders,
  not implementations or selected official PRs. Develop those ports in Custom first. PHASE
  feedback must preserve FOLD; settle MORPH/feedback parameter-id/storage compatibility before
  implementing them. Do not silently reuse legacy FM values.
