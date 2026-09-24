#!/usr/bin/env python3
"""Check, compile, or package the exact publication manifest without changing inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timezone
from urllib.parse import unquote, urlsplit
import zipfile

DEFAULT_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_COLUMNS = {"uid", "source_row", "participant_id"}
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b"),
    re.compile(r"\bsk-(?:proj-|ant-)[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")


def public_path(root, name):
    """Require a regular, root-contained file, without symlinks in its path."""
    if not isinstance(name, str) or not name or "\\" in name:
        raise ValueError("path must be a nonempty POSIX relative path")
    relative = PurePosixPath(name)
    if relative.is_absolute() or name != relative.as_posix() or any(part in {"..", "."} for part in name.split("/")):
        raise ValueError("absolute and traversing paths are prohibited")
    path = root.joinpath(*relative.parts)
    if not path.resolve().is_relative_to(root):
        raise ValueError("path escapes repository")
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError("symlinks are prohibited")
    if not path.is_file():
        raise ValueError("file is missing")
    return path


def load_publication(root, config=None):
    config = Path(config) if config else Path("configs/publication.json")
    path = config if config.is_absolute() else root / config
    relative = path.relative_to(root).as_posix()
    public_path(root, relative)
    publication = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(publication, dict):
        raise ValueError("publication manifest must be an object")
    if not isinstance(publication.get("files"), list):
        raise ValueError("publication.files must be an exact list of paths")
    if not all(isinstance(name, str) for name in publication["files"]):
        raise ValueError("publication.files entries must be strings")
    if not isinstance(publication.get("frozen_results", {}), dict):
        raise ValueError("publication.frozen_results must map paths to checksums")
    return publication, relative


def without_markdown_code(text):
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def markdown_destinations(text):
    text = without_markdown_code(text)
    # Inline links/images and reference-style definitions; optional titles are ignored.
    for match in re.finditer(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^\n]*)?\)", text):
        yield match.group(1).strip("<>")
    for match in re.finditer(r"^\s{0,3}\[[^\]\n]+\]:\s*(<[^>]+>|\S+)", text, re.M):
        yield match.group(1).strip("<>")


def referenced_path(root, source, destination):
    parts = urlsplit(destination)
    if parts.scheme or parts.netloc or not parts.path:
        return None
    decoded = unquote(parts.path)
    target = root / decoded.lstrip("/") if decoded.startswith("/") else source.parent / decoded
    if not target.resolve().is_relative_to(root):
        raise ValueError("reference escapes repository")
    return target.resolve().relative_to(root).as_posix()


def check_repository(root, config=None, staged=False):
    root = Path(root).resolve()
    errors = []
    report = {"status": "fail", "checked_files": 0, "errors": errors}
    try:
        publication, config_name = load_publication(root, config)
        names = publication["files"]
        allowed = set(names)
        if len(names) != len(allowed):
            errors.append("publication.files contains duplicates")
        valid = {}
        for name in names:
            try:
                valid[name] = public_path(root, name)
            except (ValueError, OSError) as exc:
                errors.append(f"{name}: {exc}")
        report["checked_files"] = len(valid)
        for name, expected in publication.get("frozen_results", {}).items():
            if name not in allowed:
                errors.append(f"{name}: frozen result is absent from publication.files")
            elif name in valid and digest(valid[name]) != expected:
                errors.append(f"{name}: frozen result checksum changed")
        for name, path in valid.items():
            if path.suffix.lower() == ".csv":
                with path.open(encoding="utf-8-sig", newline="") as handle:
                    fields = next(csv.reader(handle), [])
                leaked = FORBIDDEN_COLUMNS.intersection(field.strip().casefold() for field in fields)
                if leaked:
                    errors.append(f"{name}: participant-level CSV columns: {', '.join(sorted(leaked))}")
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                errors.append(f"{name}: possible private key or API token (value suppressed)")
            if path.suffix.lower() == ".tex":
                tex = re.sub(r"(?<!\\)%[^\n]*", "", text)
                for command, target in re.findall(r"\\(includegraphics\*?|input|include)(?:\[[^\]]*\])?\s*\{([^}]+)\}", tex):
                    try:
                        if Path(target).is_absolute():
                            raise ValueError("LaTeX references must be relative")
                        resolved = referenced_path(root, path, target)
                        if resolved is None:
                            raise ValueError("LaTeX references must be repository files")
                        candidates = [resolved]
                        if not Path(resolved).suffix:
                            extensions = [".pdf", ".png", ".jpg", ".jpeg"] if command.startswith("includegraphics") else [".tex"]
                            candidates += [resolved + extension for extension in extensions]
                        if not any(candidate in valid for candidate in candidates):
                            raise ValueError("asset is missing or absent from publication.files")
                    except (ValueError, OSError) as exc:
                        errors.append(f"{name}: LaTeX reference {target}: {exc}")
            if path.suffix.lower() == ".md" and not name.startswith("verification/"):
                for target in markdown_destinations(text):
                    try:
                        resolved = referenced_path(root, path, target)
                        if resolved is None:
                            continue
                        destination = root / resolved
                        if destination.is_dir():
                            if not any(item.startswith(resolved.rstrip("/") + "/") for item in valid):
                                raise ValueError("directory has no published files")
                        elif resolved not in valid:
                            raise ValueError("target is missing or absent from publication.files")
                    except (ValueError, OSError) as exc:
                        errors.append(f"{name}: Markdown link {target}: {exc}")
        bibliography = valid.get("literature/references.csl.json")
        if bibliography is None:
            errors.append("literature/references.csl.json: required published bibliography is missing")
        else:
            records = json.loads(bibliography.read_text(encoding="utf-8"))
            if not isinstance(records, list) or len(records) != 30:
                errors.append("bibliography must contain exactly 30 records")
            else:
                for record in records:
                    if not isinstance(record, dict):
                        errors.append("bibliography records must be objects")
                        continue
                    try:
                        parts = record["issued"]["date-parts"][0]
                        # Incomplete 2024 dates cannot establish the stated cutoff.
                        if parts[0] == 2024 and len(parts) < 2:
                            raise ValueError("2024 publication needs at least a month")
                        issued = date(*(list(parts[:3]) + [1] * (3 - len(parts[:3]))))
                        if issued >= date(2024, 8, 1):
                            raise ValueError("publication is not before 2024-08-01")
                    except (KeyError, IndexError, TypeError, ValueError) as exc:
                        errors.append(f"bibliography {record.get('id', '?')}: invalid publication date: {exc}")
        if staged:
            result = subprocess.run(["git", "diff", "--cached", "--name-only", "-z"], cwd=root, check=True, capture_output=True)
            staged_names = result.stdout.decode().strip("\0").split("\0") if result.stdout else []
            for name in staged_names:
                if name not in allowed and name != config_name:
                    errors.append(f"{name}: staged file is absent from publication.files")
        report["frozen_results"] = len(publication.get("frozen_results", {}))
    except (ValueError, OSError, KeyError, csv.Error, subprocess.CalledProcessError) as exc:
        errors.append(f"configuration/check error: {exc}")
    report["status"] = "pass" if not errors else "fail"
    output = root / "build"
    output.mkdir(exist_ok=True)
    (output / "check.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def require_check(root, config):
    report = check_repository(root, config)
    if report["errors"]:
        raise ValueError("publication check failed; see build/check.json")
    return load_publication(root, config)[0]


def package_repository(root, config=None):
    root = Path(root).resolve()
    publication = require_check(root, config)
    destination = root / "build" / f"autopsy-writing-{timestamp()}.zip"
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in publication["files"]:
            archive.write(public_path(root, name), name)
    return destination


def build_repository(root, config=None, language="all"):
    root = Path(root).resolve()
    publication = require_check(root, config)
    languages = publication.get("languages", {})
    if not isinstance(languages, dict) or any(key not in {"en", "zh"} for key in languages):
        raise ValueError("publication.languages must map en/zh to source directories")
    for source_directory in languages.values():
        if not isinstance(source_directory, str) or not source_directory:
            raise ValueError("language source directory must be a relative path")
        relative = PurePosixPath(source_directory)
        if relative.is_absolute() or any(part in {"..", "."} for part in source_directory.split("/")):
            raise ValueError("language source directory must be a relative path without traversal")
    selected = list(languages) if language == "all" else [language]
    if any(item not in languages for item in selected) or not selected:
        raise ValueError("requested language is not configured")
    engine = shutil.which("tectonic")
    if not engine:
        raise ValueError("tectonic is required for compilation")
    destination = root / "build" / timestamp()
    destination.mkdir()
    report = {"status": "pass", "engine": engine, "languages": {}}
    for language_name in selected:
        prefix = languages[language_name].rstrip("/") + "/"
        work = destination / language_name
        work.mkdir()
        entry = {"inputs": {}, "documents": {}}
        report["languages"][language_name] = entry
        for name in publication["files"]:
            if not name.startswith(prefix):
                continue
            relative = name[len(prefix):]
            if relative in {"manuscript.pdf", "supplement.pdf", "title_page.pdf"}:
                continue
            source = public_path(root, name)
            target = work / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            entry["inputs"][name] = digest(source)
        for document in ["manuscript", "supplement", "title_page"]:
            log = work / f"{document}.compile.log"
            with log.open("w", encoding="utf-8") as handle:
                try:
                    result = subprocess.run([engine, "--keep-logs", f"{document}.tex"], cwd=work, stdout=handle, stderr=subprocess.STDOUT, timeout=900)
                    code = result.returncode
                except subprocess.TimeoutExpired:
                    code = 124
                    handle.write("\nCompilation timed out.\n")
            pdf = work / f"{document}.pdf"
            success = code == 0 and pdf.is_file()
            entry["documents"][document] = {"status": "pass" if success else "fail", "returncode": code, "pdf_sha256": digest(pdf) if pdf.is_file() else None}
            if not success:
                report["status"] = "fail"
        for name, expected in entry["inputs"].items():
            if digest(public_path(root, name)) != expected:
                report["status"] = "fail"
                entry.setdefault("errors", []).append(f"Input changed during compilation: {name}")
    (destination / "build_manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return destination, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["check", "build", "package"])
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--config", type=Path, help="Manifest path relative to root (default: configs/publication.json)")
    parser.add_argument("--staged", action="store_true", help="Check staged Git paths as well")
    parser.add_argument("--language", choices=["en", "zh", "all"], default="all")
    args = parser.parse_args()
    try:
        if args.command == "check":
            report = check_repository(args.root, args.config, args.staged)
            print(f"{report['status']}: {report['checked_files']} files; {len(report['errors'])} errors")
            for error in report["errors"]:
                print(error, file=sys.stderr)
            return 0 if report["status"] == "pass" else 1
        if args.command == "package":
            print(package_repository(args.root, args.config))
            return 0
        destination, report = build_repository(args.root, args.config, args.language)
        print(f"{report['status']}: {destination}")
        return 0 if report["status"] == "pass" else 1
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
