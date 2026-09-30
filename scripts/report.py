"""A formal report from executed canonical results; no TeX or notebook screenshots."""
from pathlib import Path
import json
import html
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[1]

def main():
    f=json.loads((ROOT/'results/findings.json').read_text(encoding='utf-8'))
    s=f['summary'];meta=json.loads((ROOT/'data/raw/source_metadata.json').read_text(encoding='utf-8'))
    # Keep rendering standalone: importing analysis would unnecessarily require plotting.
    from analysis import narrative
    text=narrative(f)
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyAudit',fontName='Helvetica',fontSize=10.2,leading=14.6,spaceAfter=9,textColor=colors.HexColor('#243444')))
    styles.add(ParagraphStyle(name='CaptionAudit',fontName='Helvetica',fontSize=8.5,leading=11,spaceAfter=8,textColor=colors.HexColor('#596673')))
    styles.add(ParagraphStyle(name='CellAudit',fontName='Helvetica',fontSize=8.4,leading=11))
    styles.add(ParagraphStyle(name='MonoAudit',fontName='Courier',fontSize=7,leading=9))
    styles['Title'].fontName='Helvetica-Bold';styles['Title'].fontSize=25;styles['Title'].leading=30;styles['Title'].alignment=TA_LEFT;styles['Title'].textColor=colors.HexColor('#355C7D')
    styles['Heading1'].fontSize=17;styles['Heading1'].leading=21;styles['Heading1'].textColor=colors.HexColor('#355C7D')
    story=[]
    def p(txt,style='BodyAudit'):
        safe=html.escape(str(txt)).replace('2011–2012','2011-2012')
        story.append(Paragraph(safe,styles[style]))
    def h(txt):story.append(Paragraph(html.escape(txt),styles['Heading1']))
    def sub(txt):story.append(Paragraph(html.escape(txt),styles['Heading2']))
    def page():story.append(PageBreak())
    def table(data,widths=None):
        items=[[Paragraph(html.escape(str(x)),styles['CellAudit']) for x in row] for row in data]
        t=Table(items,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0F5')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#243444')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.6,colors.HexColor('#B8C7D4')),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#DAE0E5')),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6)]))
        story.append(t);story.append(Spacer(1,10))
    def image(name,max_height=220):
        path=ROOT/'results/figures'/name
        w,hgt=ImageReader(str(path)).getSize();scale=min(491/w,max_height/hgt)
        story.append(Image(str(path),width=w*scale,height=hgt*scale,hAlign='CENTER'));story.append(Spacer(1,7))
    p('DS-A1 | DATA PROVENANCE AND MEASUREMENT AUDIT','CaptionAudit')
    p('Data Provenance and Measurement Audit of the UCI Bike Sharing Dataset','Title')
    p('Capital Bikeshare | 2011-2012 | Official UCI archive','Heading2')
    p('Research question: '+__import__('analysis').QUESTION)
    h('Executive summary')
    p(text['audit']);p(text['weather']);p(text['time'])
    p('Verdict: suitable for bounded descriptive associations among observed system-hours. Coverage gaps, source-definition conflicts, sparse weather cells and measurement constraints remain material. Causal inference and present-day operational optimization are outside scope.')
    h('Research objects')
    table([['Object','Definition'],['Stakeholder','Capital Bikeshare operations and planning team; historical operational reference.'],['Population','Capital Bikeshare system-hours during the 2011-2012 observation period that the dataset is intended to represent.'],['Sample / unit',f'{s["row_count"]:,} observed rows; one Capital Bikeshare system-hour per row.'],['Target','cnt: total completed rentals; casual + registered.'],['Estimand','Conditional mean E[cnt | weathersit, workingday, hr], for observed combinations.']], [95,396])
    page();h('Dataset and provenance')
    p('Creator: Hadi Fanaee-T. Repository: UCI Machine Learning Repository. The archived README traces the source to Capital Bikeshare system logs in Washington, D.C., aggregation by the creator into hourly/daily counts, Freemeteo weather information and calendar annotations. Original feed extraction and exact weather alignment were not reconstructed by this audit.')
    p('Dataset DOI: 10.24432/C5W894. License: CC BY 4.0, verified via the official-page license link. The archived README additionally asks for citation of Fanaee-T and Gama (2013), Event labeling combining ensemble detectors and background knowledge, DOI 10.1007/s13748-013-0040-3.')
    p('Observed period: '+meta['observation_start']+' to '+meta['observation_end']+'. Download: '+meta['download_datetime_utc']+' (Singapore date '+meta['download_date_asia_singapore']+'). No official semantic version is specified; exact bytes define the analyzed version.')
    sub('Pinned file hashes')
    for name in ['hour.csv','day.csv','Readme.txt','Bike-Sharing-Dataset.zip']:
        r=meta['files'][name];p(f'{name} | {r["size_bytes"]:,} bytes','CaptionAudit');p(r['sha256'],'MonoAudit')
    sub('Source disagreements')
    p(f'The webpage reports 17,389 instances; the pinned CSV and archive README show {s["row_count"]:,}. Season labels also disagree between the page and archive. Temperature/feeling-temperature definitions differ between min-max normalization on the current page and divisor normalization in the archive. The audit uses numeric season codes and normalized values; no Celsius conversion is asserted.')
    p('Weekday is described as day of the week, without numeric mapping in either source. All seven cyclic mappings were tested: Sunday=0 fits every row empirically. This is an empirical diagnostic, not an independently documented code definition.')
    p('Official page: https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset','CaptionAudit')
    p('Official ZIP: https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip','CaptionAudit')
    page();h('Data-generating process')
    image('00_dgp_lineage.png',510)
    p('The aggregation and weather source are documented in the raw README. The relationships involving latent demand and supply are a conceptual measurement framework. Exact collection exclusions, original transaction-level processing, clock timezone and daylight-saving treatment are not documented sufficiently to reconstruct them. This audit preserves that uncertainty.')
    page();h('Audit results and data suitability')
    table([['Check','Executed finding','Meaning'],['Schema',f'{s["row_count"]:,} x {s["column_count"]}; no unexpected/missing columns','Raw schema and dictionary align.'],['Missing cells',str(s['missing_cells']),'Across all raw columns; no blank/text sentinel detected.'],['Exact / semantic duplicates',f'{s["exact_duplicates"]} / {s["semantic_duplicates"]}','Candidate natural key: date + hour.'],['Range',f'{s["range_check_failures"]} failed checks','Discrete, normalized and count/date domains tested.'],['Count identity',f'{s["cnt_identity_satisfied"]:,} satisfy; {s["cnt_identity_failures"]} fail','cnt = casual + registered.'],['Other consistency',str(s['internal_consistency_failures'])+' failures','Year, month, empirical weekday, workingday, index and day/hour totals.'],['Coverage',f'{s["absent_nominal_hours"]} absent of {s["nominal_hours"]:,} nominal labels','Observation coverage differs from cell missingness.'],['Leakage','DETECTED','Outcome components must be excluded from predictors.']], [115,155,221])
    p(text['coverage'])
    sub('Anomaly interpretation')
    p(text['anomaly'])
    flags=pd.read_csv(ROOT/'results/anomaly_flags.csv')
    table([['Variable','IQR flags','Zero rows']]+[[r.variable,int(r.flagged_rows),int(r.zero_rows)] for _,r in flags.iterrows()], [180,155,156])
    p('The largest 20 count records and their hour/workingday/season/weather contexts are preserved in CSV. No unsupported historical-event attribution is made. Zero humidity sensitivity and one-day bootstrap sensitivity are available alongside the main results.','CaptionAudit')
    page();h('Exploratory analysis: distribution and hour')
    image('01_count_distribution.png',220)
    p('Counts are right-skewed; high-use hours are retained rather than removed solely by an IQR rule. The unit is completed rentals per recorded system-hour.','CaptionAudit')
    image('02_hour_workingday.png',245)
    p(text['time'])
    p('Bands are pointwise 95% seven-day moving-block bootstrap intervals. The shape difference contains more information than the marginal working-day mean difference.','CaptionAudit')
    page();h('Exploratory analysis: weather')
    image('03_weather.png',270)
    rows=[['Weather','n hours / days','Mean','Median / SD','95% interval']]
    for r in f['weather']:
        ci='Withheld' if r['ci_low'] is None else f'{r["ci_low"]:.2f} to {r["ci_high"]:.2f}'
        rows.append([f'Code {r["weathersit"]}',f'{r["n"]:,} / {r["n_days"]}',f'{r["mean"]:.2f}',f'{r["median"]:.2f} / {r["sd"]:.2f}',ci])
    table(rows,[80,100,65,105,141]);p(text['weather'])
    sub('Inference boundary')
    p('Use 2,000 circular moving-block resamples of seven consecutive calendar days, fixed seed 42 (seed offset by block length in code), preserving observed-hour weighting. Intervals are percentile 95%, pointwise rather than simultaneous. They describe temporal resampling stability under approximate assumptions; exact finite-period means are descriptive. Seven-day blocks do not preserve all seasonal dependence or system growth. No probability-sampling or causal interpretation is warranted.')
    p('Intervals are withheld below 10 observed days or below 95% finite resamples. One-day cluster sensitivity is saved. Weather categories combine multiple conditions and do not identify a single physical treatment.','CaptionAudit')
    page();h('Working-day and interaction patterns')
    image('04_workingday_distribution.png',225)
    image('05_hour_weather.png',250)
    p('The interaction plot summarizes observed weather-hour means, with unobserved combinations left blank. The complete weather x workingday x hour table in results/conditional_statistics.csv directly estimates the stated estimand. Each cell records n, observed dates, mean, median, SD and interval status. Sparse cells restrict the supported question; marginal weather patterns can reflect different calendar compositions.')
    page();h('Leakage and measurement validity')
    sub('Deterministic target leakage')
    p(text['leakage'])
    sub('Observed rentals versus latent demand')
    p(text['measurement'])
    sub('Bias and limitations')
    p(text['bias'])
    sub('Source and coverage qualifications')
    p('Data integrity does not establish complete observation or valid causal identification. Humidity boundary values, absent hour records and conflicting metadata are retained as explicit qualifications. The auxiliary daily file validates rental totals, but does not prove every original system-hour was recorded. Original transaction-to-aggregate filtering and weather matching remain unknown.')
    page();h('Prohibited claims')
    sub('1. Causal weather effects')
    p('We must not claim that weather conditions causally determine bike rental demand based on this observational dataset. Weather is not randomized; season, hour, working-day status and calendar patterns can confound the association.')
    sub('2. Universal or present-day generalization')
    p('We must not generalize the observed relationships to all cities, all bike-sharing systems, or current populations. The sample covers a single historical system and transportability has not been tested.')
    sub('3. Perfect latent-demand measurement')
    p('Observed rental counts should not be interpreted as a perfect measurement of unconstrained latent demand. Completed rentals can be supply-limited and the files lack direct measurements of unmet demand.')
    h('Conclusion')
    p(text['conclusion'])
    h('Reproducibility')
    env=json.loads((ROOT/'results/runtime_environment.json').read_text(encoding='utf-8'))
    p('Executed on '+env['os']+', Python '+env['python']+'. Exact direct package versions are pinned in requirements.txt and environment.yml. The full pipeline verifies raw hashes, executes the notebook in a fresh kernel, generates this report and independently validates files, statistics and claims. Run from the project root:')
    p('python -m pip install -r requirements.txt','MonoAudit');p('python scripts/run_all.py','MonoAudit')
    p('Final fresh-kernel rerun and verification are recorded in results/qa_validation.json. The pipeline exits nonzero on failure. All paths are project-relative; no private machine path is required by project source. PDF creation does not require a TeX installation. No publication or GitHub push is performed.')
    page();h('AI use and source attribution')
    p('OpenAI Codex / ChatGPT-assisted workflow created the project, audit/statistical code, notebook, plots, report and documentation, then ran source/result checks. The user supplied the fixed specification. No instructor or second human review is claimed. Accepted instructions and Codex-modified implementation choices are disclosed in docs/ai_use_log.md. Programmatic checks and Codex visual review are separately identified in the QA record.')
    p('Key implementation decisions include time-block bootstrap instead of independent hourly resampling, interval withholding for sparse support, no unsupported Celsius conversions, and empirically labeled weekday mapping. The student must inspect the submitted work and follow their course disclosure policy.')
    sub('Sources actually used')
    p('Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5W894')
    p('Official dataset page (archived with SHA-256): https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset')
    p('Unchanged official ZIP: https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip')
    p('Readme.txt included in that ZIP, describing the creator, system-log aggregation, Freemeteo weather, fields and original citation request. The original system/weather feeds were not directly accessed for this audit.')
    p('CC BY 4.0 license: https://creativecommons.org/licenses/by/4.0/')
    p('README-requested paper attribution: Fanaee-T, H. and Gama, J. (2013). Event labeling combining ensemble detectors and background knowledge. Progress in Artificial Intelligence. https://doi.org/10.1007/s13748-013-0040-3 (bibliographic details reproduced from the official README; paper not independently analyzed).')
    sub('Companion evidence')
    p('Inspect the executed notebook, source_metadata.json, audit_results.csv, audit_summary.json, descriptive_statistics.csv, conditional_statistics.csv, statistical_method.json and raw-data dictionary. These preserve negative results, sparse-cell status and the actual dataset version rather than relying on this narrative alone.')
    p('Submission text is provided separately in reports/submission_summary.txt. Its repository URL must be completed only after a stable repository exists. No repository address is invented.')
    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#D7E0E8'));canvas.line(52,43,A4[0]-52,43);canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#657585'));canvas.drawString(52,29,'DS-A1 | UCI Bike Sharing | Observational measurement audit');canvas.drawRightString(A4[0]-52,29,str(doc.page));canvas.restoreState()
    pdf=ROOT/'reports/DS_A1_Bike_Sharing_Audit.pdf'
    doc=SimpleDocTemplate(str(pdf),pagesize=A4,rightMargin=52,leftMargin=52,topMargin=45,bottomMargin=58,title='Data Provenance and Measurement Audit of the UCI Bike Sharing Dataset',author='DS-A1; Codex-assisted workflow')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    print('PDF generated:',pdf.name,pdf.stat().st_size,'bytes')

if __name__=='__main__':main()
