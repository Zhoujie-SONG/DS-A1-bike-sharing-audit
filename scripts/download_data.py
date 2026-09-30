"""Acquire immutable source bytes and a verified official-page snapshot."""
from pathlib import Path
import datetime as dt
import hashlib
import json
import re
import urllib.request
import zipfile
import io
import csv

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw'
PAGE = 'https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset'
ZIP_URL = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip'

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def fetch(url):
    request = urllib.request.Request(url, headers={'User-Agent': 'DS-A1-academic-audit/1.0'})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read(), response.geturl(), dict(response.headers)

def main():
    RAW.mkdir(parents=True, exist_ok=True)
    if (RAW / 'source_metadata.json').exists():
        from verify_data import verify
        verify()
        print('Existing pinned source verified; no overwrite.')
        return
    page, page_url, page_headers = fetch(PAGE)
    html = page.decode('utf-8')
    assert '10.24432/C5W894' in html, 'DOI not verified on official page'
    assert 'creativecommons.org/licenses/by/4.0' in html, 'License not verified on official page'
    (RAW / 'uci_official_page.html').write_bytes(page)
    blob, resolved, headers = fetch(ZIP_URL)
    archive = RAW / 'Bike-Sharing-Dataset.zip'
    archive.write_bytes(blob)
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        for filename in ['hour.csv', 'day.csv', 'Readme.txt']:
            candidates = [n for n in z.namelist() if Path(n).name == filename]
            assert len(candidates) == 1, (filename, candidates)
            (RAW / filename).write_bytes(z.read(candidates[0]))
    with (RAW / 'hour.csv').open(newline='', encoding='utf-8') as f:
        dates = [r['dteday'] for r in csv.DictReader(f)]
    names = ['hour.csv', 'day.csv', 'Readme.txt', archive.name, 'uci_official_page.html']
    metadata = {
        'dataset_name': 'Bike Sharing', 'creator': 'Hadi Fanaee-T',
        'repository': 'UCI Machine Learning Repository', 'doi': '10.24432/C5W894',
        'license': 'CC BY 4.0', 'license_url': 'https://creativecommons.org/licenses/by/4.0/',
        'official_page_url': PAGE, 'resolved_page_url': page_url,
        'download_url': ZIP_URL, 'resolved_download_url': resolved,
        'download_datetime_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'download_date_asia_singapore': dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat(),
        'http_last_modified': headers.get('Last-Modified'),
        'version_policy': 'No official semantic version; pin downloaded ZIP and extracted bytes with SHA-256.',
        'observation_start': min(dates), 'observation_end': max(dates),
        'doi_license_verification': 'Checked DOI text and official CC BY 4.0 link in saved UCI HTML.',
        'files': {n: {'size_bytes': (RAW / n).stat().st_size, 'sha256': sha256(RAW / n)} for n in names}
    }
    (RAW / 'source_metadata.json').write_text(json.dumps(metadata, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(metadata, indent=2))

if __name__ == '__main__':
    main()
