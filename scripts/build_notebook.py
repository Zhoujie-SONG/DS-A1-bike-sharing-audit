"""Create readable notebook cells with nbformat; all values appear at execution."""
from pathlib import Path
import nbformat as nbf

ROOT=Path(__file__).resolve().parents[1]

def main():
    cells=[]
    def md(s):cells.append(nbf.v4.new_markdown_cell(s))
    def code(s):cells.append(nbf.v4.new_code_cell(s))
    md('''# Data Provenance and Measurement Audit of the UCI Bike Sharing Dataset

DS-A1 | Descriptive, observational associations | Official UCI archive

This notebook evaluates data suitability before interpretation. All numeric findings are computed below and saved in machine-readable files. No raw observations are deleted or imputed. See the final computed takeaways for the audit and analytical findings.''')
    md('''## 1. Introduction
### 1.1 Research Question
How does hourly bike rental volume vary with weather conditions, working-day status, and hour of day in the 2011–2012 Capital Bikeshare data?
### 1.2 Stakeholder
Capital Bikeshare operations and planning team, using historical patterns as an operating-analysis reference. The data do not directly identify optimal dispatch.
### 1.3 Population
Capital Bikeshare system-hours during the 2011–2012 observation period that the dataset is intended to represent.
### 1.4 Sample
The actual hourly observations in `hour.csv`. The exact row count is calculated after loading.
### 1.5 Unit of Analysis
One Capital Bikeshare system-hour: one date and recorded clock hour.
### 1.6 Target
`cnt`, the total rental count including `casual` and `registered`; the identity is tested below.
### 1.7 Estimand
The conditional mean hourly rental count across weather conditions, working-day status, and hour of day within the observed 2011–2012 Capital Bikeshare period:
$$E[\mathrm{cnt}\mid\mathrm{weathersit},\mathrm{workingday},\mathrm{hr}].$$
This is an associational estimand among observed system-hours. Unobserved combinations do not have an estimated mean.
### 1.8 Scope and Boundary
No weather causal effects, universal city comparisons, 2026 extrapolation, complex prediction models or perfect latent-demand measurement are claimed. Missing rows can restrict population coverage.

### Key Assumptions
Counts refer to recorded system-hours. Calendar parsing is reliable; weekday encoding must be investigated because official definitions omit its mapping. The nominal 24-hour grid is an audit device rather than a timezone-resolved exposure measure. Bootstrap intervals require approximate temporal-resampling assumptions, not random sampling from all cities.''')
    md('### Setup and immutable input verification')
    code('''from pathlib import Path
import sys, json
import pandas as pd
import numpy as np
from IPython.display import display, Markdown, Image
pd.set_option('display.max_colwidth', None)
ROOT = Path.cwd().resolve()
if not (ROOT / "data/raw/hour.csv").exists():
    ROOT = ROOT.parent
assert (ROOT / "scripts/analysis.py").exists(), "Execute from project root or notebooks directory"
sys.path.insert(0, str(ROOT / "scripts"))
import analysis as a
RANDOM_SEED = 42
assert a.RANDOM_SEED == RANDOM_SEED
df, day, metadata, dictionary = a.load_data()
print(f"Sample: {len(df):,} system-hours; {len(df.columns)} raw columns; {len(day)} daily rows")
display(df.head(5))''')
    md('''## 2. Dataset Provenance
The original source is Capital Bikeshare's 2011–2012 historical transaction log. Hadi Fanaee-T / LIAAD aggregated hourly and daily counts and added Freemeteo weather and calendar information, according to the archived README. UCI publishes the archive. This project uses the downloaded ZIP and unchanged extracted files, identified by SHA-256.

Original feeds, exact exclusions, weather alignment, timezone and daylight-saving handling have not been independently reconstructed. Official-page and archive disagreements are audit findings, not silently reconciled definitions.

Source: [UCI Bike Sharing](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). Dataset citation: Fanaee-T (2013), [DOI 10.24432/C5W894](https://doi.org/10.24432/C5W894). License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), independently checked in the saved official-page HTML. Archive README requests attribution to Fanaee-T and Gama (2013), [paper DOI 10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).''')
    code('''display(Markdown(f"**Downloaded:** {metadata['download_datetime_utc']}  \\n**Observed dates:** {metadata['observation_start']} to {metadata['observation_end']}  \\n**Creator:** {metadata['creator']}  \\n**Repository:** {metadata['repository']}  \\n**DOI:** {metadata['doi']}  \\n**License:** {metadata['license']}"))
display(pd.DataFrame(metadata['files']).T[['size_bytes', 'sha256']])''')
    md('''## 3. Data-generating Process
The lineage distinguishes documented aggregation from possible measurement mechanisms. Realized rentals may differ from latent demand. Supply constraints in the diagram are conceptual; these files do not establish that they occurred.''')
    code('''a.dgp_figure()
display(Image(filename=str(ROOT / 'results/figures/00_dgp_lineage.png'), width=760))''')
    md('''## 4. Schema, Range, Missingness and Duplicate Audit
Audit definitions are documented in `docs/data_dictionary.csv` and implemented in `scripts/analysis.py`. All fields are checked; counts have no invented maximum. Zero boundary values are inspected separately from true nulls. Exact and date-hour semantic duplicates are both checked. Failed range samples are saved, not erased.''')
    code('''summary, audit_results = a.audit(df, day, metadata, dictionary)
display(pd.Series(summary).drop(['weekday_mapping_evidence','zero_counts','source_document_conflicts']))
display(audit_results.query("check_category == 'range'")[['variable','expected','status','invalid_row_count']])''')
    md('### Missingness and key completeness')
    code('''display(df.isna().sum().rename('missing_cells').to_frame())
display(pd.read_csv(ROOT / 'results/missingness.csv'))
display(audit_results.query("check_category in ['duplicates','coverage','provenance']")[['check_name','observed','status','notes']])
print('All raw rows retained:', len(df) == summary['retained_rows'])''')
    md('''## 5. Internal Consistency
Test the count identity, parsed year/month, working-day rule, empirical weekday mapping, record-index sequence and daily/hourly rental totals. Neither source specifies weekday code mapping; all cyclic candidates are tested rather than guessing a documented mapping. Working-day consistency uses calendar weekdays directly.''')
    code('''display(audit_results.query("check_category == 'consistency'")[['check_name','observed','status','notes']])
display(pd.Series(summary['weekday_mapping_evidence'],name='mismatches_by_offset'))
assert (df.cnt == df.casual + df.registered).all()''')
    md('''## 6. Leakage Audit
If `cnt` is a prediction target, `casual` and `registered` are deterministic target leakage because they sum to the target. They must be excluded from predictors. The identifier `instant` is not a meaningful deployable feature. Random temporal splits and same-hour observed weather require separate timing review. The current task is descriptive and trains no model.''')
    code('''display(audit_results.query("check_category == 'leakage'")[['check_name','observed','status','notes']])
predictor_candidates = [c for c in df.columns if c not in ['cnt','casual','registered','instant','dteday']]
print('Descriptive calendar/weather candidates:', predictor_candidates)''')
    md('''## 7. Anomaly Audit
IQR flags are statistical flags, not confirmed errors. Inspect quantiles, histograms, boxplots, largest counts and zero counts. Possible calendar/weather contexts are examined without attributing extreme counts to an unverified event. All observations remain in the main analysis.''')
    code('''descriptive = a.describe(df)
display(descriptive.round(3))
display(pd.read_csv(ROOT / 'results/anomaly_flags.csv').round(3))
display(df.nlargest(10, 'cnt')[['dteday','hr','workingday','season','weathersit','cnt','casual','registered']])
display(df.loc[df.cnt.eq(0)])''')
    md('''## 8. Transparent Statistical Summaries
Group means, medians, SD and observed support are computed for weather, working-day status, hour, hour x workingday and the complete observed weather x workingday x hour cells. This directly estimates the stated conditional mean; marginal plots are supplementary.

Use 2,000 seeded circular moving-block resamples of seven consecutive calendar days, then recompute rental-sum / observed-hour-count ratios. This preserves within-block dependence and observed-hour weighting. Pointwise percentile 95% intervals describe temporal resampling stability of observed-period summaries. Exact finite-period descriptive means do not require sampling intervals. The bootstrap assumes approximate stability and does not fully preserve seasonality or system growth. One-day cluster intervals are saved as a sensitivity comparison. Withhold intervals below 10 observed dates or insufficient finite resamples. No causal test or external-population confidence is implied.''')
    code('''tables, workingday_difference = a.inference(df)
display(tables['weather'].round(3))
display(tables['workingday'].round(3))
display(pd.Series(workingday_difference))
display(tables['hour'].round(3))
print('Observed conditional cells:', len(tables['conditional']))
display(tables['conditional'].head(12).round(3))''')
    md('''## 9. Exploratory Analysis
Axes use completed rentals per system-hour; weather definitions are composite categories. Missing weather-hour combinations remain blank. No plot implies causation.''')
    code('''a.figures(df, tables)
computed_findings = a.findings(df, summary, tables, workingday_difference)
text = a.write_docs(df, metadata, computed_findings)''')
    for name,caption,key in [('01_count_distribution.png','Figure 1. Count distribution','anomaly'),('02_hour_workingday.png','Figure 2. Hourly working-day profiles','time'),('03_weather.png','Figure 3. Weather associations','weather'),('04_workingday_distribution.png','Figure 4. Working-day count distributions','time'),('05_hour_weather.png','Figure 5. Hour x weather means','coverage'),('06_audit_boxplots.png','Audit boxplots','anomaly'),('07_audit_histograms.png','Audit histograms','anomaly')]:
        md('### '+caption)
        code(f"display(Image(filename=str(ROOT / 'results/figures/{name}'), width=820))\ndisplay(Markdown(text['{key}']))")
    md('''## 10. Measurement Counterexample
This is a conceptual example, not a reconstructed historical incident.''')
    code("display(Markdown(text['measurement']))")
    md('## 11. Bias and Limitations')
    code("display(Markdown(text['bias']))\ndisplay(Markdown(text['coverage']))\ndisplay(pd.read_csv(ROOT / 'results/humidity_zero_sensitivity.csv').round(3))")
    md('''## 12. Prohibited Claims
### Claim 1
We must not claim that weather conditions causally determine bike rental demand based on this observational dataset. Weather is not randomly assigned and calendar/season/hour confounding is unaddressed.
### Claim 2
We must not generalize the observed relationships to all cities, all bike-sharing systems, or current populations. The sample is historical and system-specific.
### Claim 3
Observed rental counts should not be interpreted as a perfect measurement of unconstrained latent demand. Supply constraints and unfulfilled intentions are unmeasured.''')
    md('## 13. Computed Takeaways and Conclusion')
    code("display(Markdown(text['audit']))\ndisplay(Markdown(text['weather']))\ndisplay(Markdown(text['time']))\ndisplay(Markdown(text['leakage']))\ndisplay(Markdown(text['conclusion']))")
    md('''## 14. Reproducibility and AI Use
Seed 42; all code lives in this repository and uses project-relative paths. Raw hashes are rechecked below. `python scripts/run_all.py` executes a fresh kernel, generates the formal ReportLab PDF and validates artifacts; see `docs/reproducibility.md` for exact environment versions and commands. Statistical results and prose are regenerated from shared canonical findings.

OpenAI Codex assisted with code, analysis, prose, plots, PDF and validation. No second human review is asserted. Implementation choices and the distinction between code checks and Codex visual review are disclosed in `docs/ai_use_log.md`.''')
    code('''from verify_data import verify
verify()
assert summary['row_count'] == len(df)
assert summary['missing_cells'] == int(df.isna().sum().sum())
assert summary['cnt_identity_failures'] == int((df.cnt != df.casual + df.registered).sum())
print('Notebook finished: all cells executed sequentially; source bytes unchanged.')''')
    nb=nbf.v4.new_notebook(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'}})
    nbf.validate(nb)
    nbf.write(nb,ROOT / 'notebooks/DS_A1_Bike_Sharing_Audit.ipynb')

if __name__=='__main__':main()
