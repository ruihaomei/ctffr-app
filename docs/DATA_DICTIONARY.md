# Data Dictionary

This file is generated from `ctffr/schema.py`; do not edit it manually.

| Field | Definition | Unit | Type | Accepted values | Chinese aliases |
|---|---|---:|---|---|---|
| `case_id` | Study identifier for the case (do not enter a patient name) | — | str | non-empty text | 姓名, 病例号 |
| `age` | Age | years | int | 18 to 100 | 年龄 |
| `sex` | Sex (male or female) | — | enum | male/female | 性别 |
| `height_cm` | Height | cm | float | 120 to 220 | 身高 |
| `weight_kg` | Weight | kg | float | 30 to 200 | 体重 |
| `hypertension` | History of hypertension (yes or no) | — | bool | yes/no | 高血压, 血压 |
| `smoking` | Smoking history (yes or no) | — | bool | yes/no | 吸烟 |
| `alcohol` | Alcohol-use history (yes or no) | — | bool | yes/no | 饮酒, 喝酒 |
| `target_vessel` | Target vessel text containing LAD, LCX, RCA, or RPDA | — | str | non-empty text | 斑块位置, 位置, 血管 |
| `plaque_lesions` | Number of plaque lesions | count | int | 0 to 10 | 斑块数, 血管斑块病变数 |
| `diameter_stenosis` | Diameter stenosis | % | float | 0 to 100 | 狭窄率, 血管狭窄率 |
| `max_area_stenosis` | Maximum area stenosis | % | float | 0 to 100 | 最大面积狭窄率 |
| `min_lumen_area` | Minimum lumen area | mm² | float | 0 to 30 | 最小管腔面积, 管腔最小截面积 |
| `plaque_length` | Plaque length | mm | float | 0 to 200 | 斑块长度, 长度 |
| `total_plaque_burden` | Total plaque burden | % | float | 0 to 100 | 总斑块负荷, 斑块总负荷 |
| `calcified_plaque_burden` | Calcified plaque burden | % | float | 0 to 100 | 钙化斑块负荷 |
| `lipid_plaque_burden` | Lipid plaque burden | % | float | 0 to 100 | 脂质斑块负荷 |
| `positive_remodeling` | Positive remodeling (yes or no) | — | bool | yes/no | 正性重构 |
| `low_attenuation_plaque` | Low-attenuation plaque (yes or no) | — | bool | yes/no | 低密度斑块, 低密度 |
| `napkin_ring_sign` | Napkin-ring sign (yes or no) | — | bool | yes/no | 餐巾环征, 餐巾指环 |
| `spotty_calcification` | Spotty calcification (yes or no) | — | bool | yes/no | 点状钙化 |

Values inside an accepted range but outside a cohort-observed range produce a warning, not an error.
The optional `reference_ctffr` column is used only to calculate prediction error and is never supplied to the model.
