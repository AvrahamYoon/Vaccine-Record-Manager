# Vaccine Record Manager

A **local-first** vaccination record dashboard built with [Streamlit](https://streamlit.io/). Records live in CSV files beside the app — no database, no hosted account. You keep full ownership of your data.

## Highlights

- **Dashboard** — Totals, distinct vaccine counts, latest vaccination date, arm distribution (L/R), and charts (doses per year, arm split).
- **Records** — Filter and search; edit rows inline; add entries; delete by ID with confirmation.
- **Reports** — Timeline, doses by vaccine, doses by provider, yearly bar chart, arm pie chart.
- **Export** — Download CSV (UTF-8 with BOM) or a styled **A4 PDF** table.
- **Settings** — Choose **English** or **Traditional Chinese (正體中文)**; display vaccine names as **abbreviations** or **full names**; run **data quality** checks (duplicate IDs, bad dates/doses/arm values, unrecognized vaccine names); browse the vaccine name reference table.

## Requirements

- **Python** 3.10+ recommended (matching current Streamlit / pandas ecosystems).
- Packages are pinned in [`requirements.txt`](requirements.txt):

  ```
  streamlit>=1.32.0
  pandas>=2.0.0
  plotly>=5.18.0
  reportlab>=4.0.0
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

Expected columns:

```text
canonical_zh, abbr_zh, canonical_en, abbr_en, aliases
```

Pipe-separated **`aliases`** let you map many spellings or product strings to one canonical row. Names not listed are kept as typed and surfaced under **Settings → Data quality** so you can extend the table — no code change required.

## PDF export

PDFs use [ReportLab](https://www.reportlab.com/) on **A4** with a teal header styling. Chinese text needs a **CJK-capable TrueType/OpenType font** on the machine. The app tries common paths (for example Microsoft YaHei or SimSun on Windows, PingFang on macOS, Noto Sans CJK on Linux). If none register, glyphs may fall back to Helvetica and Asian characters might not render.

## Repository layout

```text
.
├── app.py                      # Single-file Streamlit application
├── vaccine_records_cleaned.csv # Your records (keep private if you use real health data)
├── vaccine_names.csv           # Vaccine aliases and display names
├── requirements.txt
├── LICENSE                     # MIT
└── README.md
```

## License

Released under the [MIT License](LICENSE).

Copyright (c) 2026 Abraham Yin.
