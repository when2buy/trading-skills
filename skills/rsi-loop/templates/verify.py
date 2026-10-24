"""Re-check script for one research round: read-only, no network, no GPU.

Usage: python3 verify.py
Checks that every evidence file listed in ARTIFACTS.json exists, with matching size and
sha256, no path escapes, and no file types that must not enter the repo. Prints OK, or fails.

Generate ARTIFACTS.json: python3 verify.py --write <file-or-dir> ...
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / 'ARTIFACTS.json'
BLOCKED = {'.npz', '.npy', '.pt', '.pth', '.safetensors', '.bin', '.so', '.o', '.zip', '.raw', '.trace', '.pyc'}
MAX_BYTES = 1 << 20  # files > 1 MB stay out of the repo; keep a summary only


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(targets):
    files = []
    for t in targets:
        p = (HERE / t).resolve()
        for f in sorted([p] if p.is_file() else p.rglob('*')):
            if not f.is_file() or f.name in ('ARTIFACTS.json', 'verify.py'):
                continue
            rel = f.relative_to(HERE).as_posix()
            assert f.suffix not in BLOCKED, f'file type must not enter the repo: {rel}'
            assert f.stat().st_size <= MAX_BYTES, f'file over 1 MB; keep a summary only: {rel}'
            files.append({'path': rel, 'bytes': f.stat().st_size, 'sha256': sha256(f)})
    MANIFEST.write_text(json.dumps({'files': files}, ensure_ascii=False, indent=1) + '\n')
    print(f'wrote {len(files)} files to {MANIFEST.name}')


def verify():
    rows = json.loads(MANIFEST.read_text())['files']
    for row in rows:
        rel = PurePosixPath(row['path'])
        assert not rel.is_absolute() and '..' not in rel.parts, rel
        path = HERE / str(rel)
        assert path.resolve().is_relative_to(HERE) and not path.is_symlink(), rel
        assert path.suffix not in BLOCKED, rel
        raw = path.read_bytes()
        assert len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'], rel
    # Add round-specific checks here, e.g. numbers in the conclusion table match the result files,
    # or the previous round's ARTIFACTS.json is unchanged.
    print(f'OK {len(rows)} files')


if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[1] == '--write':
        write(sys.argv[2:])
    else:
        verify()
