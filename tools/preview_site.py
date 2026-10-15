#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build matched preview sites and preserve other channels during publication."""
import argparse
import hashlib
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPOSITORIES = {"fgunited/Felucca", "fgunited/Felucca-PR"}
SHA = re.compile(r"[0-9a-f]{40}")


def route(value):
    if value == ".":
        return value
    if not re.fullmatch(r"[a-z0-9-]+(?:/[a-z0-9-]+)*", value):
        raise ValueError(f"Invalid preview path: {value}")
    if value.split("/")[0] not in {"features", "custom-next", "upstream"}:
        raise ValueError(f"Reserved preview path: {value}")
    return value


def channels(config, workflow_sha, published=None):
    data = json.loads(Path(config).read_text())
    if data["repository"] not in REPOSITORIES:
        raise ValueError("Unexpected repository")
    actual = os.environ.get("GITHUB_REPOSITORY", data["repository"])
    if actual != data["repository"]:
        raise ValueError("Channel configuration belongs to another repository")
    if not SHA.fullmatch(workflow_sha):
        raise ValueError("Workflow commit must be an exact SHA")
    seen_ids, seen_routes = set(), set()
    result = []
    for entry in data["channels"]:
        item = dict(entry)
        if not re.fullmatch(r"[a-z0-9-]+", item["id"]) or item["id"] in seen_ids:
            raise ValueError("Duplicate or invalid channel id")
        seen_ids.add(item["id"])
        for path in [item["path"], *item.get("aliases", [])]:
            route(path)
            if path in seen_routes:
                raise ValueError("Duplicate channel path")
            seen_routes.add(path)
        item["ref"] = workflow_sha if item["ref"] == "@workflow" else item["ref"]
        # Pin every source, including feature candidates. Never build a moving ref.
        if not SHA.fullmatch(item["ref"]):
            raise ValueError("Source ref must be a full commit SHA or @workflow")
        # A pinned channel already has a tested, immutable publication. Reuse it
        # instead of rebuilding it with possibly changed build dependencies.
        # Moving @workflow channels must always pass the complete build suite.
        if published is not None and entry["ref"] != "@workflow":
            immutable = Path(published) / "builds" / item["id"] / item["ref"]
            if immutable.exists():
                original = verify_package(immutable)
                route_folder = Path(published) if item["path"] == "." else Path(published) / item["path"]
                active_original = verify_package(route_folder)
                # Rebuilt artifacts are archived by manifest hash; reuse the exact
                # tested variant currently served, leaving the first archive intact.
                package = original["package"]
                if (immutable / package).read_bytes() != (route_folder / package).read_bytes():
                    for variant in sorted(immutable.iterdir()):
                        if variant.is_dir() and (variant / "build-info.json").is_file():
                            candidate = verify_package(variant)
                            if candidate == active_original and (variant / package).read_bytes() == (route_folder / package).read_bytes():
                                immutable, original = variant, candidate
                                break
                expected = {"id": item["id"], "source_commit": item["ref"],
                            "source_repository": data["repository"], "path": item["path"],
                            "aliases": item.get("aliases", [])}
                if any(original.get(key, [] if key == "aliases" else None) != value
                       for key, value in expected.items()):
                    raise ValueError("Published pinned channel identity or routes differ")
                # The current routes must still serve that exact publication.
                for path in [item["path"], *item.get("aliases", [])]:
                    active_folder = Path(published) if path == "." else Path(published) / path
                    active = verify_package(active_folder)
                    if any(active.get(key) != original.get(key)
                           for key in ["id", "source_repository", "source_commit", "package"]):
                        raise ValueError("Published pinned channel route differs from its archive")
                    package = original["package"]
                    if (immutable / package).read_bytes() != (active_folder / package).read_bytes():
                        raise ValueError("Published pinned channel firmware differs from its archive")
                continue
        result.append(item)
    return result


def assemble(source, out, item, repository):
    if repository not in REPOSITORIES:
        raise ValueError("Unexpected repository")
    route(item["path"])
    source, out = Path(source).resolve(), Path(out).resolve()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
    if not SHA.fullmatch(sha) or sha != item["ref"]:
        raise ValueError("Checked-out source does not match the requested commit")
    package, emulator = source / "build/felucca.fwsc", source / "build/emu"
    for required in [package, emulator / "felucca.wasm", emulator / "index.html", emulator / "worklet.js"]:
        if not required.is_file() or required.stat().st_size == 0:
            raise ValueError(f"Missing build output: {required}")
    version = re.search(r'^#define FELUCCA_VERSION "([^"]+)"',
                        (source / "firmware/src/felucca.c").read_text(), re.M).group(1)
    label = re.sub(r"[^A-Za-z0-9.-]", "-", f"{version.removeprefix('v')}-{item['id']}-{sha[:8]}")
    spec = importlib.util.spec_from_file_location("source_make_site", source / "web/make_site.py")
    maker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(maker)
    maker.main(package, label, out)
    shutil.copytree(emulator, out / "webapp/try", dirs_exist_ok=True)
    emu_page = out / "webapp/try/index.html"
    content = emu_page.read_text()
    storage = json.dumps(f"felucca-emu-flash:{repository}:{item['id']}:{sha}")
    content, replaced = re.subn(r'\bconst\s+STORE\s*=\s*"felucca-emu-flash"(?=\s*[,;])',
                               lambda _: f"const STORE = {storage}", content, count=1)
    if replaced != 1:
        raise ValueError("Emulator storage namespace changed; review channel isolation")
    emu_page.write_text(content)
    shutil.copyfile(package, out / "firmware/felucca-preview.fwsc")
    # Preserve the existing precheck download URL.
    if item["id"] == "precheck":
        shutil.copyfile(package, out / "firmware/felucca-precheck.fwsc")
    for filename in ["felucca.bin", "loader/ota.bin"]:
        shutil.copyfile(source / "build" / filename, out / "firmware" / Path(filename).name)
    attribution = source / "assets/samples-cc0/ATTRIBUTION.txt"
    if attribution.is_file():
        shutil.copyfile(attribution, out / "firmware/SAMPLE-ATTRIBUTION.txt")
    info = {**item, "source_repository": repository, "source_commit": sha,
            "firmware_version": version, "preview_version": label,
            "built_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "workflow_run": os.environ.get("GITHUB_RUN_ID"),
            "checks": "firmware build, target budgets, host suite and WebAssembly checks passed",
            "hardware_test": item.get("hardware_test", "pending"), "package": "firmware/felucca-preview.fwsc"}
    (out / "build-info.json").write_text(json.dumps(info, indent=2) + "\n")
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}\n" for p in files))
    source_url = f"https://github.com/{repository}/commit/{sha}"
    title = html.escape(item["title"])
    description = html.escape(item["description"])
    root_html = f'''<!doctype html><html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>body{{font:17px/1.6 system-ui,sans-serif;max-width:960px;margin:48px auto;padding:0 24px;background:#10151c;color:#edf2f7}}a{{color:#8bd3ff}}h1{{line-height:1.15}}nav,.channels{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px;margin:28px 0}}nav a,.channels a{{display:block;border:1px solid #3d536b;border-radius:12px;padding:18px;text-decoration:none;background:#19232f}}strong,small{{display:block}}small{{color:#b1bdcb}}code{{overflow-wrap:anywhere}}.label{{color:#ffd58b}}</style></head><body>
<p class="label">{html.escape(item['kind'])}</p><h1>{title}</h1><p>{description}</p>
<nav><a href="webapp/try/"><strong>Browser-Emulator</strong>Ohne Gerät spielen und testen</a>
<a href="webapp/editor/"><strong>Web-Editor</strong>Den angeschlossenen FM-1 bearbeiten</a>
<a href="webapp/installer/"><strong>Web-Installer</strong>Genau diese Firmware installieren</a>
<a href="firmware/felucca-preview.fwsc"><strong>Firmware herunterladen</strong>Passendes .fwsc-Paket</a></nav>
<p>Firmware: <code>{html.escape(version)}</code> · Kanal: <code>{html.escape(item['id'])}</code><br>
Quellstand: <a href="{source_url}"><code>{sha[:12]}</code></a></p>
<p>Automatische Prüfungen bestanden. Der Hardwaretest dieses Quellstands steht noch aus.</p>
<p><a href="build-info.json">Build-Informationen</a> · <a href="SHA256SUMS">Prüfsummen</a> ·
<a href="https://github.com/{repository}/actions">Build-Verlauf</a></p>
<!-- CHANNELS -->
</body></html>'''
    (out / "index.html").write_text(root_html)
    # Keep the channel identity visible when opening a direct emulator/editor/installer link.
    for page in [out / f"webapp/{name}/index.html" for name in ["try", "editor", "installer"]]:
        content = page.read_text()
        badge = (f'<div style="position:relative;z-index:99999;background:#10151c;color:#edf2f7;padding:8px;font:13px system-ui">'
                 f'<a style="color:#8bd3ff" href="../../">{title}</a> · {html.escape(label)} · {sha[:12]}</div>')
        content, count = re.subn(r"(<body\b[^>]*>)", lambda m: m[1] + badge, content, count=1, flags=re.I)
        if not count:
            content = badge + content
        page.write_text(content)
    (out / ".nojekyll").touch()
    # Hash final files, including banners and landing page.
    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name != "SHA256SUMS")
    (out / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(out).as_posix()}\n" for p in files))


def verify_package(folder):
    info = json.loads((folder / "build-info.json").read_text())
    if info["source_repository"] not in REPOSITORIES or not SHA.fullmatch(info["source_commit"]):
        raise ValueError("Invalid source metadata")
    for line in (folder / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        path = folder / relative
        if not path.resolve().is_relative_to(folder.resolve()):
            raise ValueError("Checksum path escapes artifact")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Checksum mismatch: {relative}")
    for name in ["index.html", "webapp/try/felucca.wasm", "webapp/editor/index.html",
                 "webapp/installer/index.html", info["package"]]:
        if not (folder / name).is_file():
            raise ValueError(f"Incomplete channel: {name}")
    return info


def publish(incoming, state):
    incoming, state = Path(incoming), Path(state)
    state.mkdir(parents=True, exist_ok=True)
    catalog_path = state / "catalog.json"
    catalog = json.loads(catalog_path.read_text()) if catalog_path.exists() else {}
    entries = []
    for folder in sorted(incoming.glob("channel-*")):
        info = verify_package(folder)
        for path in [info["path"], *info.get("aliases", [])]:
            route(path)
        immutable = state / "builds" / info["id"] / info["source_commit"]
        if immutable.exists():
            verify_package(immutable)
            manifest = (folder / "SHA256SUMS").read_bytes()
            if (immutable / "SHA256SUMS").read_bytes() != manifest:
                # Rebuilding a source commit can produce a different package. Keep
                # the first archive intact and give each validated artifact its own
                # content identity, including firmware, emulator and metadata.
                immutable /= hashlib.sha256(manifest).hexdigest()
                if immutable.exists():
                    verify_package(immutable)
                    if (immutable / "SHA256SUMS").read_bytes() != manifest:
                        raise ValueError("An immutable artifact already exists with different contents")
        entries.append((folder, info, immutable))
    if not entries:
        raise ValueError("No tested channel artifacts")
    # Root first; nested channels and immutable builds always survive a root replacement.
    entries.sort(key=lambda pair: pair[1]["path"] != ".")
    protected = {".git", "builds", "features", "custom-next", "upstream"}
    for folder, info, immutable in entries:
        for path in [info["path"], *info.get("aliases", [])]:
            destination = state if path == "." else state / path
            if path == ".":
                for old in state.iterdir():
                    if old.name not in protected:
                        if old.is_dir():
                            shutil.rmtree(old)
                        else:
                            old.unlink()
            elif destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(folder, destination, dirs_exist_ok=True)
            catalog[path] = {**info, "path": path}
        if not immutable.exists():
            shutil.copytree(folder, immutable)
    catalog_path.write_text(json.dumps(catalog, indent=2) + "\n")
    cards = []
    for path, info in sorted(catalog.items()):
        prefix = "" if path == "." else path + "/"
        title = html.escape(info["title"])
        cards.append(f'<a href="{prefix}webapp/try/"><strong>{title}</strong><small>{html.escape(info["kind"])} · {info["source_commit"][:12]}</small></a>')
    overview = '<h2>Verfügbare Versionen</h2><div class="channels">' + "".join(cards) + '</div>'
    index = state / "index.html"
    if index.exists():
        content = index.read_text()
        content = re.sub(r"<!-- CHANNELS -->.*?<!-- /CHANNELS -->", "<!-- CHANNELS -->", content, flags=re.S)
        content = content.replace("<!-- CHANNELS -->", "<!-- CHANNELS -->" + overview + "<!-- /CHANNELS -->")
        index.write_text(content)
    else:
        index.write_text('<!doctype html><meta charset="utf-8"><title>Felucca previews</title>' + overview)
    # Root index/catalog are publication metadata; each immutable build keeps its own full checksums.
    (state / ".nojekyll").touch()
    sums = state / "SHA256SUMS"
    if sums.exists():
        # The root landing page gains the catalog after assembly.
        lines = []
        for line in sums.read_text().splitlines():
            _, relative = line.split("  ", 1)
            lines.append(f"{hashlib.sha256((state / relative).read_bytes()).hexdigest()}  {relative}")
        sums.write_text("\n".join(lines) + "\n")
    return catalog


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    matrix = sub.add_parser("matrix")
    matrix.add_argument("config")
    matrix.add_argument("--published", type=Path)
    assembly = sub.add_parser("assemble")
    assembly.add_argument("source")
    assembly.add_argument("output")
    publication = sub.add_parser("publish")
    publication.add_argument("incoming")
    publication.add_argument("state")
    args = parser.parse_args()
    if args.command == "matrix":
        print("matrix=" + json.dumps({"include": channels(args.config, os.environ["GITHUB_SHA"], args.published)}, separators=(",", ":")))
    elif args.command == "assemble":
        assemble(args.source, args.output, json.loads(os.environ["CHANNEL_JSON"]), os.environ["GITHUB_REPOSITORY"])
    else:
        publish(args.incoming, args.state)


if __name__ == "__main__":
    main()
