# Dataset provenance

Fanaee-T, H. (2013). Bike Sharing [Dataset]. UCI Machine Learning Repository. DOI: [10.24432/C5W894](https://doi.org/10.24432/C5W894). [Official page](https://archive.ics.uci.edu/dataset/275/bike+sharing+dataset). CC BY 4.0: [license](https://creativecommons.org/licenses/by/4.0/). The archived README additionally requests citation of Fanaee-T and Gama (2013), Event labeling combining ensemble detectors and background knowledge, DOI [10.1007/s13748-013-0040-3](https://doi.org/10.1007/s13748-013-0040-3).

Original Capital Bikeshare transaction logs (Washington D.C., 2011-2012) -> Hadi Fanaee-T / LIAAD aggregation into hourly and daily counts -> weather attributes sourced from Freemeteo and calendar annotations described in Readme.txt -> UCI distribution -> our hash-pinned audit. This lineage is documented in the archived README, not reconstructed by independently accessing the original transaction/weather feeds. Unknown steps include exact exclusions, weather temporal/spatial alignment, timezone and daylight-saving treatment.

Official ZIP: https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip

Downloaded at 2026-09-30T02:16:41.598381+00:00 (Singapore date 2026-09-30). Observed dates: 2011-01-01 to 2012-12-31. No published semantic version was supplied; the following byte hashes define this project version. Raw files are never edited.

DOI and license were verified against text/link in the saved official HTML. The source-page snapshot is evidence of that verification; it may vary on later retrieval without indicating a CSV revision.

| File | Bytes | SHA-256 |
| --- | ---: | --- |
| hour.csv | 1156736 | `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f` |
| day.csv | 57569 | `a6bcf826782d3c0fbfdcbeead17cd0884185a0dafe8ff10cd48a874ee7ba18be` |
| Readme.txt | 5607 | `b92c8628622948bf0828c43a1b315d1517c3d7fd63654730d0dea379b8e88175` |
| Bike-Sharing-Dataset.zip | 279992 | `b70182d0d0508e9abbb79306ce5c0cec34869000f8220175ac83d11dbe845401` |
| uci_official_page.html | 157041 | `25386f08f920472c16f8973d5c51e390abf546d42c3e9cc3c82cb497311eecdb` |

## Source conflicts retained

The current official webpage reports 17,389 instances, whereas the archive README and the executed CSV have 17,379. Current season labels (1:winter,2:spring,3:summer,4:fall) differ from archived labels (1:springer,2:summer,3:fall,4:winter). Temperature definitions differ: webpage temp=(t+8)/47 and atemp=(t+16)/66; README temp=t/41 and atemp=t/50. We use numeric season codes and normalized values, make no Celsius conversion, and treat the actual CSV as the authoritative analyzed version. Neither document specifies the weekday numeric mapping. All seven cyclic offsets were tested; Sunday=0 matches all rows empirically, and is labeled empirical rather than source-confirmed.

## Project transformations

Date parsing, derived nominal date-hour keys, grouping, descriptive summaries and seeded temporal bootstrap only. No raw rows were removed or filled. Hour and daily count totals are reconciled; daily weather fields are not joined back as hourly predictors. Original ZIP and extracted bytes are retained under the verified license with attribution.
