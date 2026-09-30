# Project

Data Provenance and Measurement Audit of the UCI Bike Sharing Dataset (DS-A1).

## Research Question

How does hourly bike rental volume vary with weather conditions, working-day status, and hour of day in the 2011–2012 Capital Bikeshare data?

## Dataset

Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5W894](https://doi.org/10.24432/C5W894). [Official page](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). CC BY 4.0: [license](https://creativecommons.org/licenses/by/4.0/). The archived README additionally requests citation of Fanaee-T and Gama (2013), Event labeling combining ensemble detectors and background knowledge, DOI [10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).

Observed CSV: 17,379 rows, 17 columns; 2011-01-01 to 2012-12-31. ZIP, original CSVs, README and official HTML snapshot are included with hashes in data/raw/source_metadata.json.

## Main Findings

The raw hourly file contains 17,379 rows and 17 columns across 731 dates. The UCI metadata reports no missing values, and the independent programmatic audit found 0 missing cells across 17 columns. Exact duplicates: 0; duplicate date-hour keys: 0; failed range checks: 0; internal consistency failures: 0. The count identity holds for all 17,379 rows.

Observed mean rentals/hour are 204.87 for clear/few-cloud weather (n=11,413), 175.17 for mist/cloudy weather (n=4,544), and 111.58 for light-rain/snow weather (n=1,419). Weather code 4 has only 3 rows on 3 date(s); its descriptive mean is 74.33 and its interval is withheld. Marginal contrasts may reflect calendar and hour composition.

Working-day hourly means peak at 17:00 (525.29 rentals/hour); non-working-day means peak at 13:00 (372.73). The marginal working-minus-non-working mean difference is 11.80 rentals/hour (95% seven-day block interval 3.38 to 19.91). This marginal average hides distinct hourly profiles.

A nominal 24-hour-per-date grid contains 17,544 labels; 165 labels have no row. This is record-level incompleteness despite zero missing cells. Clock timezone, daylight-saving handling and omission reasons are undocumented. Absent hours are not assigned zero rentals; estimands are evaluated among observed rows.

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

The temporal boundary is 2011-2012 and the system boundary is Capital Bikeshare in the Washington, D.C. area. Season, calendar, year and hour may confound marginal weather associations; system growth and serial dependence also limit statistical interpretation. Sparse weather-hour-workingday cells do not identify all conditional means reliably. Missing system-hours and measurement constraints limit representativeness. Historical patterns do not establish optimal rebalancing or current operating decisions.

Conceptual counterexample (not an event observed in these files): 200 people want a bike, only 100 bikes are available, and 100 rentals are completed. Observed cnt = 100 while latent demand is approximately 200. Bike availability, dock capacity, service outages and supply constraints are possible mechanisms. The CSV has no direct measures of unmet demand or these constraints; cnt measures completed rentals.

We must not claim that weather conditions causally determine bike rental demand based on this observational dataset: no intervention, random assignment or causal adjustment is supplied. We must not generalize the observed relationships to all cities, all bike-sharing systems, or current populations: geographic and temporal transportability is untested. Observed rental counts should not be interpreted as a perfect measurement of unconstrained latent demand: supply constraints are unmeasured.

## License / Attribution

Original dataset CC BY 4.0 with creator and paper attribution above. This educational analysis and code are provided under MIT (LICENSE). Official-page snapshot is retained as verification evidence; it is not assigned a new license. Raw dataset bytes are never rewritten. The repository address is populated only after verified creation: https://github.com/Zhoujie-SONG/DS-A1-bike-sharing-audit.
