# Data Card: Bike Sharing

| Item | Description |
|---|---|
| Dataset | Bike Sharing |
| Creator | Hadi Fanaee-T |
| Source | [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) |
| DOI | [10.24432/C5W894](https://doi.org/10.24432/C5W894) |
| License | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), listed by UCI |
| Download | [Official Bike-Sharing-Dataset.zip](https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip) |
| Download date | 2026-09-30 |
| Period | 2011-01-01 to 2012-12-31 |
| System | Capital Bikeshare, Washington, D.C., USA |
| Rows / columns | 17,379 / 17 in the actual hourly CSV |
| Unit | One recorded hour for the whole system |
| Target | `cnt`, completed rentals per hour |
| Version | The exact hourly file is identified by SHA-256 below |

**SHA-256 of `data/raw/hour.csv`:**

`e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f`

## Origin and intended use

The supplied README describes hourly aggregation of Capital Bikeshare records with Freemeteo weather information. The creator prepared the dataset and UCI distributes it. This project keeps `hour.csv` and the official `Readme.txt` unchanged.

The data are used for a course assignment about provenance, measurement, basic quality checks, and descriptive rental patterns. The question is: How does hourly bike rental volume vary with weather conditions, working-day status, and hour of day in the 2011-2012 Capital Bikeshare data?

## Important limitations

1. Only Capital Bikeshare is represented.
2. Only 2011-2012 is represented.
3. Weather comparisons are observational and may also reflect season, time of day, and working-day status.

`cnt` counts completed rentals rather than everyone who wanted a bike. For example, 200 people might want a bike while only 100 bikes are available. If each bike is rented once, about 100 completed rentals would be recorded. This is a conceptual example, not an observed event.

`casual` and `registered` together equal `cnt` on every row. They should not be predictors when `cnt` is the target.

## Attribution

Fanaee-T, H. (2013). *Bike Sharing* [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5W894.

The official README also requests citation of Fanaee-T, H. and Gama, J. (2013). *Event labeling combining ensemble detectors and background knowledge*. Progress in Artificial Intelligence. [DOI: 10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).
