"""Assemble the reviewed publication; keep the baseline byte-for-byte in trace."""
import hashlib
import io
import json
import subprocess
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path.cwd()
BASE = '51e1e780111c712e43e1202e2b9f305111f3eaf3'
DELIVERY = ROOT / '.delivery'
manifest = json.loads((DELIVERY / 'payload.b64').read_text())
raw = b''.join((DELIVERY / name).read_bytes() for name in manifest['parts'])
assert hashlib.sha256(raw).hexdigest() == manifest['sha256'], 'Payload checksum mismatch'
archive = tarfile.open(fileobj=io.BytesIO(raw), mode='r:xz')
members = archive.getmembers()
assert len(members) == 58 and sum(m.size for m in members) < 3000000
seen = set()
for member in members:
    path = PurePosixPath(member.name)
    assert member.isfile() and not path.is_absolute() and '..' not in path.parts
    assert str(path) not in seen
    seen.add(str(path))
    assert path.parts[0] in {'.gitattributes', '.gitignore', 'README.md', 'build.sh', 'en', 'zh', 'trace'}
    assert not str(path).startswith('trace/baseline/')

changed = subprocess.check_output(['git', 'diff', '--name-only', BASE, 'HEAD'], text=True).splitlines()
assert all(p.startswith(('.delivery/', '.github/workflows/')) for p in changed), changed
originals = subprocess.check_output(['git', 'ls-tree', '-r', '-z', '--name-only', BASE]).decode().strip('\0').split('\0')
old_publication = json.loads(subprocess.check_output(['git', 'show', BASE + ':configs/publication.json']))
assert set(originals) == set(old_publication['files']), 'Baseline allowlist differs from tracked files'
archive_dirs = {'configs', 'data', 'docs', 'environment', 'literature', 'results', 'scripts', 'tables', 'verification'}
archive_files = {'AGENTS.md', 'CONTEXT.md', 'WRITING_HANDOFF.md', 'README.md', '.gitignore', '.gitattributes'}
archived = {}
for name in originals:
    source = ROOT / name
    expected = subprocess.check_output(['git', 'show', BASE + ':' + name])
    assert source.read_bytes() == expected, 'Unexpected baseline modification: ' + name
    if PurePosixPath(name).parts[0] in archive_dirs or name in archive_files:
        dest = ROOT / 'trace' / 'baseline' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(expected)
        archived[dest.relative_to(ROOT).as_posix()] = hashlib.sha256(expected).hexdigest()
# Delete only the explicitly enumerated baseline files. Git history remains intact.
for name in originals:
    (ROOT / name).unlink()
for member in members:
    dest = ROOT / member.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(archive.extractfile(member).read())
    dest.chmod(0o644)
archive.close()
# Three passes stabilize the Chinese manuscript's cross-references from a clean build.
build = ROOT / 'build.sh'
text = build.read_text()
assert 'for pass in 1 2; do' in text
build.write_text(text.replace('for pass in 1 2; do', 'for pass in 1 2 3; do'))
build.chmod(0o755)
readme = ROOT / 'README.md'
text = readme.read_text()
assert '用 XeLaTeX 连续编译所需主文件两遍' in text
text = text.replace('用 XeLaTeX 连续编译所需主文件两遍', '用 XeLaTeX 连续编译所需主文件三遍，直至交叉引用稳定')
text += '\nDebian/Ubuntu 最小环境依赖：`texlive-xetex texlive-latex-extra texlive-lang-chinese texlive-fonts-recommended fonts-liberation`。其中 `texlive-fonts-recommended` 提供超链接所需的字体度量。\n'
readme.write_text(text)
# Preserve historical byte streams, including CRLF, when Git stages the trace.
(ROOT / 'trace/.gitattributes').write_text('baseline/** -text\n')
expected_files = {m.name: hashlib.sha256((ROOT / m.name).read_bytes()).hexdigest() for m in members}
expected_files['trace/.gitattributes'] = hashlib.sha256((ROOT / 'trace/.gitattributes').read_bytes()).hexdigest()
(DELIVERY / 'expected_files.json').write_text(json.dumps(expected_files, indent=2) + '\n')
(DELIVERY / 'archived_files.json').write_text(json.dumps(archived, indent=2) + '\n')
(ROOT / 'trace' / 'local_pdf_checks.json').write_text(json.dumps(manifest['local_pdf_checks'], indent=2) + '\n')
print('Extracted', len(members), 'reviewed files; archived', len(archived), 'baseline files unchanged.')
