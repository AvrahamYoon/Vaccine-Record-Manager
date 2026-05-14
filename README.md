# Vaccine Record Manager

A **local-first** vaccination record dashboard built with [Streamlit](https://streamlit.io/). Records live in CSV files beside the app — no database, no hosted account. You keep full ownership of your data.

## Tech stack

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-239120?style=flat&logo=plotly&logoColor=white)](https://plotly.com/python/)
[![DuckDB](https://img.shields.io/badge/DuckDB-FFD700?style=flat&logo=duckdb&logoColor=black)](https://duckdb.org/)
[![SQL](https://img.shields.io/badge/SQL-005571?style=flat)](https://duckdb.org/docs/sql/introduction)
[![ReportLab](https://img.shields.io/badge/ReportLab-333333?style=flat)](https://www.reportlab.com/)

Badges from [Shields.io](https://shields.io/) (`style=flat`).

## Highlights

- **Overview** — KPIs and charts in one page: totals, latest date, yearly stats, timeline, vaccine/provider breakdown.
- **Records** — Filter/search, inline edit, inline delete (checkbox + save), add records, and visual import (CSV/Excel with mapping + preview).
- **Export** — Download CSV (UTF-8 with BOM) or a styled **A4 PDF** table with localized headers.
- **Settings** — Choose **English** or **Traditional Chinese (正體中文)**; switch vaccine display mode; run data quality checks; view vaccine name references.
- **Sign-in** — Simple username/password gate before the app (see below).

## Sign-in (default credentials)

The app opens with a **login screen by default**:

| Field | Default value |
|-------|----------------|
| Username | `admin` |
| Password | `RO_760715` |

**Why this password?** It is a small mnemonic for **15 July 1987** — the day **martial law was lifted** in **Taiwan (Republic of China, 中華民國)**, known in Chinese as **解嚴** (*jiěyán*). The string is not high security; it is meant as a memorable default for a personal/local tool and as a nod to that date.

**Overrides** — Set `VACCINE_APP_USERNAME` and/or `VACCINE_APP_PASSWORD`, or add `login_username` / `login_password` to [`.streamlit/secrets.toml`](.streamlit/secrets.toml) (see [`.streamlit/secrets.toml.example`](.streamlit/secrets.toml.example)). Values in the environment or secrets file replace the built-in defaults.

**Disable login** (e.g. local development): set environment variable `VACCINE_APP_NO_AUTH` to `1`, `true`, `yes`, or `on`.

> **Note:** Default credentials are visible in the repository (`core/auth.py`). Anyone with clone access can sign in. For sensitive deployments, always override with secrets or env vars and do not rely on the default password alone.

## Requirements

- **Python** 3.10+ recommended (matching current Streamlit / pandas ecosystems).
- Packages are pinned in [`requirements.txt`](requirements.txt):

  ```
  streamlit>=1.44.0
  pandas>=2.0.0
  plotly>=5.18.0
  reportlab>=4.0.0
  duckdb>=1.0.0
  opencc-python-reimplemented>=0.1.7
  ```

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

Running `python app.py` invokes Streamlit programmatically (`streamlit run` on port **8501**). You can also run Streamlit directly if you prefer:

```bash
streamlit run app.py
```

Using **VS Code** or Cursor, the **Run** button on `app.py` uses the same `__main__` entry point, so one click starts the app.

## Data loading (DuckDB + SQL)

CSV reads go through **[DuckDB](https://duckdb.org/)** using plain **`.sql` files** under [`sql/`](sql/) (for example [`sql/load_records.sql`](sql/load_records.sql)). Python only loads the file text and passes the CSV path as a bound parameter — **no SQL literals embedded in Python**.

- **Writes** still use **pandas `to_csv`** on `vaccine_records_cleaned.csv` (same on-disk format as before).
- If DuckDB fails (missing dependency, bad path), **`load_data` / `load_vaccine_names` fall back to `pandas.read_csv`**.

## Data files

| File | Role |
|------|------|
| `vaccine_records_cleaned.csv` | Primary store. Created automatically as an empty file with headers if it does not exist. |
| `vaccine_names.csv` | Optional mapping table: canonical Chinese/English names, abbreviations, and pipe-separated aliases. |

### Record columns (`vaccine_records_cleaned.csv`)

| Column | Meaning |
|--------|---------|
| `id` | Integer primary key (auto-assigned for new rows). |
| `name` | Canonical Chinese vaccine name after alias resolution (derived from mapping + `raw_name`). |
| `raw_name` | Original text as imported or typed; preserved for audit and export fidelity. |
| `dose` | Dose number (1, 2, …). |
| `date` | Vaccination date as `YYYY-MM-DD`. |
| `manufacturer` | Manufacturer name. |
| `batch` | Batch / lot number. |
| `arm` | `L`, `R`, or empty for unknown / both / not tracked. |
| `provider` | Clinic or hospital. |

Runtime columns **`abbr_zh`**, **`name_en`**, **`abbr_en`**, **`_display_name`** are computed in memory from `vaccine_names.csv` and language/format settings — they are **not** persisted to the CSV except through the resolved `name` / `raw_name` rules in `load_data()`.

### Legacy imports

If your CSV uses older headers, they are renamed on load: `vaccine_name` → `name`, `vaccination_date` → `date`, `batch_no` → `batch`.

### Vaccine name table (`vaccine_names.csv`)

Primary expected columns:

```text
canonical_zh, abbr_zh, canonical_en, abbr_en, aliases
```

For Chinese compatibility (Scheme A), the app accepts dual-standard headers:

- `canonical_zh_tw` / `canonical_zh_hant` (preferred traditional canonical name)
- `canonical_zh_cn` / `canonical_zh_hans` (simplified canonical name)
- `abbr_zh_tw` / `abbr_zh_hant` / `abbr_zh_cn` / `abbr_zh_hans`
- `aliases_tw` / `aliases_hant` / `aliases_cn` / `aliases_hans`

The app normalizes these into one internal standard and uses **traditional Chinese as the canonical display target** whenever provided. At the same time, simplified/traditional canonical names and abbreviations are both added to alias matching, so either script can map to the same vaccine entry.

## PDF export

PDFs use [ReportLab](https://www.reportlab.com/) on **A4** with a teal header styling. Chinese text needs a **CJK-capable TrueType/OpenType font** on the machine. The app tries common paths (for example Microsoft YaHei or SimSun on Windows, PingFang on macOS, Noto Sans CJK on Linux). If none register, glyphs may fall back to Helvetica and Asian characters might not render.

## Repository layout

```text
.
├── app.py                      # App entry, routing, shared UI style
├── core/
│   ├── auth.py                 # Optional login gate (defaults + env / secrets overrides)
│   ├── charts.py               # Shared chart palette + style helper
│   ├── data_store.py           # CSV I/O, ID generation, vaccine alias mapping
│   ├── duck_csv.py             # Run sql/*.sql via DuckDB to read CSV into pandas
│   ├── i18n.py                 # Language dictionary (English / 正體中文)
│   └── pdf_export.py           # PDF generation and CJK font fallback
├── sql/                        # DuckDB queries (read_csv_auto); path bound from Python
│   ├── load_records.sql
│   └── load_vaccine_names.sql
├── views/                      # UI renderers (not named `pages/` — Streamlit reserves that folder)
│   ├── login.py
│   ├── overview.py
│   ├── records.py
│   ├── export.py
│   └── settings.py
├── scripts/
│   └── expand_vaccine_aliases.py  # Optional: expand `aliases` with 简繁 variants (requires OpenCC)
├── vaccine_records_cleaned.csv # Your records (keep private if you use real health data)
├── vaccine_names.csv           # Vaccine aliases and display names
├── requirements.txt
├── LICENSE                     # MIT
└── README.md
```

## License

Released under the [MIT License](LICENSE).

Copyright (c) 2026 Abraham Yin.
