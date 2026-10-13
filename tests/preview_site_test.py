#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Publication regression checks: preservation, integrity and pinned sources."""
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview_site", ROOT / "tools/preview_site.py")
site = importlib.util.module_from_spec(spec)
spec.loader.exec_module(site)


def artifact(root, channel, path, sha, aliases=(), package=b"firmware"):
    folder = root / f"channel-{channel}"
    folder.mkdir(parents=True, exist_ok=True)
    files = {"index.html": b"<html><!-- CHANNELS --></html>",
             "webapp/try/felucca.wasm": b"wasm", "webapp/editor/index.html": b"editor",
             "webapp/installer/index.html": b"installer", "firmware/felucca-preview.fwsc": package}
    info = {"id": channel, "title": channel, "description": channel, "kind": "TEST",
            "path": path, "aliases": list(aliases), "source_repository": "fgunited/Felucca-PR",
            "source_commit": sha, "package": "firmware/felucca-preview.fwsc"}
    files["build-info.json"] = json.dumps(info).encode()
    for name, content in files.items():
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    (folder / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(content).hexdigest()}  {name}\n" for name, content in files.items()))
    return folder


class Publication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.incoming, self.state = self.root / "incoming", self.root / "state"
        self.incoming.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def clear_incoming(self):
        import shutil
        shutil.rmtree(self.incoming)
        self.incoming.mkdir()

    def test_channels_survive_new_root_and_other_feature(self):
        artifact(self.incoming, "precheck", ".", "a" * 40, ["features/step-record"])
        site.publish(self.incoming, self.state)
        self.clear_incoming()
        artifact(self.incoming, "morph", "features/morph", "b" * 40, package=b"morph")
        site.publish(self.incoming, self.state)
        self.clear_incoming()
        artifact(self.incoming, "precheck", ".", "c" * 40, ["features/phase-feedback"], b"phase")
        catalog = site.publish(self.incoming, self.state)
        self.assertEqual(set(catalog), {".", "features/step-record", "features/morph", "features/phase-feedback"})
        self.assertEqual((self.state / "features/morph/firmware/felucca-preview.fwsc").read_bytes(), b"morph")
        self.assertEqual((self.state / "features/step-record/firmware/felucca-preview.fwsc").read_bytes(), b"firmware")
        self.assertTrue((self.state / ("builds/precheck/" + "a" * 40) / "build-info.json").is_file())
        site.verify_package(self.state)
        self.assertEqual((self.state / "index.html").read_text().count("<h2>Verfügbare Versionen"), 1)

    def test_corrupted_artifact_leaves_previous_site_untouched(self):
        artifact(self.incoming, "precheck", ".", "a" * 40)
        site.publish(self.incoming, self.state)
        original = (self.state / "index.html").read_bytes()
        self.clear_incoming()
        bad = artifact(self.incoming, "morph", "features/morph", "b" * 40)
        (bad / "firmware/felucca-preview.fwsc").write_bytes(b"wrong")
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            site.publish(self.incoming, self.state)
        self.assertEqual((self.state / "index.html").read_bytes(), original)

    def test_immutable_build_cannot_change_firmware(self):
        artifact(self.incoming, "precheck", ".", "a" * 40)
        site.publish(self.incoming, self.state)
        self.clear_incoming()
        artifact(self.incoming, "precheck", ".", "a" * 40, package=b"changed")
        with self.assertRaisesRegex(ValueError, "immutable"):
            site.publish(self.incoming, self.state)

    def test_pins_and_paths_are_validated(self):
        config = self.root / "channels.json"
        data = {"repository": os.environ.get("GITHUB_REPOSITORY", "fgunited/Felucca-PR"),
                "channels": [{"id": "precheck", "ref": "main", "path": "."}]}
        config.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "full commit SHA"):
            site.channels(config, "a" * 40)
        data["channels"][0]["ref"] = "@workflow"
        config.write_text(json.dumps(data))
        self.assertEqual(site.channels(config, "a" * 40)[0]["ref"], "a" * 40)
        for bad in ["../main", ".git", "features/../main", "/features/morph", "webapp"]:
            with self.assertRaises(ValueError):
                site.route(bad)

    def test_assembly_uses_the_source_editor_and_isolates_emulator_storage(self):
        source = self.root / "source"
        (source / "web").mkdir(parents=True)
        for name in ["make_site.py", "index_pkg.html", "fm1pkg.js", "fm1ota.js", "fm1backup.js", "editor.html"]:
            shutil.copyfile(ROOT / "web" / name, source / "web" / name)
        for name in ["LICENSE", "LICENSING.md"]:
            shutil.copyfile(ROOT / name, source / name)
        shutil.copytree(ROOT / "LICENSES", source / "LICENSES")
        (source / "firmware/src").mkdir(parents=True)
        (source / "firmware/src/felucca.c").write_text('#define FELUCCA_VERSION "v1.6"\n')
        emulator = source / "build/emu"
        emulator.mkdir(parents=True)
        (emulator / "index.html").write_text('<html><body><script>const STORE = "felucca-emu-flash", KNOBS_ON = "felucca-emu-knobs";</script></body></html>')
        (emulator / "felucca.wasm").write_bytes(b"wasm-fixture")
        (emulator / "worklet.js").write_text("// worklet fixture\n")
        (source / "build/loader").mkdir()
        (source / "build/loader/ota.bin").write_bytes(b"loader-fixture")
        (source / "build/felucca.bin").write_bytes(b"app-fixture")
        raw = bytearray(b"\x7d" * 1024)
        for i, character in enumerate("FM-1_900"):
            raw[i * 0x30 + 0x2f] = (ord(character) + i + 1) & 255
        raw.extend(b"FELUCCA-LOADER-1")
        (source / "build/felucca.fwsc").write_bytes(raw)
        subprocess.run(["git", "init", "-q", str(source)], check=True)
        subprocess.run(["git", "add", "."], cwd=source, check=True)
        subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                        "commit", "-qm", "source fixture"], cwd=source, check=True)
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=source, text=True).strip()
        item = {"id": "morph", "title": "Morph candidate", "description": "one feature", "kind": "TEST",
                "path": "features/morph", "aliases": [], "ref": sha}
        out = self.incoming / "channel-morph"
        site.assemble(source, out, item, "fgunited/Felucca-PR")
        info = site.verify_package(out)
        self.assertEqual(info["source_commit"], sha)
        self.assertEqual((out / info["package"]).read_bytes(), raw)
        self.assertIn(f"felucca-emu-flash:fgunited/Felucca-PR:morph:{sha}", (out / "webapp/try/index.html").read_text())
        self.assertIn('KNOBS_ON = "felucca-emu-knobs"', (out / "webapp/try/index.html").read_text())
        self.assertIn("Morph candidate", (out / "webapp/editor/index.html").read_text())
        self.assertIn("../../firmware/felucca-1.6-morph-", (out / "webapp/installer/index.html").read_text())
        item["ref"] = "b" * 40
        with self.assertRaisesRegex(ValueError, "does not match"):
            site.assemble(source, self.root / "wrong", item, "fgunited/Felucca-PR")


if __name__ == "__main__":
    unittest.main()
