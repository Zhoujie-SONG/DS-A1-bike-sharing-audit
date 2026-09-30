# Reproducibility

Executed OS: Windows-10-10.0.26200-SP0; Python 3.11.5. Package versions are recorded in requirements.txt, environment.yml and results/runtime_environment.json. Random seed: 42; bootstrap replicates: 2000. No complex machine learning model is used. This run reused the existing Python analysis stack plus a workspace-only copy of bundled ReportLab exposed by PYTHONPATH after network installation attempts were interrupted. The clean setup below installs the same direct versions normally and does not need that temporary copy. SciPy was considered but is not required: the bootstrap uses NumPy. The jupyter-core CLI, nbconvert, nbclient and ipykernel are used without the unnecessary full Jupyter metapackage. Requests was considered but acquisition uses Python's standard-library urllib. The single-command pipeline uses nbclient rather than relying on a shell-level kernel configuration.

From the project root:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate ; macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/download_data.py
python scripts/verify_data.py
python scripts/run_all.py
```

Notebook-only execution, also from the root:

```bash
python scripts/run_all.py --notebook-only
```

The one-command pipeline creates a temporary kernel specification pointing to its own Python executable, so an unrelated installed kernel is not silently selected. IPython history is confined to the temporary kernel directory; Windows uses the documented selector event loop for ZeroMQ. Paths inside project code and notebook are relative to the project root discovered from the script/notebook location, compatible with Windows/macOS/Linux. The PDF uses ReportLab and does not require TeX. Poppler or pypdfium2 can render pages for visual inspection; this run used bundled Poppler. Notebook uses UTF-8 and a fresh kernel, and warnings are not globally suppressed. A conventional nbconvert HTML preview was attempted but this Windows environment's certificate-store loading failed with an SSL error before conversion; an offline, read-only notebook-output HTML viewer was used instead. This does not affect the nbclient execution path.

Expected outputs: executed notebook, PDF, submission summary (150-300 English words), audit CSV/JSON, descriptive CSV, grouped means and bootstrap intervals, full weather x workingday x hour conditional table, audit/EDA/lineage PNGs, data card, dictionary, provenance, disclosure, QA records. Notebook code regenerates figures and results; run_all additionally generates the PDF and independently validates artifacts. Already-pinned raw data are hash-verified and reused without network access; first acquisition verifies the official webpage and ZIP. Changed hashes or failed validation return a nonzero exit code. Hash verification is on raw bytes, not platform-rewritten line endings.

Statistical method: Circular moving-block bootstrap of calendar days, block length 7; hour-weighted ratio of rental sums to observed row counts. The exact observed-period means do not need sampling intervals; reported intervals assess model-based resampling stability under approximate temporal assumptions. Fewer than 10 observed dates -> interval withheld. One-day cluster sensitivity is saved separately. No causal or external-population inference is justified.

The final quality check reruns the notebook from a fresh kernel, checks required files, figures and hash identity, compares canonical findings with notebook/PDF/README/summary, and records source/claim review. Semantic correctness remains inspectable in code; automated checks are not human verification. Install-time package resolution on another operating system may need platform-specific wheels even with exact direct versions.
