#!/usr/bin/env python3
"""Assemble the precheck Pages site from this checkout's tested build outputs."""
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import importlib.util


def main(out):
    root = Path(__file__).resolve().parents[1]
    out = Path(out).resolve()
    package = root / 'build/felucca.fwsc'
    emu = root / 'build/emu'
    for required in [package, emu / 'felucca.wasm', emu / 'index.html', emu / 'worklet.js']:
        if not required.is_file():
            raise SystemExit(f'Missing build output: {required}')
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    version = re.search(r'^#define FELUCCA_VERSION "([^"]+)"',
                        (root / 'firmware/src/felucca.c').read_text(), re.M).group(1)
    label = f'{version.removeprefix("v")}-precheck-{sha[:8]}'
    spec = importlib.util.spec_from_file_location('make_site', root / 'web/make_site.py')
    maker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(maker)
    maker.main(package, label, out)
    shutil.copytree(emu, out / 'webapp/try', dirs_exist_ok=True)
    # Stable URL for downloads; the installer uses the SHA-labelled package.
    shutil.copyfile(package, out / 'firmware/felucca-precheck.fwsc')
    (out / '.nojekyll').touch()
    repository = os.environ.get('GITHUB_REPOSITORY', 'fgunited/Felucca-PR')
    if repository != 'fgunited/Felucca-PR':
        raise SystemExit('This preview is scoped to fgunited/Felucca-PR')
    stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    checksums = []
    for relative in [f'firmware/felucca-{label}.fwsc', 'firmware/felucca-precheck.fwsc',
                     'webapp/try/felucca.wasm']:
        digest = hashlib.sha256((out / relative).read_bytes()).hexdigest()
        checksums.append(f'{digest}  {relative}')
    (out / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
    info = {'branch': 'precheck', 'source_commit': sha, 'firmware_version': version,
            'preview_version': label, 'built_at_utc': stamp,
            'workflow_run': os.environ.get('GITHUB_RUN_ID'),
            'hardware_test': 'pending', 'package': 'firmware/felucca-precheck.fwsc'}
    (out / 'build-info.json').write_text(json.dumps(info, indent=2) + '\n')
    source = f'https://github.com/{repository}/commit/{sha}'
    body = f'''<!doctype html>
<html lang="de"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Felucca Precheck</title>
<style>body{{font:17px/1.6 system-ui,sans-serif;max-width:850px;margin:60px auto;padding:0 24px;background:#10151c;color:#edf2f7}}a{{color:#8bd3ff}}h1{{line-height:1.1}}nav{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:32px 0}}nav a{{display:block;border:1px solid #3d536b;border-radius:12px;padding:20px;text-decoration:none;background:#19232f}}nav strong{{display:block;font-size:22px}}nav span{{color:#c4cfdd}}code{{overflow-wrap:anywhere}}.label{{color:#ffd58b}}small{{color:#b1bdcb}}</style>
<p class="label">TESTBUILD · PRECHECK</p><h1>Felucca ausprobieren</h1>
<p>Erst im Browser ausprobieren, dann bei Bedarf am FM-1 testen.</p>
<nav>
<a href="webapp/try/"><strong>Browser-Emulator</strong><span>Spielen und Step Recording ohne Gerät testen.</span></a>
<a href="webapp/editor/"><strong>Web-Editor</strong><span>Den angeschlossenen FM-1 über USB bearbeiten.</span></a>
<a href="webapp/installer/"><strong>Firmware installieren</strong><span>Diesen Testbuild in Chrome oder Edge auf den FM-1 übertragen.</span></a>
<a href="firmware/felucca-precheck.fwsc" download><strong>Firmware herunterladen</strong><span>Installierbares .fwsc-Paket desselben Builds.</span></a>
</nav>
<h2>Step Recording testen</h2>
<p><strong>SEQ &gt; STEP → PLAY → SEQ halten + REC.</strong> Im Emulator hält Shift-Klick auf SEQ den Button fest; REC anklicken und SEQ mit erneutem Shift-Klick lösen.</p>
<p>Unten steht <strong>STEP REC</strong>. Noten oder Akkorde spielen: Die Eingabe erfolgt am Cursor. Nach Loslassen aller Noten rückt er weiter, während der Playhead läuft (CHORD ENTRY: HOLD). SEQ halten + REC schaltet auf <strong>LIVE REC</strong>; REC allein beendet die Aufnahme.</p>
<p>Vor einer Installation ein Backup im Web-Editor sichern. Dieser Build ist zum Testen bestimmt; ein Hardwaretest steht noch aus.</p>
<p><small>Firmware: {html.escape(version)} · Branch: <code>precheck</code><br>
Quellstand: <a href="{source}"><code>{sha[:12]}</code></a> · Erstellt: {stamp}<br>
<a href="SHA256SUMS">Prüfsummen</a> · <a href="build-info.json">Build-Informationen</a> · <a href="https://github.com/{repository}/actions/workflows/precheck.yml">Build-Verlauf</a></small></p>
</html>'''
    (out / 'index.html').write_text(body, encoding='utf-8')
    (out / 'firmware/index.html').write_text(
        '<!doctype html><meta charset="utf-8"><title>Felucca Precheck Firmware</title>'
        '<h1>Precheck Firmware</h1><p><a href="felucca-precheck.fwsc">Firmware (.fwsc)</a></p>'
        '<p><a href="../webapp/installer/">Web-Installer</a> · <a href="../SHA256SUMS">Prüfsummen</a></p>'
        '<p><a href="LICENSE">GPL-3.0</a> · <a href="LICENSING.md">Lizenzhinweise</a> · <a href="LICENSES/">Weitere Lizenzen</a></p>')
    print(f'Precheck site: {out}, source {sha}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('usage: make_precheck_site.py OUT_DIR')
    main(sys.argv[1])
