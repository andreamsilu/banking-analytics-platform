You are helping me build a professional data analytics portfolio project called:

"Banking Analytics Intelligence Platform Using Python"

Context:
I am a software developer transitioning into data analytics. The target employers are financial institutions such as banks, fintech companies, and insurance companies.

Current status:
- Project folder has already been created:
  Banking-Analytics-Platform
- Python virtual environment has been created:
  venv/
- requirements.txt has been created and packages are being installed.
- The next task is to build the synthetic banking data generation system.

Project Goal:
Create a realistic banking analytics platform using only Python.

Technology Stack:
- Python 3.12+
- Pandas
- NumPy
- Faker
- Matplotlib
- Seaborn
- Plotly
- Jupyter Notebook
- Streamlit (later for dashboard)

Follow professional data analytics project practices.

Current folder structure:

Banking-Analytics-Platform/

├── data/
│   ├── raw/
│   └── processed/
│
├── notebooks/
│   ├── 01_customer_analysis.ipynb
│   ├── 02_transaction_analysis.ipynb
│   └── 03_loan_analysis.ipynb
│
├── src/
│   ├── data_generator.py
│   ├── data_cleaning.py
│   └── analysis.py
│
├── dashboards/
│   └── app.py
│
├── reports/
│   └── insights.md
│
├── requirements.txt
└── README.md


TASK 1:
Create a synthetic banking data generation system.

Create:

src/data_generator.py


The script should generate realistic Tanzania banking datasets.

Generate the following datasets:

1. Customers Dataset

File:
data/raw/customers.csv

Generate 100,000 customers.

Columns:

customer_id
full_name
gender
date_of_birth
age
region
occupation
income_level
customer_since
customer_type


Rules:

- Use Faker for names.
- Use Tanzania regions:
  Dar es Salaam
  Arusha
  Mwanza
  Dodoma
  Mbeya
  Morogoro
  Tanga
  Zanzibar
  Kilimanjaro
  Tabora

Customer types:

Premium
Standard
Basic


2. Accounts Dataset

File:
data/raw/accounts.csv

Generate 150,000 accounts.

Columns:

account_id
customer_id
account_type
opening_date
balance
currency
status


Account types:

Savings
Current
Fixed Deposit


Currency:

TZS


Rules:

- Link accounts to existing customers.
- Generate realistic balances.
- Active accounts should be around 90%.


3. Transactions Dataset

File:
data/raw/transactions.csv

Generate 1,000,000 transactions.

Columns:

transaction_id
customer_id
account_id
transaction_date
transaction_time
channel
transaction_type
amount
merchant_category
region


Channels:

Mobile App
USSD
ATM
Branch
Internet Banking


Distribution:

Mobile App 45%
USSD 30%
ATM 15%
Branch 7%
Internet Banking 3%


Transaction types:

Deposit
Withdrawal
Transfer
Bill Payment
Merchant Payment
Loan Repayment


Merchant categories:

Shopping
Food
Transport
Utilities
Education
Healthcare


Rules:

- Transactions should cover 2025 and 2026.
- Amounts should be realistic in Tanzanian shillings.
- Mobile transactions should generally have smaller amounts.
- Branch transactions should have higher average amounts.


4. Loans Dataset

File:
data/raw/loans.csv

Generate 50,000 loans.

Columns:

loan_id
customer_id
loan_type
loan_amount
interest_rate
loan_date
duration_months
repayment_status
loan_status


Loan types:

Personal Loan
Business Loan
Education Loan
Vehicle Loan
Mortgage


Repayment status:

On Time
Late
Default


TASK 2:
Create reusable functions:

Example:

generate_customers()
generate_accounts()
generate_transactions()
generate_loans()

Use:

if __name__ == "__main__":
    main()


TASK 3:
Add logging:

Show progress:

Example:

Generating customers...
100000 customers created

Generating transactions...
1000000 transactions created


TASK 4:
Add comments and documentation.

TASK 5:
After creating the script:

Explain:
- How to run it
- Expected output files
- How to verify generated data


Important:
Do not create analysis yet.
Only focus on creating the synthetic banking data generation pipeline first.

Write clean production-quality Python code suitable for a GitHub portfolio project.