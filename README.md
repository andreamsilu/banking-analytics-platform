# Banking Analytics Intelligence Platform

End-to-end banking analytics platform for Tanzania financial institutions. The system generates retail banking data, runs a quality and feature-engineering pipeline, produces analytical reports, and delivers an executive Streamlit BI dashboard for customer, payments, and credit decision support.

**Focus areas:** retail banking portfolio monitoring · digital channel performance · credit risk · management decision support (TZS)

---

## Overview

| Capability | Description |
|---|---|
| **Data generation** | Scalable Tanzania retail banking datasets (customers, accounts, transactions, loans) |
| **Data quality** | Validation, cleaning, and feature engineering into analysis-ready tables |
| **Exploratory analysis** | Jupyter notebooks and CSV/chart exports under `reports/` |
| **Executive BI** | Interactive Streamlit dashboard with KPI ribbons, scorecards, and prioritized actions |

### Scale (full local warehouse)

| Entity | Volume |
|---|---|
| Customers | 100,000 |
| Accounts | 150,000 |
| Transactions | 1,000,000 |
| Loans | 50,000 |

Published cloud mart: `data/analytics/` (GitHub / Streamlit Cloud). Full extracts: `data/processed/` (local).

---

## Architecture

```
data/raw/          →  Landing zone (source extracts)
       ↓
data_cleaning.py   →  Quality checks, types, features
       ↓
data/processed/    →  Warehouse tables (local)
       ↓
notebooks/ + reports/  →  Deep-dive analysis
       ↓
dashboard_utils.py + executive_bi.py  →  KPI / insight engine
       ↓
dashboards/app.py  →  Executive BI application
       ↓
data/analytics/    →  Published mart for cloud deployment
```

---

## Technology Stack

| Layer | Tools |
|---|---|
| Language | Python 3.12+ |
| Data | Pandas, NumPy, Faker, openpyxl |
| Visualization | Matplotlib, Seaborn, Plotly |
| Analysis | Jupyter Notebook |
| Application | Streamlit |

---

## Project Structure

```
Banking-Analytics-Platform/
├── data/
│   ├── raw/                 # Source extracts
│   ├── processed/           # Cleaned warehouse (local, gitignored)
│   └── analytics/           # Published analytics mart (cloud)
├── notebooks/
│   ├── 01_customer_analysis.ipynb
│   ├── 02_transaction_analysis.ipynb
│   └── 03_loan_analysis.ipynb
├── src/
│   ├── data_generator.py    # Source data generation
│   ├── data_cleaning.py     # Cleaning & feature engineering
│   ├── dashboard_utils.py   # Loaders, KPIs, charts
│   └── executive_bi.py      # Decision-support metrics & insights
├── dashboards/
│   ├── app.py               # Streamlit executive BI app
│   └── assets/              # Branding assets
├── reports/                 # Analysis exports (CSV + charts)
├── .streamlit/config.toml
├── requirements.txt
└── README.md
```

---

## Getting Started

### 1. Environment

```bash
git clone https://github.com/andreamsilu/banking-analytics-platform.git
cd banking-analytics-platform

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Build the data warehouse (local)

```bash
python src/data_generator.py
python src/data_cleaning.py
```

| Output | Path |
|---|---|
| Source extracts | `data/raw/*.csv` |
| Cleaned tables | `data/processed/*_clean.csv` |

### 3. Launch the dashboard

```bash
streamlit run dashboards/app.py
```

Open the URL shown in the terminal (typically `http://localhost:8501`).

> **Note:** Local runs prefer `data/processed/`. Streamlit Cloud loads `data/analytics/`.

---

## Data Model

### Source tables (`data/raw/`)

| Table | Contents |
|---|---|
| `customers.csv` | Demographics, region, segment, income, occupation |
| `accounts.csv` | Product type, balance, status, open date |
| `transactions.csv` | Amount, type, channel, timestamp, linked account |
| `loans.csv` | Product, principal, term, repayment status, risk |

### Engineered fields (`data/processed/`)

| Table | Added fields |
|---|---|
| `customers_clean.csv` | `customer_age_group` |
| `transactions_clean.csv` | `transaction_month`, `transaction_year`, `transaction_hour` |
| `loans_clean.csv` | `risk_category`, `monthly_interest`, `total_contractual_interest` |
| `interest_income_monthly_clean.csv` | Monthly performing-book interest income fact |

### Coverage

- **Regions:** Dar es Salaam, Arusha, Mwanza, Dodoma, Mbeya, Morogoro, Tanga, Zanzibar, Kilimanjaro, Tabora  
- **Channels:** Mobile App, USSD, ATM, Branch, Internet Banking  
- **Currency:** TZS  

---

## Analytical Workstreams

| Notebook | Focus | Report folder |
|---|---|---|
| `01_customer_analysis.ipynb` | Segments, demographics, regional value | `reports/customer_analysis/` |
| `02_transaction_analysis.ipynb` | Volume/value, channels, payment behaviour | `reports/transaction_analysis/` |
| `03_loan_analysis.ipynb` | Portfolio mix, repayment, default risk | `reports/loan_analysis/` |

Run notebooks from the project root with the virtual environment activated so imports and relative paths resolve correctly.

---

## Executive BI Dashboard

Internal management application for portfolio monitoring and decision support.

### Pages

| Page | Purpose |
|---|---|
| **Executive Overview** | KPI ribbon (with MoM / status), executive summary, action panel, scorecards |
| **Customer Analytics** | Demographics, value concentration, filters by region / type / gender |
| **Transaction Analytics** | Channel adoption, volume & value trends, regional payments |
| **Loan Portfolio Analytics** | Repayment health, NPL ratio, risk tiers, regional defaults |

### Design principles

- Decision-first layout (KPI → insight → recommended action)
- Material-icon navigation and branded sidebar
- Light / Dark theme via Streamlit settings
- MVC-style separation: UI in `dashboards/app.py`, logic in `src/`

---

## Deployment (Streamlit Community Cloud)

1. Ensure `main` is pushed to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io).
3. Create an app with:
   - **Repository:** `andreamsilu/banking-analytics-platform`
   - **Branch:** `main`
   - **Main file path:** `dashboards/app.py`
4. Deploy.

The cloud runtime loads the published mart from `data/analytics/`. Regenerate the full local warehouse anytime with the generation and cleaning scripts above.

---

## Configuration

| Item | Location |
|---|---|
| Streamlit theme / server | `.streamlit/config.toml` |
| Force analytics mart locally | `USE_ANALYTICS_DATA=1` |
| Large local extracts | Gitignored under `data/raw/`, `data/processed/` |

---

## License

All rights reserved. Banking Analytics Intelligence Platform — for professional portfolio and institutional demonstration use.
