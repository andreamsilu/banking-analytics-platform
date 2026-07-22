You are continuing the project:

"Banking Analytics Intelligence Platform Using Python"

Current progress:
- Synthetic banking datasets have been generated successfully.
- Raw datasets exist in:

data/raw/

Files:

customers.csv
accounts.csv
transactions.csv
loans.csv


The next phase is:

STEP 3: Data Quality Checks and Data Cleaning Pipeline


Goal:
Create a professional data preparation pipeline similar to what a banking data analyst would build before performing analysis.

We need to:
1. Load raw banking datasets
2. Perform data quality checks
3. Clean the data
4. Transform variables
5. Save processed datasets


Create:

src/data_cleaning.py


Follow this structure:

Banking-Analytics-Platform/

├── data/
│   ├── raw/
│   └── processed/
│
├── src/
│   ├── data_generator.py
│   ├── data_cleaning.py
│   └── analysis.py


--------------------------------------------------

TASK 1:
Create functions for loading datasets


Functions:

load_customers()
load_accounts()
load_transactions()
load_loans()


Requirements:

- Use pandas
- Load CSV files from data/raw/
- Return pandas DataFrames


--------------------------------------------------

TASK 2:
Create data quality checking functions


Create:

check_missing_values(df)

Purpose:
Identify missing values per column.


Output example:

Column              Missing

income_level        150
balance             0


--------------------------------


check_duplicates(df)

Purpose:
Find duplicate records.


Output example:

Duplicate rows found: 120


--------------------------------


check_data_types(df)

Purpose:
Display incorrect data types.


Example:

transaction_date should be datetime.


--------------------------------


Create a general function:

generate_data_quality_report(df, dataset_name)


It should display:

- Dataset name
- Number of rows
- Number of columns
- Missing values
- Duplicate rows
- Data types



--------------------------------------------------

TASK 3:
Clean each dataset


Create functions:


clean_customers(df)

Cleaning rules:

- Remove duplicate customers
- Handle missing values
- Convert dates correctly
- Ensure age is numeric
- Remove invalid ages


Age validation:

Minimum:
18

Maximum:
100



--------------------------------


clean_accounts(df)


Rules:

- Remove duplicates
- Convert opening_date to datetime
- Ensure balance is numeric
- Remove negative balances
- Validate account types



--------------------------------


clean_transactions(df)


Rules:

- Remove duplicate transactions
- Convert transaction_date to datetime
- Convert amount to numeric
- Remove zero or negative transactions
- Validate transaction channels
- Validate transaction types



--------------------------------


clean_loans(df)


Rules:

- Remove duplicates
- Convert dates
- Validate loan amounts
- Validate repayment status
- Remove invalid records



--------------------------------------------------

TASK 4:
Create feature engineering


Add useful banking analytics fields.


Customers:

Create:

customer_age_group


Categories:

18-30
31-45
46-60
60+



--------------------------------


Transactions:

Create:

transaction_month

transaction_year

transaction_hour


Example:

2026-01-15 14:30

becomes:

month = January
year = 2026
hour = 14



--------------------------------


Loans:

Create:

risk_category


Rules:

Default = High Risk

Late = Medium Risk

On Time = Low Risk



--------------------------------------------------

TASK 5:
Save cleaned datasets


Save to:

data/processed/


Files:

customers_clean.csv

accounts_clean.csv

transactions_clean.csv

loans_clean.csv



--------------------------------------------------

TASK 6:
Create main execution function


Example:


if __name__ == "__main__":

    print("Starting data cleaning pipeline")

    Load datasets

    Generate quality reports

    Clean datasets

    Save processed files

    print("Cleaning completed")


--------------------------------------------------

TASK 7:
Add documentation


Include comments explaining:

- Why each cleaning step is required
- Banking analytics importance
- Data quality issues being handled


--------------------------------------------------

TASK 8:
Create a README section


Add:

## Data Cleaning Pipeline

Explain:

- Raw data source
- Cleaning process
- Output datasets


--------------------------------------------------

Important:

Do not create visualizations yet.

Do not create dashboards yet.

Focus only on building a professional data preparation pipeline.

The final output should resemble the work of a banking data analyst preparing enterprise data for analytics.