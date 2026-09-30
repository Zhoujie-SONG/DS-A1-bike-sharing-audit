"""One command: acquire/verify -> fresh notebook -> PDF -> independent QA."""
from pathlib import Path
import sys
import os
import json
import tempfile
import subprocess
import asyncio
import nbformat
from nbclient import NotebookClient

ROOT=Path(__file__).resolve().parents[1]

def execute_notebook():
    path=ROOT/'notebooks/DS_A1_Bike_Sharing_Audit.ipynb'
    nb=nbformat.read(path,as_version=4)
    for cell in nb.cells:
        if cell.cell_type=='code':cell.outputs=[];cell.execution_count=None
    with tempfile.TemporaryDirectory(prefix='ds-a1-kernel-') as temp:
        kernel=Path(temp)/'kernels/ds-a1-python';kernel.mkdir(parents=True)
        (kernel/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-Xfrozen_modules=off','-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'DS-A1 current Python','language':'python'}),encoding='utf-8')
        old=os.environ.get('JUPYTER_PATH')
        old_ipython=os.environ.get('IPYTHONDIR')
        os.environ['JUPYTER_PATH']=temp+(os.pathsep+old if old else '')
        os.environ['IPYTHONDIR']=str(Path(temp)/'ipython')
        if sys.platform=='win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        try:
            client=NotebookClient(nb,timeout=600,kernel_name='ds-a1-python',resources={'metadata':{'path':str(ROOT)}},allow_errors=False)
            client.execute()
        finally:
            if old is None:os.environ.pop('JUPYTER_PATH',None)
            else:os.environ['JUPYTER_PATH']=old
            if old_ipython is None:os.environ.pop('IPYTHONDIR',None)
            else:os.environ['IPYTHONDIR']=old_ipython
    nb.metadata.kernelspec={'name':'python3','display_name':'Python 3','language':'python'}
    nbformat.validate(nb)
    nbformat.write(nb,path)
    print('PASS: notebook executed from a fresh kernel.',flush=True)

def main():
    from download_data import main as download
    download()
    if not (ROOT/'notebooks/DS_A1_Bike_Sharing_Audit.ipynb').exists():
        from build_notebook import main as build
        build()
    execute_notebook()
    if '--notebook-only' in sys.argv:
        return
    from report import main as report
    report()
    from validate_project import main as validate
    validate()
    print('PASS: full pipeline completed.',flush=True)

if __name__=='__main__':main()
