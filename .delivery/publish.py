"""Stage only the reviewed publication, verify committed bytes, then push the work branch."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

root = Path.cwd()
def git(*args):
    return subprocess.check_output(['git', *args])
integrity = json.loads((root / 'trace/source_integrity.json').read_text())
manifest = json.loads((root / 'trace/publication.json').read_text())
report_path = root / 'trace/repository_checks.json'
report = json.loads(report_path.read_text())
expected = {**integrity['sources'], **integrity['baseline'], **manifest['frozen_results']}
expected.update({row['file']: row['sha256'] for row in report['pdfs']})
shutil.rmtree(root / '.delivery')
git('add', '-A')
tracked = set(git('ls-files', '-z').decode().strip('\0').split('\0'))
temporary = {'.github/workflows/publish-clean-manuscript.yml'}
assert tracked == set(manifest['files']) | temporary, ('Tracked allowlist mismatch', tracked ^ (set(manifest['files']) | temporary))
for name, digest in expected.items():
    assert hashlib.sha256(git('show', ':' + name)).hexdigest() == digest, 'Staging changed bytes: ' + name
report['git_index_check'] = {'verified_files': len(expected), 'all_expected_bytes_match': True, 'tracked_allowlist_matches': True, 'temporary_workflow_pending_removal': list(temporary)}
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
git('add', 'trace/repository_checks.json')
git('config', 'user.name', 'github-actions[bot]')
git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
print(git('commit', '-m', 'Publish clean bilingual LaTeX and PDF manuscripts; archive research trace').decode())
print(git('push', 'origin', 'HEAD:publish/clean-manuscript-20260924').decode())
