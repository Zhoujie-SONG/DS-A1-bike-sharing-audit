"""Fail explicitly if any pinned source bytes change."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]

def verify():
    raw = ROOT / 'data/raw'
    meta = json.loads((raw / 'source_metadata.json').read_text(encoding='utf-8'))
    for name, record in meta['files'].items():
        p = raw / name
        assert p.stat().st_size == record['size_bytes'], f'Size mismatch: {name}'
        assert hashlib.sha256(p.read_bytes()).hexdigest() == record['sha256'], f'Hash mismatch: {name}'
    print('PASS: all pinned source hashes and sizes verified.')
    return meta

if __name__ == '__main__':
    verify()
