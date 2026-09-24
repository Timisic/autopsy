"""Publication checks use deliberately small repositories with realistic failure cases."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location("repository", Path(__file__).resolve().parents[1] / "scripts/repository.py")
repository = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(repository)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {
            "README.md": "Read [paper](manuscript/latex/manuscript.tex).\n",
            "manuscript/latex/manuscript.tex": "\\includegraphics{figures/plot.pdf}\n",
            "manuscript/latex/figures/plot.pdf": "%PDF fixture\n",
            "tables/metrics.csv": "outcome,rmse\npositive_affect,0.1\n",
            "literature/references.csl.json": json.dumps([
                {"id": f"source-{i}", "issued": {"date-parts": [[2020]]}} for i in range(30)
            ]),
        }
        for name, text in self.files.items():
            self.write(name, text)
        self.config = {
            "files": list(self.files),
            "frozen_results": {"tables/metrics.csv": repository.digest(self.root / "tables/metrics.csv")},
            "languages": {"en": "manuscript/latex"},
        }
        self.save_config()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def save_config(self):
        self.write("configs/publication.json", json.dumps(self.config))

    def errors(self):
        return "\n".join(repository.check_repository(self.root)["errors"])

    def test_valid_repository_and_report(self):
        self.assertEqual(self.errors(), "")
        self.assertEqual(json.loads((self.root / "build/check.json").read_text())["status"], "pass")

    def test_participant_csv_is_rejected_case_insensitively(self):
        self.write("tables/metrics.csv", "Outcome, UiD \npositive,123\n")
        self.assertIn("participant-level CSV", self.errors())

    def test_undeclared_latex_asset_is_rejected_even_if_present(self):
        self.config["files"].remove("manuscript/latex/figures/plot.pdf")
        self.save_config()
        self.assertIn("LaTeX reference figures/plot.pdf", self.errors())

    def test_changed_frozen_result_is_rejected(self):
        self.write("tables/metrics.csv", "outcome,rmse\npositive_affect,0.9\n")
        self.assertIn("frozen result checksum changed", self.errors())

    def test_missing_file_is_rejected(self):
        (self.root / "tables/metrics.csv").unlink()
        self.assertIn("file is missing", self.errors())

    def test_traversal_and_symlink_are_rejected(self):
        self.config["files"].append("../outside.csv")
        (self.root / "alias.csv").symlink_to(self.root / "tables/metrics.csv")
        self.config["files"].append("alias.csv")
        self.save_config()
        errors = self.errors()
        self.assertIn("traversing", errors)
        self.assertIn("symlinks", errors)

    def test_package_contains_only_declared_files(self):
        self.write("data.csv", "UID,score\n123,1\n")
        self.write("manuscript/latex/private.txt", "unpublished material")
        archive_path = repository.package_repository(self.root)
        with zipfile.ZipFile(archive_path) as archive:
            self.assertEqual(set(archive.namelist()), set(self.config["files"]))
            self.assertNotIn("data.csv", archive.namelist())
            self.assertNotIn("manuscript/latex/private.txt", archive.namelist())

    def test_build_uses_isolated_copy_and_preserves_inputs(self):
        for document in ["supplement", "title_page"]:
            name = f"manuscript/latex/{document}.tex"
            self.write(name, "A document.\n")
            self.config["files"].append(name)
        self.write("manuscript/latex/manuscript.pdf", "old PDF")
        self.config["files"].append("manuscript/latex/manuscript.pdf")
        self.save_config()
        original_hashes = {name: repository.digest(self.root / name) for name in self.config["files"]}

        def compile_copy(command, cwd, **kwargs):
            self.assertNotEqual(cwd, self.root / "manuscript/latex")
            document = Path(command[-1]).stem
            self.assertTrue((cwd / command[-1]).is_file())
            if document == "manuscript":
                self.assertFalse((cwd / "manuscript.pdf").exists())
            (cwd / f"{document}.pdf").write_bytes(b"%PDF new compilation")
            return type("Result", (), {"returncode": 0})()

        with patch.object(repository.shutil, "which", return_value="/fake/tectonic"), patch.object(repository.subprocess, "run", side_effect=compile_copy):
            destination, report = repository.build_repository(self.root, language="en")
        self.assertEqual(report["status"], "pass")
        self.assertEqual(len(report["languages"]["en"]["documents"]), 3)
        self.assertTrue((destination / "en/figures/plot.pdf").exists())
        self.assertEqual(original_hashes, {name: repository.digest(self.root / name) for name in self.config["files"]})

    def test_links_inside_code_and_historical_report_are_ignored(self):
        self.write("README.md", "```md\n[old](missing.md)\n```\n`[example](missing.md)`\n")
        self.write("verification/old.md", "[historical](removed.md)")
        self.config["files"].append("verification/old.md")
        self.save_config()
        self.assertEqual(self.errors(), "")

    def test_live_markdown_link_must_be_published(self):
        self.write("README.md", "[private](data.csv)")
        self.write("data.csv", "UID,score\n123,1\n")
        self.assertIn("Markdown link data.csv", self.errors())

    def test_cutoff_and_secret_checks(self):
        records = json.loads(self.files["literature/references.csl.json"])
        records[0]["issued"]["date-parts"] = [[2024, 8, 1]]
        self.write("literature/references.csl.json", json.dumps(records))
        self.write("README.md", "token: " + "ghp_" + "a" * 36)
        errors = self.errors()
        self.assertIn("publication is not before", errors)
        self.assertIn("possible private key or API token", errors)
        self.assertNotIn("a" * 36, errors)


if __name__ == "__main__":
    unittest.main()
