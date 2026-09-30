# Data card

- Dataset: UCI Bike Sharing; creator Hadi Fanaee-T; repository UCI.
- Source, DOI and license: Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5W894](https://doi.org/10.24432/C5W894). [Official page](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). CC BY 4.0: [license](https://creativecommons.org/licenses/by/4.0/). The archived README additionally requests citation of Fanaee-T and Gama (2013), Event labeling combining ensemble detectors and background knowledge, DOI [10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).
- Observation period: 2011-01-01 to 2012-12-31.
- Geographic/system scope: Capital Bikeshare, Washington D.C. area; no universal scope.
- Unit: one recorded Capital Bikeshare system-hour.
- Population: Capital Bikeshare system-hours during the 2011-2012 observation period that the dataset is intended to represent.
- Sample: 17,379 observed hourly rows; 731 auxiliary daily rows.
- Columns: 17 raw columns. This project treats 12 calendar/weather fields as descriptive predictor candidates; 2 ID/key fields (instant,dteday), 2 outcome components and 1 target. UCI reports 13 features under a different role convention, including date.
- Target: cnt, completed rental count; cnt = casual + registered.
- Estimand: E[cnt | weathersit, workingday, hr], estimated only for observed combinations; unavailable combinations are not zero.
- Stakeholder: Capital Bikeshare operations and planning team; historical descriptive reference.
- Known transformations: derived date/hour key, calendar comparisons, aggregate summaries, seeded bootstrap; no raw-byte edits, exclusions or zero imputation.
- Intended use: descriptive measurement/provenance audit and historical pattern exploration.
- Out-of-scope use: weather causal effects, optimal dispatch, 2026 forecasts, other cities, perfect unmet-demand measurement.
- Missingness and completeness: The raw hourly file contains 17,379 rows and 17 columns across 731 dates. The UCI metadata reports no missing values, and the independent programmatic audit found 0 missing cells across 17 columns. Exact duplicates: 0; duplicate date-hour keys: 0; failed range checks: 0; internal consistency failures: 0. The count identity holds for all 17,379 rows. A nominal 24-hour-per-date grid contains 17,544 labels; 165 labels have no row. This is record-level incompleteness despite zero missing cells. Clock timezone, daylight-saving handling and omission reasons are undocumented. Absent hours are not assigned zero rentals; estimands are evaluated among observed rows.
- Limitations: The temporal boundary is 2011-2012 and the system boundary is Capital Bikeshare in the Washington, D.C. area. Season, calendar, year and hour may confound marginal weather associations; system growth and serial dependence also limit statistical interpretation. Sparse weather-hour-workingday cells do not identify all conditional means reliably. Missing system-hours and measurement constraints limit representativeness. Historical patterns do not establish optimal rebalancing or current operating decisions. Source metadata conflicts are detailed in provenance.md.
- Leakage: For prediction of cnt, casual and registered constitute deterministic target leakage: cnt = casual + registered on all 17,379 observed rows. Both components must be excluded from predictors. No model is trained. A future-facing model should use chronological evaluation and preprocessing fitted only on the training interval. Same-hour realized weather is potentially post-origin information for advance forecasts; feature timestamps are absent, so forecast availability cannot be certified.
- Ethics/privacy: distributed data are aggregate system-hour counts, with no rider identifiers or station-level locations in these CSVs. This does not prove that all source transaction data are risk-free. Do not infer individual behavior or justify exclusion of user groups using these historical aggregates.
- Provenance: documented original logs -> creator aggregation and Freemeteo weather -> UCI -> pinned project.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| hour.csv | 1156736 | `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f` |
| day.csv | 57569 | `a6bcf826782d3c0fbfdcbeead17cd0884185a0dafe8ff10cd48a874ee7ba18be` |
| Readme.txt | 5607 | `b92c8628622948bf0828c43a1b315d1517c3d7fd63654730d0dea379b8e88175` |
| Bike-Sharing-Dataset.zip | 279992 | `b70182d0d0508e9abbb79306ce5c0cec34869000f8220175ac83d11dbe845401` |
| uci_official_page.html | 157041 | `25386f08f920472c16f8973d5c51e390abf546d42c3e9cc3c82cb497311eecdb` |
