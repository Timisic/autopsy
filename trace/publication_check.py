"""Verify the actual rebuilt publication without retraining statistical models."""
import collections
import datetime
import hashlib
import json
import os
import re
import subprocess
import unicodedata
from pathlib import Path

ROOT = Path.cwd()
TRACE = ROOT / 'trace'
DELIVERY = ROOT / '.delivery'
BASE = '51e1e780111c712e43e1202e2b9f305111f3eaf3'
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')
if (DELIVERY / 'expected_files.json').is_file():
    expected = json.loads((DELIVERY / 'expected_files.json').read_text())
    archived = json.loads((DELIVERY / 'archived_files.json').read_text())
    save(TRACE / 'source_integrity.json', {'sources': expected, 'baseline': archived})
else:
    integrity = json.loads((TRACE / 'source_integrity.json').read_text())
    expected, archived = integrity['sources'], integrity['baseline']
for name, sha in {**expected, **archived}.items():
    assert digest(ROOT / name) == sha, 'Changed source or baseline: ' + name
baseline = json.loads((TRACE / 'baseline/configs/publication.json').read_text())
frozen = {'trace/baseline/' + name: sha for name, sha in baseline['frozen_results'].items()}
for name, sha in frozen.items():
    assert digest(ROOT / name) == sha, 'Frozen-result mismatch: ' + name
for row in json.loads((TRACE / 'source_cleanup.json').read_text()):
    assert digest(ROOT / row['file']) == row['clean_sha256']
    assert not re.search(r'^\s*%\s*\[', (ROOT / row['file']).read_text(), re.M)

def expand(path, language_root, stack=()):
    assert path not in stack, 'Cyclic TeX input'
    text = '\n'.join(line for line in path.read_text().splitlines() if not line.lstrip().startswith('%'))
    def insert(match):
        relative = match.group(1)
        candidate = language_root / relative
        if not candidate.suffix:
            candidate = candidate.with_suffix('.tex')
        assert candidate.is_file(), 'Missing TeX input: ' + str(candidate)
        assert candidate.resolve().is_relative_to(language_root.resolve())
        return expand(candidate, language_root, stack + (path,))
    return re.sub(r'\\input\{([^}]+)\}', insert, text)

citations = []
resource_count = 0
for language in ('en', 'zh'):
    folder = ROOT / language
    for name in ('manuscript', 'supplement', 'title_page'):
        text = expand(folder / (name + '.tex'), folder)
        for image in re.findall(r'\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}', text):
            assert (folder / image).is_file(), image
            resource_count += 1
        keys = re.findall(r'\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}', text)
        duplicates = [k for k, n in collections.Counter(keys).items() if n > 1]
        used = set()
        for group in re.findall(r'\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^}]+)\}', text):
            used.update(k.strip() for k in group.split(','))
        assert not duplicates and used == set(keys), (language, name, duplicates, used ^ set(keys))
        labels = re.findall(r'\\label\{([^}]+)\}', text)
        assert len(labels) == len(set(labels)), (language, name, 'duplicate labels')
        refs = set(re.findall(r'\\(?:ref|pageref|eqref)\{([^}]+)\}', text))
        assert refs <= set(labels), (language, name, 'missing labels', refs - set(labels))
        citations.append({'document': language + '/' + name, 'references': len(keys), 'citations_complete': True, 'labels_complete': True})

table_checks = []
for source in sorted((ROOT / 'en/tables').glob('*.tex')):
    other = ROOT / 'zh/tables' / source.name
    numbers = lambda s: re.findall(r'(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?', s)
    a, b = numbers(source.read_text()), numbers(other.read_text())
    assert a == b, 'Bilingual numeric mismatch: ' + source.name
    table_checks.append({'table': source.name, 'numeric_tokens': len(a), 'equal': True})
assert len(table_checks) == 14

local = {row['file']: row for row in json.loads((TRACE / 'local_pdf_checks.json').read_text())}
pdfs = []
for relative, previous in local.items():
    path = ROOT / relative
    assert path.is_file() and path.read_bytes().startswith(b'%PDF-')
    info = subprocess.check_output(['pdfinfo', str(path)], text=True)
    pages = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    text = subprocess.check_output(['pdftotext', '-layout', str(path), '-'], text=True)
    assert len(text.strip()) > 500
    normalized = ' '.join(unicodedata.normalize('NFKC', text).split())
    text_sha = hashlib.sha256(normalized.encode()).hexdigest()
    author = re.search(r'^Author:[ \t]*(.*)$', info, re.M)
    assert not author or not author.group(1).strip(), 'Identifying PDF author metadata'
    language, filename = relative.split('/')
    log = (ROOT / '.build' / language / filename.replace('.pdf', '.log')).read_text(errors='replace')
    issues = [line for line in log.splitlines() if re.search(r'Overfull \\[hv]box|Missing character:|(?:Citation|Reference) .*undefined|There were undefined|Label\(s\) may have changed|^!', line)]
    assert not issues, (relative, issues)
    warnings = [line.strip() for line in log.splitlines() if 'Warning:' in line]
    pdfs.append({'file': relative, 'bytes': path.stat().st_size, 'pages': pages, 'sha256': digest(path), 'normalized_text_sha256': text_sha, 'matches_local_pages': pages == previous['pages'], 'matches_local_normalized_text': text_sha == previous['normalized_text_sha256'], 'log_issues': issues, 'nonblocking_warnings': warnings})

# Preserve the actual checking script for traceability; it is not an analysis pipeline.
(TRACE / 'publication_check.py').write_bytes(Path(__file__).read_bytes())
report = {
    'checked_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'baseline_commit': BASE,
    'build_input_commit': os.environ.get('GITHUB_SHA', 'local'),
    'workflow_run_url': 'https://github.com/Timisic/autopsy/actions/runs/' + os.environ.get('GITHUB_RUN_ID', 'local'),
    'scope': 'Publication assembly and recompilation only. No new statistical analysis, model retraining, or human author approval.',
    'source_files_verified': len(expected),
    'baseline_files_preserved_byte_for_byte': len(archived),
    'frozen_results_verified': len(frozen),
    'frozen_result_mismatches': [],
    'tex_dependency_check': 'passed',
    'graphics_references_verified': resource_count,
    'bibliography_and_labels': citations,
    'bilingual_tables': table_checks,
    'pdfs': pdfs,
    'build_passes_per_document': 3,
    'compiler_version': subprocess.check_output(['xelatex', '--version'], text=True).splitlines()[0],
    'visual_review': 'Not newly performed on the remote renderer. The preceding delivery underwent visual review; normalized-text/page comparisons are reported separately.',
    'not_performed': ['Retraining or raw-data reproduction', 'New literature/full-text verification', 'Independent scientific peer review', 'Responsible human-author approval'],
    'author_controlled_items': ['Ethics and secondary-use authorization', 'Questionnaire scoring provenance', 'Authorship, funding and conflicts', 'Relationship to the previously published study'],
    'history_rewritten': False,
    'temporary_workflow': 'This check runs on an isolated publication branch. Workflow removal and promotion to main are separate, subsequent Git operations.'
}
save(TRACE / 'repository_checks.json', report)
allowed_roots = {'en', 'zh', 'trace'}
allowed_root_files = {'.gitattributes', '.gitignore', 'README.md', 'build.sh'}
files = sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and (p.relative_to(ROOT).parts[0] in allowed_roots or p.relative_to(ROOT).as_posix() in allowed_root_files))
assert not any(Path(p).suffix.lower() in {'.otf', '.ttf', '.woff', '.woff2', '.zip', '.aux', '.log', '.png', '.joblib', '.pkl'} for p in files)
assert len([p for p in files if p.endswith('.pdf')]) == 8
if 'trace/publication.json' not in files:
    files.append('trace/publication.json')
files.sort()
save(TRACE / 'publication.json', {'schema_version': 1, 'purpose': 'Clean bilingual LaTeX and PDFs with historical aggregate research trace', 'baseline_commit': BASE, 'files': files, 'languages': {'en': 'en', 'zh': 'zh'}, 'frozen_results': frozen})
assert all(row['matches_local_pages'] and row['matches_local_normalized_text'] for row in pdfs), 'Remote PDF differs from reviewed local text/pages; inspect before publishing'
print(json.dumps({'source_files': len(expected), 'archived_files': len(archived), 'frozen_results': len(frozen), 'table_pairs': len(table_checks), 'pdfs': [(r['file'], r['pages']) for r in pdfs], 'public_files': len(files)}, indent=2))
