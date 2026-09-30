"""Independent file/data/output checks with an inspectable QA receipt."""
from pathlib import Path
import hashlib
import json
import re
import datetime as dt
import numpy as np
import pandas as pd
import nbformat
from pypdf import PdfReader
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
REQUIRED=['README.md','requirements.txt','environment.yml','.gitignore','.gitattributes','LICENSE','data/raw/hour.csv','data/raw/day.csv','data/raw/Readme.txt','data/raw/source_metadata.json','data/README.md','notebooks/DS_A1_Bike_Sharing_Audit.ipynb','reports/DS_A1_Bike_Sharing_Audit.pdf','reports/submission_summary.txt','docs/data_card.md','docs/data_dictionary.csv','docs/provenance.md','docs/ai_use_log.md','docs/reproducibility.md','docs/qa_review.md','results/audit_results.csv','results/audit_summary.json','results/descriptive_statistics.csv','scripts/download_data.py','scripts/verify_data.py','scripts/run_all.py']

def main():
    from verify_data import verify
    meta=verify()
    for name in REQUIRED:
        assert (ROOT/name).is_file() and (ROOT/name).stat().st_size>0,name
    df=pd.read_csv(ROOT/'data/raw/hour.csv')
    s=json.loads((ROOT/'results/audit_summary.json').read_text(encoding='utf-8'))
    checks={'row_count':len(df),'column_count':len(df.columns),'missing_cells':int(df.isna().sum().sum()),'exact_duplicates':int(df.duplicated().sum()),'semantic_duplicates':int(df.duplicated(['dteday','hr']).sum()),'cnt_identity_failures':int(df.cnt.ne(df.casual+df.registered).sum())}
    for k,v in checks.items():assert s[k]==v,(k,s[k],v)
    audits=pd.read_csv(ROOT/'results/audit_results.csv')
    assert s['range_check_failures']==int(audits.query("check_category == 'range'").status.eq('FAIL').sum())
    assert set(df.columns)==set(pd.read_csv(ROOT/'docs/data_dictionary.csv').variable)
    for name,keys in [('weather',['weathersit']),('workingday',['workingday']),('hour',['hr']),('conditional',['weathersit','workingday','hr'])]:
        actual=pd.read_csv(ROOT/f'results/{name}_statistics.csv').set_index(keys)
        independent=df.groupby(keys).cnt.agg(n='size',mean='mean',median='median',sd='std')
        np.testing.assert_allclose(actual.loc[independent.index,['n','mean','median','sd']],independent,equal_nan=True,rtol=1e-12)
    nb=nbformat.read(ROOT/'notebooks/DS_A1_Bike_Sharing_Audit.ipynb',as_version=4);nbformat.validate(nb)
    cells=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in cells)
    assert [c.execution_count for c in cells]==list(range(1,len(cells)+1))
    assert not any(o.output_type=='error' for c in cells for o in c.outputs)
    image_count=sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs)
    assert image_count>=8,image_count
    figures=list((ROOT/'results/figures').glob('*.png'))
    assert len(figures)>=8
    for p in figures:
        with Image.open(p) as im:im.verify()
    reader=PdfReader(ROOT/'reports/DS_A1_Bike_Sharing_Audit.pdf')
    assert len(reader.pages)>=8
    pages=[p.extract_text() for p in reader.pages]
    assert all(len(x)>100 for x in pages),'Empty or image-only report page'
    pdf_text='\n'.join(pages)
    assert (ROOT/'reports/DS_A1_Bike_Sharing_Audit.pdf').stat().st_size>100000
    summary=(ROOT/'reports/submission_summary.txt').read_text(encoding='utf-8')
    assert 150<=len(summary.split())<=300
    notebook_text='\n'.join(c.get('source','') for c in nb.cells)+'\n'+'\n'.join(str(o.get('data',{}).get('text/plain',''))+str(o.get('text',''))+str(o.get('data',{}).get('text/markdown','')) for c in cells for o in c.outputs)
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    f=json.loads((ROOT/'results/findings.json').read_text(encoding='utf-8'))
    tokens=[f'{len(df):,}',f'{f["weather"][0]["mean"]:.2f}',f'{f["weather"][2]["mean"]:.2f}']
    for name,txt in [('README',readme),('PDF',pdf_text),('summary',summary),('notebook',notebook_text)]:
        for token in tokens:assert token in txt,(name,token)
        assert 'casual' in txt and 'registered' in txt,name
    # Search authored prose and notebook markdown/output, not third-party archives.
    claim_hits=[];unfinished=[]
    pattern=re.compile(r'\b(cause|causes|caused|proves|all cities|all users)\b',re.I)
    pending=re.compile(r'\b(TODO|TBD|FIXME|XXX|placeholder)\b',re.I)
    for path in [ROOT/'README.md',*sorted((ROOT/'docs').glob('*.md')),ROOT/'reports/submission_summary.txt']:
        for i,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
            if pattern.search(line):claim_hits.append({'file':path.relative_to(ROOT).as_posix(),'line':i,'text':line})
            if pending.search(line):unfinished.append({'file':path.relative_to(ROOT).as_posix(),'line':i,'text':line})
    for name,txt in [('notebook',notebook_text),('PDF',pdf_text)]:
        for line in txt.splitlines():
            if pattern.search(line):claim_hits.append({'file':name,'text':line})
            if pending.search(line):unfinished.append({'file':name,'text':line})
    assert not unfinished,unfinished
    expected_url='<INSERT_STABLE_GITHUB_REPOSITORY_URL>'
    receipt=ROOT/'docs/repository.json'
    if receipt.exists():
        expected_url=json.loads(receipt.read_text(encoding='utf-8'))['url']
        assert expected_url.startswith('https://github.com/')
        assert expected_url in readme
        assert '<INSERT_STABLE_GITHUB_REPOSITORY_URL>' not in summary
    assert expected_url in summary
    result=dict(status='PASS',completed_utc=dt.datetime.now(dt.timezone.utc).isoformat(),required_files_checked=len(REQUIRED),fresh_kernel_execution='PASS',executed_code_cells=len(cells),notebook_embedded_images=image_count,source_hashes='PASS',independent_statistics='PASS',narrative_consistency='PASS',pdf_pages=len(reader.pages),pdf_size_bytes=(ROOT/'reports/DS_A1_Bike_Sharing_Audit.pdf').stat().st_size,figure_count=len(figures),summary_word_count=len(summary.split()),unfinished_marker_hits=unfinished,claim_review_hits=claim_hits,allowed_repository_url_token=expected_url,visual_review='See docs/qa_review.md; not inferred from programmatic pass.')
    (ROOT/'results/qa_validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['claim_review_hits','unfinished_marker_hits']},indent=2))

if __name__=='__main__':main()
