# DS-A1 Bike Sharing Data Audit

## Question

How does hourly bike rental volume vary with weather conditions, working-day status, and hour of day in the 2011-2012 Capital Bikeshare data?

## Dataset

The official [UCI Bike Sharing dataset](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset) contains Capital Bikeshare records from 2011-2012. DOI: [10.24432/C5W894](https://doi.org/10.24432/C5W894). License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The unchanged hourly CSV and official README are included. Source URL, download date, attribution, and SHA-256 are recorded in [the Data Card](docs/data_card.md).

## Files

- `data/raw/`: `hour.csv` and official `Readme.txt`.
- `notebooks/DS_A1_Bike_Sharing_Audit.ipynb`: the complete analysis and explanations.
- `reports/`: PDF report and 150-300 word submission summary.
- `docs/`: Data Card, data dictionary, and AI-use/verification log.
- `results/`: audit results, summary statistics, and three figures.

## Main Findings

- The CSV has 17,379 rows and 17 columns.
- There are no missing cells, exact duplicate rows, or duplicate date-hour keys.
- The checked ranges are valid. `cnt = casual + registered` on every row, so the two components should not be predictors for `cnt`.
- Working days peak at 17:00; non-working days peak at 13:00.
- Mean rentals are 204.87 per hour in clear/few-cloud weather and 111.58 in light rain/snow.
- Completed rentals do not measure everyone who wanted a bike.

## How to Run

```bash
python -m pip install -r requirements.txt
jupyter notebook notebooks/DS_A1_Bike_Sharing_Audit.ipynb
```

Choose **Restart Kernel -> Run All**. The notebook runs with the included CSV and saves the result tables and figures. All main code is in its cells. The PDF is already generated.

## Limitations

The dataset covers one bike-sharing system and only 2011-2012. Weather comparisons are observational and may also reflect season, time of day, and working-day status. They do not establish causal effects or apply automatically to all systems or current users.

Repository: [https://github.com/Zhoujie-SONG/DS-A1-bike-sharing-audit](https://github.com/Zhoujie-SONG/DS-A1-bike-sharing-audit).
