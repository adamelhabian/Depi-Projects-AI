# CharityML Frontend Integration Guide

This directory contains the user interface for **Project 2: CharityML (Finding Donors)**.

## Architecture

```text
ML_P2/
├── Data/
│   ├── raw/census.csv
│   └── processed/census_cleaned.csv
├── Preprocessing/
│   └── finding_donors_preprocessing.ipynb
├── ML_Notebook/
│   └── MachineLearningTraining&Evaluation.ipynb
├── frontend/
│   ├── preview.html        # Direct browser test & demo file
│   ├── README.md           # Backend integration docs
│   ├── templates/
│   │   └── index.html      # Main UI Template (Jinja2 + HTML5)
│   └── static/
│       ├── css/
│       │   └── style.css   # Stylesheet & visual tokens
│       └── js/
│           └── main.js     # Form presets, education sync, smooth scroll
```

## Backend Integration Details (For Mina)

The form submits to `POST /predict`.

### Form Input Field Names (`request.form`)

| Field Name | Type | Description / Accepted Values |
| :--- | :--- | :--- |
| `age` | Integer | 17 to 90 (e.g. `38`) |
| `workclass` | String | `Private`, `Self-emp-not-inc`, `Self-emp-inc`, `Federal-gov`, `Local-gov`, `State-gov`, `Without-pay` |
| `education_level` | String | `Bachelors`, `Some-college`, `11th`, `HS-grad`, `Prof-school`, `Assoc-acdm`, `Assoc-voc`, `9th`, `7th-8th`, `12th`, `Masters`, `1st-4th`, `10th`, `Doctorate`, `5th-6th`, `Preschool` |
| `education-num` | Float/Int | 1.0 to 16.0 (automatically synced from `education_level` by JS, but also manually editable) |
| `marital-status` | String | `Married-civ-spouse`, `Divorced`, `Never-married`, `Separated`, `Widowed`, `Married-spouse-absent`, `Married-AF-spouse` |
| `occupation` | String | `Adm-clerical`, `Exec-managerial`, `Handlers-cleaners`, `Prof-specialty`, `Other-service`, `Sales`, `Craft-repair`, `Transport-moving`, `Farming-fishing`, `Machine-op-inspct`, `Tech-support`, `Protective-serv`, `Armed-Forces`, `Priv-house-serv` |
| `relationship` | String | `Wife`, `Own-child`, `Husband`, `Not-in-family`, `Other-relative`, `Unmarried` |
| `race` | String | `White`, `Asian-Pac-Islander`, `Amer-Indian-Eskimo`, `Other`, `Black` |
| `sex` | String | `Male`, `Female` |
| `capital-gain` | Float | Minimum 0 (e.g. `0` or `5178`) |
| `capital-loss` | Float | Minimum 0 (e.g. `0` or `1887`) |
| `hours-per-week` | Float | 1 to 99 (e.g. `40`) |
| `native-country` | String | `United-States`, `Canada`, `Germany`, etc. |

### Template Variables (`render_template("index.html", ...)`)

- **`prediction`** (string/int):
  - Pass `">50K"` (or `1`) when the model classifies high income (Likely Donor).
  - Pass `"<=50K"` (or `0`) when the model classifies standard income.
- **`error`** (optional string): Error message to display in the alert banner if validation or inference fails.
- **`form_data`** (optional dict): Echo back user inputs so the form stays populated after submission (`form_data=request.form`).
