"""Documented, deterministic audits and descriptive associations; no predictive model."""
from pathlib import Path
import json
import hashlib
import platform
import sys
import importlib.metadata as metadata
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
RANDOM_SEED = 42
B = 2000
WEATHER = {1: 'Clear / few clouds', 2: 'Mist / cloudy', 3: 'Light rain / snow', 4: 'Heavy rain / snow / fog'}
QUESTION = 'How does hourly bike rental volume vary with weather conditions, working-day status, and hour of day in the 2011–2012 Capital Bikeshare data?'
PACKAGES = ['pandas', 'numpy', 'matplotlib', 'jupyter-core', 'nbconvert', 'nbformat', 'nbclient', 'ipykernel', 'reportlab', 'pypdf', 'Pillow']

# Definitions use the archived README for source bytes; current UCI differences are explicit.
DEFINITIONS = {
 'instant': ('Record index', 'ID', 'positive integer', 'index', 'Readme: record index', 'Not a predictor; sequential uniqueness is additionally checked.'),
 'dteday': ('Observation date', 'key', '2011-01-01 to 2012-12-31', 'calendar date', 'Readme: date', 'No timezone or daylight-saving convention documented.'),
 'season': ('Season code', 'feature', '1,2,3,4', 'category', 'Readme: 1:springer, 2:summer, 3:fall, 4:winter', 'Current UCI page instead says 1:winter,2:spring,3:summer,4:fall; retain numeric codes.'),
 'yr': ('Year code', 'feature', '0,1', 'category', 'Readme: 0:2011,1:2012', ''),
 'mnth': ('Month', 'feature', '1 to 12 integer', 'calendar month', 'Readme: month (1 to 12)', ''),
 'hr': ('Hour of day', 'key/feature', '0 to 23 integer', 'clock hour', 'Readme: hour (0 to 23)', 'Natural key candidate: dteday + hr.'),
 'holiday': ('Holiday indicator', 'feature', '0,1', 'binary', 'Readme: holiday status from DC holiday schedule', 'Historical external holiday schedule not independently reconstructed.'),
 'weekday': ('Day-of-week code', 'feature', '0 to 6 integer', 'category', 'Readme/UCI: day of the week; numeric mapping unspecified', 'Sunday=0 is verified empirically against parsed dates; not asserted as a documented mapping.'),
 'workingday': ('Neither weekend nor holiday', 'feature', '0,1', 'binary', 'Readme: 1 if neither weekend nor holiday; else 0', 'Calendar-based consistency uses parsed dates, independent of weekday encoding.'),
 'weathersit': ('Weather situation', 'feature', '1,2,3,4', 'category', 'Readme: 1 clear/few clouds; 2 mist/cloudy; 3 light snow/rain; 4 heavy rain/ice pellets/thunderstorm/mist or snow/fog', 'Composite categories; severity-4 inference withheld for insufficient support.'),
 'temp': ('Normalized temperature', 'feature', '0 to 1 inclusive', 'normalized', 'Readme: Celsius divided by 41; current UCI: (t+8)/47', 'Conflicting normalizations; no Celsius conversion in analysis.'),
 'atemp': ('Normalized feeling temperature', 'feature', '0 to 1 inclusive', 'normalized', 'Readme: Celsius divided by 50; current UCI: (t+16)/66', 'Conflicting normalizations; no Celsius conversion in analysis.'),
 'hum': ('Normalized humidity', 'feature', '0 to 1 inclusive', 'fraction', 'Readme: humidity divided by 100', 'Zero is within documented range; flag as possibly unusual, not established missing code.'),
 'windspeed': ('Normalized wind speed', 'feature', '0 to 1 inclusive', 'normalized', 'Readme: wind speed divided by 67', 'Physical unit of original wind speed not explicitly stated; zero may be calm/rounded.'),
 'casual': ('Casual-user rental count', 'target component', 'nonnegative integer; no documented upper cap', 'rentals/hour', 'Readme: count of casual users', 'Deterministic target leakage when predicting cnt.'),
 'registered': ('Registered-user rental count', 'target component', 'nonnegative integer; no documented upper cap', 'rentals/hour', 'Readme: count of registered users', 'Deterministic target leakage when predicting cnt.'),
 'cnt': ('Total completed rental count', 'target', 'nonnegative integer; no documented upper cap', 'rentals/hour', 'Readme: total rental bikes including casual and registered', 'Proxy for realized use, not unconstrained latent demand.')
}

def save_json(path, obj):
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n', encoding='utf-8')

def load_data():
    from verify_data import verify
    meta = verify()
    df = pd.read_csv(ROOT / 'data/raw/hour.csv')
    day = pd.read_csv(ROOT / 'data/raw/day.csv')
    dictionary = pd.DataFrame([dict(variable=k, description=v[0], dtype=str(df[k].dtype), role=v[1], valid_range_or_categories=v[2], units=v[3], source_definition=v[4], audit_notes=v[5]) for k,v in DEFINITIONS.items()])
    dictionary.to_csv(ROOT / 'docs/data_dictionary.csv', index=False)
    return df, day, meta, dictionary

def audit(df, day, meta, dictionary):
    rows = []
    def check(cat, name, var, expected, observed, status='PASS', notes='', invalid=0):
        rows.append(dict(check_category=cat, check_name=name, variable=var, expected=str(expected), observed=str(observed), status=status, notes=notes, invalid_row_count=int(invalid)))
    def rule(cat, name, var, condition, valid, notes=''):
        bad = ~pd.Series(valid, index=df.index).fillna(False)
        n = int(bad.sum())
        check(cat, name, var, condition, f'{len(df)-n} valid; {n} invalid', 'FAIL' if n else 'PASS', notes, n)
        if n:
            df.loc[bad].head(100).to_csv(ROOT / 'results' / f'invalid_{name}.csv', index=False)
        return n
    expected = list(DEFINITIONS)
    check('schema', 'shape', 'all', 'hourly observations x documented fields', list(df.shape))
    check('schema', 'columns', 'all', expected, list(df.columns), 'PASS' if list(df.columns)==expected else 'FAIL')
    check('schema', 'unexpected_columns', 'all', '[]', sorted(set(df)-set(expected)), 'PASS' if not set(df)-set(expected) else 'FAIL')
    check('schema', 'missing_columns', 'all', '[]', sorted(set(expected)-set(df)), 'PASS' if not set(expected)-set(df) else 'FAIL')
    check('schema', 'dictionary_alignment', 'all', 'same variables and actual pandas dtypes', len(dictionary), 'PASS' if dictionary.variable.tolist()==expected and dictionary.dtype.tolist()==[str(df[c].dtype) for c in expected] else 'FAIL')
    dates = pd.to_datetime(df.dteday, format='%Y-%m-%d', errors='coerce')
    discrete = {'season': [1,2,3,4], 'yr':[0,1], 'mnth':range(1,13), 'hr':range(24), 'holiday':[0,1], 'weekday':range(7), 'workingday':[0,1], 'weathersit':[1,2,3,4]}
    for c in df:
        typ = 'string' if c=='dteday' else ('float' if c in ['temp','atemp','hum','windspeed'] else 'integer')
        good_type = (df[c].dtype==object or pd.api.types.is_string_dtype(df[c])) if typ=='string' else (pd.api.types.is_float_dtype(df[c]) if typ=='float' else pd.api.types.is_integer_dtype(df[c]))
        check('schema', 'dtype', c, typ, str(df[c].dtype), 'PASS' if good_type else 'FAIL')
        if c in discrete:
            rule('range', c, c, f'in {list(discrete[c])}; integer', df[c].isin(discrete[c]) & df[c].eq(np.floor(df[c])))
        elif c in ['temp','atemp','hum','windspeed']:
            rule('range', c, c, 'finite and 0 <= value <= 1', np.isfinite(df[c]) & df[c].between(0,1), 'Normalized scale; no unverified physical conversion.')
        elif c in ['cnt','casual','registered','instant']:
            rule('range', c, c, 'finite nonnegative integer' if c!='instant' else 'finite positive integer', np.isfinite(df[c]) & df[c].ge(0 if c!='instant' else 1) & df[c].eq(np.floor(df[c])))
        else:
            rule('range', 'date_period', c, c+' parseable and in documented 2011-2012 period', dates.notna() & dates.between('2011-01-01','2012-12-31'))
    strings = pd.read_csv(ROOT / 'data/raw/hour.csv', dtype=str, keep_default_na=False)
    missing = df.isna().sum()
    miss_records=[]
    for c in df:
        s = strings[c].str.strip().str.lower()
        empty = int(s.eq('').sum())
        special = int(s.isin(['na','n/a','nan','null','none','missing','?','-999','-9999']).sum())
        miss_records.append(dict(variable=c, missing_cells=int(missing[c]), blank_strings=empty, suspected_sentinel_count=special))
        check('missingness','nulls',c,'0',int(missing[c]),'FAIL' if missing[c] else 'PASS',invalid=int(missing[c]))
        check('missingness','blank_or_sentinel',c,'no blank or predefined textual/negative sentinel codes',empty+special,'WARN' if empty+special else 'PASS', 'Heuristic only: positive 9999 is a legitimate record index, not a missing code; valid zeros are examined as anomalies.',empty+special)
    pd.DataFrame(miss_records).to_csv(ROOT / 'results/missingness.csv',index=False)
    rule('missingness','date_parse','dteday','all dates parse',dates.notna())
    exact=int(df.duplicated().sum()); semantic=int(df.duplicated(['dteday','hr']).sum()); index_dup=int(df.instant.duplicated().sum())
    for name,var,n in [('exact_rows','all',exact),('system_hour_key','dteday+hr',semantic),('index_key','instant',index_dup)]:
        check('duplicates',name,var,'0 repeated rows after first',n,'FAIL' if n else 'PASS',invalid=n)
    df.loc[df.duplicated(['dteday','hr'],keep=False)].to_csv(ROOT / 'results/semantic_duplicate_records.csv',index=False)
    identity=rule('consistency','cnt_identity','cnt','cnt == casual + registered',df.cnt.eq(df.casual+df.registered))
    rule('consistency','month_identity','mnth','mnth == parsed calendar month',df.mnth.eq(dates.dt.month))
    rule('consistency','year_identity','yr','yr == parsed year - 2011',df.yr.eq(dates.dt.year-2011))
    mappings={str(offset):int(df.weekday.ne((dates.dt.dayofweek+offset)%7).sum()) for offset in range(7)}
    save_json(ROOT / 'results/weekday_mapping_diagnostic.json', mappings)
    rule('consistency','weekday_empirical','weekday','empirical candidate (Monday=0 + 1) mod 7',df.weekday.eq((dates.dt.dayofweek+1)%7), 'Neither official document specifies mapping; all seven offsets tested. Empirical consistency, not independently documented encoding.')
    wd=(dates.dt.dayofweek.lt(5) & df.holiday.eq(0)).astype(int)
    rule('consistency','workingday_identity','workingday','weekday Mon-Fri and holiday=0 -> 1',df.workingday.eq(wd))
    rule('consistency','index_sequence','instant','observed sequence 1..N',df.instant.eq(np.arange(1,len(df)+1)), 'Empirical sequence expectation, not a source-specified maximum.')
    totals=df.groupby('dteday')[['casual','registered','cnt']].sum()
    joined=day.set_index('dteday')[['casual','registered','cnt']].join(totals,rsuffix='_hour',how='outer')
    failures=int((joined[['casual','registered','cnt']].to_numpy()!=joined[['casual_hour','registered_hour','cnt_hour']].to_numpy()).any(axis=1).sum())
    joined.to_csv(ROOT / 'results/day_hour_reconciliation.csv')
    check('consistency','day_hour_counts','casual,registered,cnt','hour sums equal daily counts on every date',failures,'FAIL' if failures else 'PASS',invalid=failures)
    hours=dates + pd.to_timedelta(df.hr,unit='h')
    calendar=pd.date_range(dates.min(),dates.max()+pd.Timedelta(hours=23),freq='h')
    gaps=calendar.difference(pd.DatetimeIndex(hours))
    gap_df=pd.DataFrame({'nominal_system_hour':gaps})
    gap_df['hour']=gap_df.nominal_system_hour.dt.hour
    gap_df.to_csv(ROOT / 'results/absent_system_hours.csv',index=False)
    gap_df.groupby('hour').size().rename('absent_hours').to_csv(ROOT / 'results/absent_hours_by_clock_hour.csv')
    check('coverage','nominal_hour_grid','dteday+hr','inspect 24 labeled hours per date',f'{len(calendar)} nominal; {len(gaps)} absent','WARN' if len(gaps) else 'PASS','Nominal clock grid only; timezone/DST and omission mechanism undocumented. Do not insert zero counts.')
    check('provenance','official_row_count_conflict','rows','compare pinned CSV with official page',f'CSV={len(df)}; current UCI page=17389','WARN','Archive README count matches CSV; analysis uses actual bytes.')
    check('provenance','definition_conflict','season,temp,atemp','reconcile archive README and current page','season labels and temperature normalization disagree','WARN','Use numeric season codes and normalized temperatures.')
    check('leakage','deterministic_target_components','casual,registered','exclude when predicting cnt',f'identity holds on {len(df)-identity}/{len(df)} rows','DETECTED','Outcome components reveal target; leakage is not a corrupted-data range failure.')
    check('leakage','temporal_split','dteday,instant','future-facing evaluation uses chronological split','not trained; dates parsed and ordered','REVIEWED','Random splits permit future-period information. Fit preprocessing only within training period; exclude record index.')
    check('leakage','post_outcome_availability','weather,temp,atemp,hum,windspeed','available at forecast origin','feature publication timestamps not supplied','UNVERIFIABLE','Same-hour realized weather may be unavailable for advance forecasts; no claim of forecast readiness.')
    check('leakage','predictor_review','all','calendar/weather candidates; no target or components','exclude cnt,casual,registered,instant','REVIEWED','Other deterministic outcome leakage not found in remaining definitions; timing cannot be verified.')
    variables=['cnt','casual','registered','temp','atemp','hum','windspeed']
    extremes=[]
    for c in variables:
        q1,q3=df[c].quantile([.25,.75]); lo=q1-1.5*(q3-q1); hi=q3+1.5*(q3-q1)
        mask=(df[c]<lo)|(df[c]>hi)
        n=int(mask.sum())
        check('anomaly','iqr_flag',c,f'outside [{lo:.4f},{hi:.4f}]',n,'FLAG' if n else 'PASS','Statistical flag; preserve all rows.',n)
        extremes.append(dict(variable=c,lower_fence=float(lo),upper_fence=float(hi),flagged_rows=n,zero_rows=int(df[c].eq(0).sum())))
    pd.DataFrame(extremes).to_csv(ROOT / 'results/anomaly_flags.csv',index=False)
    df.loc[df.cnt.eq(0)].to_csv(ROOT / 'results/zero_count_records.csv',index=False)
    df.nlargest(20,'cnt').to_csv(ROOT / 'results/extreme_count_records.csv',index=False)
    q1,q3=df.cnt.quantile([.25,.75]); peak=df[df.cnt>q3+1.5*(q3-q1)]
    peak.groupby(['hr','workingday','season','weathersit']).agg(n=('cnt','size'),mean=('cnt','mean')).reset_index().to_csv(ROOT / 'results/extreme_count_context.csv',index=False)
    zeros={c:int(df[c].eq(0).sum()) for c in variables}
    check('anomaly','humidity_zero','hum','inspect valid boundary values',zeros['hum'],'WARN' if zeros['hum'] else 'PASS','Zero humidity is unusual but not documented as missing; retain and compare sensitivity.')
    checks=pd.DataFrame(rows)
    checks.to_csv(ROOT / 'results/audit_results.csv',index=False)
    summary=dict(row_count=len(df),column_count=len(df.columns),day_row_count=len(day),missing_cells=int(missing.sum()),exact_duplicates=exact,semantic_duplicates=semantic,range_check_failures=int(checks.loc[checks.check_category.eq('range'),'status'].eq('FAIL').sum()),range_invalid_rows_total=int(checks.loc[checks.check_category.eq('range'),'invalid_row_count'].sum()),cnt_identity_satisfied=len(df)-identity,cnt_identity_failures=identity,internal_consistency_failures=int(checks.loc[checks.check_category.eq('consistency'),'invalid_row_count'].sum()),target_leakage_detected=identity==0,nominal_hours=len(calendar),absent_nominal_hours=len(gaps),observed_days=int(dates.nunique()),zero_counts=zeros,weekday_mapping_evidence=mappings,source_document_conflicts=['row count','season labels','temp/atemp normalization'],retained_rows=len(df),audit_check_count=len(checks))
    save_json(ROOT / 'results/audit_summary.json',summary)
    assert identity==0 and exact==0 and semantic==0, 'Critical invariant failed; investigate retained evidence.'
    return summary,checks

def describe(df):
    variables=['cnt','casual','registered','temp','atemp','hum','windspeed']
    stats=df[variables].describe(percentiles=[.01,.05,.25,.5,.75,.95,.99]).T
    stats.index.name='variable'
    stats.to_csv(ROOT / 'results/descriptive_statistics.csv')
    return stats

def bootstrap_weights(n, block_days):
    rng=np.random.default_rng(RANDOM_SEED+block_days)
    starts=rng.integers(0,n,size=(B,int(np.ceil(n/block_days))))
    idx=(starts[:,:,None]+np.arange(block_days))%n
    idx=idx.reshape(B,-1)[:,:n]
    weights=np.zeros((B,n),dtype=np.float64)
    np.add.at(weights,(np.repeat(np.arange(B),n),idx.ravel()),1)
    return weights

def grouped_estimates(df, keys, weights, days):
    grouped=df.groupby(keys,observed=True)
    stat=grouped.cnt.agg(n='size',mean='mean',median='median',sd='std').reset_index()
    stat['n_days']=grouped.dteday.nunique().to_numpy()
    sums=df.pivot_table(index='dteday',columns=keys,values='cnt',aggfunc='sum',fill_value=0).reindex(days,fill_value=0)
    counts=df.pivot_table(index='dteday',columns=keys,values='cnt',aggfunc='size',fill_value=0).reindex(days,fill_value=0)
    # GroupBy and pivot_table both use sorted category keys.
    denominator=weights @ counts.to_numpy(dtype=float)
    means=np.divide(weights @ sums.to_numpy(dtype=float),denominator,out=np.full(denominator.shape,np.nan),where=denominator>0)
    lower=[];upper=[];valid=[]
    for j,r in stat.iterrows():
        finite=means[:,j][np.isfinite(means[:,j])]
        valid.append(len(finite))
        if r.n_days<10 or len(finite)<.95*B:
            lower.append(np.nan);upper.append(np.nan)
        else:
            ci=np.quantile(finite,[.025,.975]);lower.append(ci[0]);upper.append(ci[1])
    stat['ci_low']=lower;stat['ci_high']=upper;stat['valid_bootstrap_draws']=valid
    stat['ci_status']=np.where(stat.n_days<10,'withheld: fewer than 10 observed days',np.where(stat.valid_bootstrap_draws<.95*B,'withheld: sparse bootstrap support','available'))
    return stat,means

def inference(df):
    days=sorted(df.dteday.unique())
    weights=bootstrap_weights(len(days),7)
    tables={}
    for name,keys in [('weather',['weathersit']),('workingday',['workingday']),('hour',['hr']),('hour_workingday',['hr','workingday']),('conditional',['weathersit','workingday','hr'])]:
        table,draws=grouped_estimates(df,keys,weights,days)
        table.to_csv(ROOT / f'results/{name}_statistics.csv',index=False)
        tables[name]=table
        if name=='workingday':
            diff=draws[:,1]-draws[:,0]
            ci=np.quantile(diff[np.isfinite(diff)],[.025,.975])
            point=float(table.loc[table.workingday.eq(1),'mean'].iloc[0]-table.loc[table.workingday.eq(0),'mean'].iloc[0])
            difference=dict(contrast='workingday=1 minus workingday=0',mean_difference=point,ci_low=float(ci[0]),ci_high=float(ci[1]),bootstrap_draws=B,block_days=7)
    one_day=bootstrap_weights(len(days),1)
    sensitivity,_=grouped_estimates(df,['weathersit'],one_day,days)
    sensitivity.to_csv(ROOT / 'results/weather_one_day_bootstrap_sensitivity.csv',index=False)
    df[df.hum.gt(0)].groupby('weathersit').cnt.agg(n='size',mean='mean').to_csv(ROOT / 'results/humidity_zero_sensitivity.csv')
    save_json(ROOT / 'results/workingday_difference.json',difference)
    method=dict(seed=RANDOM_SEED,effective_primary_seed=RANDOM_SEED+7,effective_sensitivity_seed=RANDOM_SEED+1,bootstrap_draws=B,primary_method='Circular moving-block bootstrap of calendar days, block length 7; hour-weighted ratio of rental sums to observed row counts',sensitivity='Independent day-cluster bootstrap, block length 1',ci='Percentile 95%; pointwise, not simultaneous; withheld for cells observed on fewer than 10 days or less than 95% finite draws',interpretation='The finite observed-period means are exact descriptions. Intervals describe model-based temporal resampling stability, not a probability sample, causal identification, or generalization to 2026.',limitations='Seven-day blocks preserve local dependence but not all seasonal dependence or system growth; stationarity is approximate; no multiplicity correction.',missing_hours='No zero imputation; observed system-hours only')
    save_json(ROOT / 'results/statistical_method.json',method)
    return tables,difference

def savefig(name):
    plt.savefig(ROOT / 'results/figures' / name,dpi=220,bbox_inches='tight',facecolor='white')
    plt.close()

def figures(df,tables):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','figure.facecolor':'white'})
    blue='#355C7D';gold='#AA7733'
    fig,ax=plt.subplots(figsize=(8,4))
    ax.hist(df.cnt,bins=40,color=blue,edgecolor='white',linewidth=.3)
    ax.set(title='Figure 1. Observed hourly rental count distribution',xlabel='Completed rentals per system-hour',ylabel='Observed system-hours',xlim=(0,None),ylim=(0,None))
    savefig('01_count_distribution.png')
    fig,ax=plt.subplots(figsize=(8,4.3))
    for work,col,style,label in [(0,gold,'--','Non-working day'),(1,blue,'-','Working day')]:
        g=tables['hour_workingday'].query('workingday == @work')
        ax.plot(g.hr,g['mean'],style,color=col,marker='o',markersize=3,label=label)
        ax.fill_between(g.hr,g.ci_low,g.ci_high,color=col,alpha=.14)
    ax.set(title='Figure 2. Hourly patterns by working-day status',xlabel='Hour of day (recorded clock hour)',ylabel='Mean completed rentals / hour',xticks=range(0,24,2),ylim=(0,None));ax.legend(frameon=False)
    fig.tight_layout(rect=(0,.07,1,1))
    fig.text(.12,.01,'Bands: pointwise 95% seven-day block bootstrap intervals.',fontsize=9)
    savefig('02_hour_workingday.png')
    fig,ax=plt.subplots(figsize=(8,4.5))
    w=tables['weather'];x=np.arange(len(w))
    ax.bar(x,w['mean'],color=blue,width=.6)
    finite=w.ci_low.notna()
    ax.errorbar(x[finite],w.loc[finite,'mean'],yerr=np.array([w.loc[finite,'mean']-w.loc[finite,'ci_low'],w.loc[finite,'ci_high']-w.loc[finite,'mean']]),fmt='none',ecolor='#333333',capsize=4)
    for i,r in w.iterrows(): ax.text(i,r['mean']+30,f'n={int(r.n):,}',ha='center',fontsize=9)
    ax.set(title='Figure 3. Rental volume by recorded weather situation',xticks=x,xticklabels=['1 Clear /\nfew clouds','2 Mist /\ncloudy','3 Light rain /\nsnow','4 Heavy rain /\nsnow / fog'],xlabel='Weather code (composite source categories)',ylabel='Mean completed rentals / hour',ylim=(0,float(w['mean'].max())+95))
    fig.tight_layout(rect=(0,.08,1,1))
    fig.text(.12,.005,'95% seven-day block intervals; code 4 interval withheld for sparse support.',fontsize=9)
    savefig('03_weather.png')
    fig,ax=plt.subplots(figsize=(8,4.2))
    groups=[df.loc[df.workingday.eq(k),'cnt'] for k in [0,1]]
    ax.boxplot(groups,tick_labels=['Non-working day','Working day'],showfliers=True,flierprops={'marker':'.','markersize':2,'alpha':.3},medianprops={'color':blue,'linewidth':2})
    ax.set(title='Figure 4. Rental distribution by working-day status',xlabel='Working-day status',ylabel='Completed rentals per system-hour',ylim=(0,None))
    savefig('04_workingday_distribution.png')
    fig,ax=plt.subplots(figsize=(8,4.3))
    matrix=df.pivot_table(index='weathersit',columns='hr',values='cnt',aggfunc='mean').reindex(index=[1,2,3,4],columns=range(24))
    im=ax.imshow(np.ma.masked_invalid(matrix.to_numpy()),aspect='auto',vmin=0,cmap='Blues')
    ax.set(title='Figure 5. Observed mean rentals: hour x weather',xlabel='Hour of day',ylabel='Weather code',xticks=range(0,24,2),yticks=range(4),yticklabels=[1,2,3,4]);fig.colorbar(im,ax=ax,label='Mean completed rentals / hour')
    fig.tight_layout(rect=(0,.07,1,1))
    fig.text(.12,.005,'Blank cells are unobserved combinations; weather code 4 has sparse support.',fontsize=9)
    savefig('05_hour_weather.png')
    variables=['cnt','casual','registered','temp','atemp','hum','windspeed']
    fig,axes=plt.subplots(2,4,figsize=(12,6))
    for ax,c in zip(axes.flat,variables):
        ax.boxplot(df[c],vert=True,showfliers=True,flierprops={'marker':'.','markersize':1,'alpha':.2},medianprops={'color':blue});ax.set(title=c,ylabel='rentals/hour' if c in ['cnt','casual','registered'] else 'normalized value');ax.set_xticks([])
    axes.flat[-1].axis('off');fig.suptitle('Audit: variable distributions (flags retained)',fontsize=14);fig.tight_layout()
    savefig('06_audit_boxplots.png')
    fig,axes=plt.subplots(2,4,figsize=(12,6))
    for ax,c in zip(axes.flat,variables):
        ax.hist(df[c],bins=30,color=blue);ax.set(title=c,xlabel='rentals/hour' if c in ['cnt','casual','registered'] else 'normalized value',ylabel='system-hours');ax.set_ylim(0,None)
    axes.flat[-1].axis('off');fig.suptitle('Audit: counts and normalized weather distributions',fontsize=14);fig.tight_layout()
    savefig('07_audit_histograms.png')
    dgp_figure()

def dgp_figure():
    fig,ax=plt.subplots(figsize=(9,8.4));ax.set(xlim=(0,12),ylim=(0,10));ax.axis('off')
    nodes=[(7.4,9.4,'Real-world time, calendar and weather\nUnobserved city activity'),(7.4,8,'Latent desire to use bikes'),(7.4,6.6,'Completed bike rentals\nObserved use, subject to possible supply constraints'),(7.4,5.2,'Capital Bikeshare transaction logs\n2011-2012 system records'),(7.4,3.8,'Fanaee-T / LIAAD: hourly and daily aggregation\nWeather from Freemeteo; calendar annotations'),(7.4,2.4,'UCI repository: pinned official ZIP\nhour.csv + day.csv + Readme.txt'),(7.4,1,'Our audit and descriptive analysis\nNo raw-byte modification or zero imputation')]
    for x,y,label in nodes:
        ax.add_patch(FancyBboxPatch((x-3.7,y-.42),7.4,.84,boxstyle='round,pad=0.04',facecolor='#F2F5F8',edgecolor='#355C7D',linewidth=1));ax.text(x,y,label,ha='center',va='center',fontsize=10)
    for a,b in zip(nodes,nodes[1:]):ax.annotate('',xy=(7.4,b[1]+.45),xytext=(7.4,a[1]-.45),arrowprops=dict(arrowstyle='->',color='#555555'))
    ax.text(.3,6.6,'Possible bike / dock\navailability and\nservice constraints',fontsize=9,ha='left',va='center',bbox=dict(facecolor='white',edgecolor='#AAAAAA',boxstyle='round,pad=.3'))
    ax.annotate('',xy=(3.65,6.6),xytext=(2.7,6.6),arrowprops=dict(arrowstyle='->',color='#777777'))
    fig.suptitle('Data-generating process and provenance lineage',fontsize=15)
    fig.text(.1,.015,'Supply mechanisms are conceptual. Collection, aggregation and weather source follow Readme.txt.\nExact original filtering, weather alignment, timezone and DST handling are not documented.',fontsize=9)
    savefig('00_dgp_lineage.png')

def findings(df,summary,tables,difference):
    w=tables['weather'];hw=tables['hour_workingday']
    peaks={str(k):hw.loc[hw.workingday.eq(k)].sort_values('mean',ascending=False).iloc[0][['hr','mean']].to_dict() for k in [0,1]}
    f=dict(summary=summary,overall_mean=float(df.cnt.mean()),weather=w[['weathersit','n','n_days','mean','median','sd','ci_low','ci_high','ci_status']].replace({np.nan:None}).to_dict('records'),workingday_difference=difference,peaks=peaks,weather_count_zero_humidity_excluded=int(df.hum.gt(0).sum()))
    save_json(ROOT / 'results/findings.json',f)
    return f

def narrative(f):
    s=f['summary'];w={int(r['weathersit']):r for r in f['weather']};p=f['peaks'];d=f['workingday_difference']
    return {
      'audit':f'The raw hourly file contains {s["row_count"]:,} rows and {s["column_count"]} columns across {s["observed_days"]} dates. The UCI metadata reports no missing values, and the independent programmatic audit found {s["missing_cells"]} missing cells across {s["column_count"]} columns. Exact duplicates: {s["exact_duplicates"]}; duplicate date-hour keys: {s["semantic_duplicates"]}; failed range checks: {s["range_check_failures"]}; internal consistency failures: {s["internal_consistency_failures"]}. The count identity holds for all {s["cnt_identity_satisfied"]:,} rows.',
      'coverage':f'A nominal 24-hour-per-date grid contains {s["nominal_hours"]:,} labels; {s["absent_nominal_hours"]} labels have no row. This is record-level incompleteness despite zero missing cells. Clock timezone, daylight-saving handling and omission reasons are undocumented. Absent hours are not assigned zero rentals; estimands are evaluated among observed rows.',
      'weather':f'Observed mean rentals/hour are {w[1]["mean"]:.2f} for clear/few-cloud weather (n={w[1]["n"]:,}), {w[2]["mean"]:.2f} for mist/cloudy weather (n={w[2]["n"]:,}), and {w[3]["mean"]:.2f} for light-rain/snow weather (n={w[3]["n"]:,}). Weather code 4 has only {w[4]["n"]} rows on {w[4]["n_days"]} date(s); its descriptive mean is {w[4]["mean"]:.2f} and its interval is withheld. Marginal contrasts may reflect calendar and hour composition.',
      'time':f'Working-day hourly means peak at {int(p["1"]["hr"]):02d}:00 ({p["1"]["mean"]:.2f} rentals/hour); non-working-day means peak at {int(p["0"]["hr"]):02d}:00 ({p["0"]["mean"]:.2f}). The marginal working-minus-non-working mean difference is {d["mean_difference"]:.2f} rentals/hour (95% seven-day block interval {d["ci_low"]:.2f} to {d["ci_high"]:.2f}). This marginal average hides distinct hourly profiles.',
      'anomaly':f'The observed count range is retained in full. Zero-count rows: {s["zero_counts"]["cnt"]}; zero-humidity rows: {s["zero_counts"]["hum"]}; zero-wind rows: {s["zero_counts"]["windspeed"]}. Zero humidity is a possible measurement concern, not an established missing code. IQR flags and the top 20 counts are saved with calendar/weather context. Statistically extreme rental counts are not automatically treated as data errors because they may represent genuine peak-demand periods.',
      'leakage':f'For prediction of cnt, casual and registered constitute deterministic target leakage: cnt = casual + registered on all {s["row_count"]:,} observed rows. Both components must be excluded from predictors. No model is trained. A future-facing model should use chronological evaluation and preprocessing fitted only on the training interval. Same-hour realized weather is potentially post-origin information for advance forecasts; feature timestamps are absent, so forecast availability cannot be certified.',
      'measurement':'Conceptual counterexample (not an event observed in these files): 200 people want a bike, only 100 bikes are available, and 100 rentals are completed. Observed cnt = 100 while latent demand is approximately 200. Bike availability, dock capacity, service outages and supply constraints are possible mechanisms. The CSV has no direct measures of unmet demand or these constraints; cnt measures completed rentals.',
      'bias':'The temporal boundary is 2011-2012 and the system boundary is Capital Bikeshare in the Washington, D.C. area. Season, calendar, year and hour may confound marginal weather associations; system growth and serial dependence also limit statistical interpretation. Sparse weather-hour-workingday cells do not identify all conditional means reliably. Missing system-hours and measurement constraints limit representativeness. Historical patterns do not establish optimal rebalancing or current operating decisions.',
      'prohibited':'We must not claim that weather conditions causally determine bike rental demand based on this observational dataset: no intervention, random assignment or causal adjustment is supplied. We must not generalize the observed relationships to all cities, all bike-sharing systems, or current populations: geographic and temporal transportability is untested. Observed rental counts should not be interpreted as a perfect measurement of unconstrained latent demand: supply constraints are unmeasured.',
      'conclusion':'The pinned data support a testable descriptive question about conditional mean completed rentals among observed 2011-2012 Capital Bikeshare system-hours. Hourly profiles differ by working-day status and rental volume differs across recorded weather categories. Data-level integrity passes do not remove source-document conflicts, absent-hour coverage, sparse cells, confounding or imperfect measurement. No causal, universal or optimal-dispatch claim follows.'
    }

def write_docs(df,meta,f):
    n=narrative(f);s=f['summary']
    hash_table='\n'.join(f'| {name} | {r["size_bytes"]} | `{r["sha256"]}` |' for name,r in meta['files'].items())
    source=f'''Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5W894](https://doi.org/10.24432/C5W894). [Official page]({meta['official_page_url']}). CC BY 4.0: [license]({meta['license_url']}). The archived README additionally requests citation of Fanaee-T and Gama (2013), Event labeling combining ensemble detectors and background knowledge, DOI [10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).'''
    provenance=f'''# Dataset provenance

{source}

Original Capital Bikeshare transaction logs (Washington D.C., 2011-2012) -> Hadi Fanaee-T / LIAAD aggregation into hourly and daily counts -> weather attributes sourced from Freemeteo and calendar annotations described in Readme.txt -> UCI distribution -> our hash-pinned audit. This lineage is documented in the archived README, not reconstructed by independently accessing the original transaction/weather feeds. Unknown steps include exact exclusions, weather temporal/spatial alignment, timezone and daylight-saving treatment.

Official ZIP: {meta['download_url']}

Downloaded at {meta['download_datetime_utc']} (Singapore date {meta['download_date_asia_singapore']}). Observed dates: {meta['observation_start']} to {meta['observation_end']}. No published semantic version was supplied; the following byte hashes define this project version. Raw files are never edited.

DOI and license were verified against text/link in the saved official HTML. The source-page snapshot is evidence of that verification; it may vary on later retrieval without indicating a CSV revision.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
{hash_table}

## Source conflicts retained

The current official webpage reports 17,389 instances, whereas the archive README and the executed CSV have {s['row_count']:,}. Current season labels (1:winter,2:spring,3:summer,4:fall) differ from archived labels (1:springer,2:summer,3:fall,4:winter). Temperature definitions differ: webpage temp=(t+8)/47 and atemp=(t+16)/66; README temp=t/41 and atemp=t/50. We use numeric season codes and normalized values, make no Celsius conversion, and treat the actual CSV as the authoritative analyzed version. Neither document specifies the weekday numeric mapping. All seven cyclic offsets were tested; Sunday=0 matches all rows empirically, and is labeled empirical rather than source-confirmed.

## Project transformations

Date parsing, derived nominal date-hour keys, grouping, descriptive summaries and seeded temporal bootstrap only. No raw rows were removed or filled. Hour and daily count totals are reconciled; daily weather fields are not joined back as hourly predictors. Original ZIP and extracted bytes are retained under the verified license with attribution.
'''
    (ROOT / 'docs/provenance.md').write_text(provenance,encoding='utf-8')
    card=f'''# Data card

- Dataset: UCI Bike Sharing; creator Hadi Fanaee-T; repository UCI.
- Source, DOI and license: {source}
- Observation period: {meta['observation_start']} to {meta['observation_end']}.
- Geographic/system scope: Capital Bikeshare, Washington D.C. area; no universal scope.
- Unit: one recorded Capital Bikeshare system-hour.
- Population: Capital Bikeshare system-hours during the 2011-2012 observation period that the dataset is intended to represent.
- Sample: {s['row_count']:,} observed hourly rows; {s['day_row_count']} auxiliary daily rows.
- Columns: {s['column_count']} raw columns. This project treats 12 calendar/weather fields as descriptive predictor candidates; 2 ID/key fields (instant,dteday), 2 outcome components and 1 target. UCI reports 13 features under a different role convention, including date.
- Target: cnt, completed rental count; cnt = casual + registered.
- Estimand: E[cnt | weathersit, workingday, hr], estimated only for observed combinations; unavailable combinations are not zero.
- Stakeholder: Capital Bikeshare operations and planning team; historical descriptive reference.
- Known transformations: derived date/hour key, calendar comparisons, aggregate summaries, seeded bootstrap; no raw-byte edits, exclusions or zero imputation.
- Intended use: descriptive measurement/provenance audit and historical pattern exploration.
- Out-of-scope use: weather causal effects, optimal dispatch, 2026 forecasts, other cities, perfect unmet-demand measurement.
- Missingness and completeness: {n['audit']} {n['coverage']}
- Limitations: {n['bias']} Source metadata conflicts are detailed in provenance.md.
- Leakage: {n['leakage']}
- Ethics/privacy: distributed data are aggregate system-hour counts, with no rider identifiers or station-level locations in these CSVs. This does not prove that all source transaction data are risk-free. Do not infer individual behavior or justify exclusion of user groups using these historical aggregates.
- Provenance: documented original logs -> creator aggregation and Freemeteo weather -> UCI -> pinned project.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
{hash_table}
'''
    (ROOT / 'docs/data_card.md').write_text(card,encoding='utf-8')
    versions={p:metadata.version(p) for p in PACKAGES}
    runtime=dict(os=platform.platform(),python=platform.python_version(),packages=versions,random_seed=RANDOM_SEED)
    save_json(ROOT / 'results/runtime_environment.json',runtime)
    (ROOT / 'requirements.txt').write_text('\n'.join(f'{p}=={v}' for p,v in versions.items())+'\n',encoding='utf-8')
    (ROOT / 'environment.yml').write_text('name: ds-a1-bike-audit\nchannels:\n  - conda-forge\ndependencies:\n  - python='+platform.python_version()+'\n  - pip\n  - pip:\n'+''.join(f'      - {p}=={v}\n' for p,v in versions.items()),encoding='utf-8')
    repro=f'''# Reproducibility

Executed OS: {runtime['os']}; Python {runtime['python']}. Package versions are recorded in requirements.txt, environment.yml and results/runtime_environment.json. Random seed: {RANDOM_SEED}; bootstrap replicates: {B}. No complex machine learning model is used. This run reused the existing Python analysis stack plus a workspace-only copy of bundled ReportLab exposed by PYTHONPATH after network installation attempts were interrupted. The clean setup below installs the same direct versions normally and does not need that temporary copy. SciPy was considered but is not required: the bootstrap uses NumPy. The jupyter-core CLI, nbconvert, nbclient and ipykernel are used without the unnecessary full Jupyter metapackage. Requests was considered but acquisition uses Python's standard-library urllib. The single-command pipeline uses nbclient rather than relying on a shell-level kernel configuration.

From the project root:

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate ; macOS/Linux: source .venv/bin/activate
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

Statistical method: {json.loads((ROOT/'results/statistical_method.json').read_text())['primary_method']}. The exact observed-period means do not need sampling intervals; reported intervals assess model-based resampling stability under approximate temporal assumptions. Fewer than 10 observed dates -> interval withheld. One-day cluster sensitivity is saved separately. No causal or external-population inference is justified.

The final quality check reruns the notebook from a fresh kernel, checks required files, figures and hash identity, compares canonical findings with notebook/PDF/README/summary, and records source/claim review. Semantic correctness remains inspectable in code; automated checks are not human verification. Install-time package resolution on another operating system may need platform-specific wheels even with exact direct versions.
'''
    (ROOT / 'docs/reproducibility.md').write_text(repro,encoding='utf-8')
    ai='''# AI-use disclosure

## AI tool
OpenAI Codex / ChatGPT-assisted workflow.

## Tasks assisted by AI
The user supplied a detailed assignment specification. Codex performed project scaffolding, official-source retrieval, Python audit and bootstrap implementation, notebook construction and execution, figure generation, documentation drafting, PDF creation, Git preparation and programmatic QA.

## Accepted suggestions
The implemented design follows the supplied research question and data source, immutable SHA-256 pinning, date-hour duplicate checks, deterministic target-leakage identification and the conceptual supply-constraint counterexample. These were task instructions, not fabricated user interactions.

## Rejected / modified suggestions
No human acceptance or rejection beyond the initial request is documented. During implementation Codex modified the suggested bootstrap approach to use seven-day blocks instead of independent hourly resampling, withheld intervals in sparsely supported cells, avoided selecting one of the conflicting temperature normalizations, and treated weekday mapping as empirically verified rather than documented. A broad sentinel scan initially flagged legitimate instant=9999; contextual inspection rejected that flag and removed positive 9999 from the candidate list without changing raw data. These are Codex implementation decisions, not claimed human judgments. Network package installation attempts were interrupted after prolonged delays. Existing analysis packages and a workspace-only copy of bundled ReportLab were used for this run; no successful installation is asserted.

## Independent verification
Here independent means results recomputed or checked against source bytes/documentation, not a second human reviewer. Code verifies official UCI DOI/license and raw SHA-256, date/calendar consistency, cnt identity and daily/hourly totals; fresh-kernel notebook reruns and artifact validation are performed by run_all.py. The accompanying results/qa_validation.json and docs/qa_review.md distinguish programmatic checks from Codex visual/text review. No unperformed manual or instructor review is asserted. The student must inspect and accept the submitted work under their course policy.
'''
    (ROOT / 'docs/ai_use_log.md').write_text(ai,encoding='utf-8')
    summary=f'''This project asks how hourly bike rental volume varies with weather conditions, working-day status, and hour of day in the 2011-2012 Capital Bikeshare data. It uses the official UCI Bike Sharing archive, with DOI and CC BY 4.0 verified against the official webpage and raw files pinned by SHA-256.

The executed hourly file contains {s['row_count']:,} rows and {s['column_count']} columns. The audit found {s['missing_cells']} missing cells, {s['exact_duplicates']} exact duplicates, {s['semantic_duplicates']} duplicate date-hour keys, {s['range_check_failures']} failed range checks and {s['internal_consistency_failures']} internal consistency failures. However, {s['absent_nominal_hours']} nominal hourly labels are absent, and official webpage metadata conflict with the archive on row count and some definitions. These issues are documented rather than hidden.

Mean hourly rentals are {f['weather'][0]['mean']:.2f} in clear/few-cloud weather and {f['weather'][2]['mean']:.2f} in light-rain/snow weather. Working-day and non-working-day hourly profiles differ; these are observational associations. Seven-day block bootstrap intervals assess temporal resampling stability, with sparse cells explicitly restricted.

The identity cnt = casual + registered holds on every row. Therefore both components must be excluded when predicting cnt because they deterministically reveal the target. Completed rentals also do not measure all latent demand: unavailable bikes or docks could restrict observed rentals. The files do not establish that these mechanisms actually occurred. The data support historical descriptive analysis of observed system-hours, with no weather causal claim or generalization to current or other systems.

GitHub URL: <INSERT_STABLE_GITHUB_REPOSITORY_URL>
'''
    assert 150<=len(summary.split())<=300,len(summary.split())
    (ROOT / 'reports/submission_summary.txt').write_text(summary,encoding='utf-8')
    readme=f'''# Project

Data Provenance and Measurement Audit of the UCI Bike Sharing Dataset (DS-A1).

## Research Question

{QUESTION}

## Dataset

{source}

Observed CSV: {s['row_count']:,} rows, {s['column_count']} columns; {meta['observation_start']} to {meta['observation_end']}. ZIP, original CSVs, README and official HTML snapshot are included with hashes in data/raw/source_metadata.json.

## Main Findings

{n['audit']}

{n['weather']}

{n['time']}

{n['coverage']}

Leakage: casual and registered exactly reconstruct cnt; exclude both from prediction inputs. Source documentation disagreements are recorded in docs/provenance.md.

## Repository Structure

- data/raw/: immutable official sources and source_metadata.json.
- notebooks/: executed English audit notebook.
- scripts/: acquisition, verification, analysis, notebook build, PDF and full pipeline.
- docs/: data card, dictionary, provenance, AI log, reproduction and QA review.
- results/: machine-readable audits, statistics, figures and QA.
- reports/: formal PDF and 150-300 word submission summary.

## Reproduction

```bash
python -m pip install -r requirements.txt
python scripts/run_all.py
```

See docs/reproducibility.md for a virtual environment and standalone notebook command. Existing source files are verified instead of redownloaded. Failed stages propagate a nonzero exit status.

## Outputs

- notebooks/DS_A1_Bike_Sharing_Audit.ipynb
- reports/DS_A1_Bike_Sharing_Audit.pdf
- reports/submission_summary.txt
- docs/data_card.md and docs/data_dictionary.csv
- results/audit_results.csv and results/audit_summary.json
- results/conditional_statistics.csv: direct E[cnt | weathersit, workingday, hr] estimates.

## Limitations

{n['bias']}

{n['measurement']}

{n['prohibited']}

## License / Attribution

Original dataset CC BY 4.0 with creator and paper attribution above. This educational analysis and code are provided under MIT (LICENSE). Official-page snapshot is retained as verification evidence; it is not assigned a new license. Raw dataset bytes are never rewritten. GitHub URL is intentionally completed only after a stable repository is created.
'''
    (ROOT / 'README.md').write_text(readme,encoding='utf-8')
    (ROOT / 'data/README.md').write_text('# Raw data policy\n\nOfficial UCI ZIP only. Exact source bytes are retained; no rows deleted or values filled. SHA-256 and sizes are in raw/source_metadata.json. Run `python scripts/verify_data.py` before analysis. Attribution and source conflicts: ../docs/provenance.md. Absent system-hours are not zero-imputed.\n',encoding='utf-8')
    return n
