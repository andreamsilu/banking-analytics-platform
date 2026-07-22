You are continuing the project:

"Banking Analytics Intelligence Platform Using Python"


CURRENT PROJECT STATUS:

Completed:

✅ Synthetic Banking Data Generation

Datasets:

data/raw/

- customers.csv
- accounts.csv
- transactions.csv
- loans.csv


✅ Data Cleaning Pipeline

Datasets:

data/processed/

- customers_clean.csv
- accounts_clean.csv
- transactions_clean.csv
- loans_clean.csv


✅ Customer Analytics Module

Notebook:

notebooks/01_customer_analysis.ipynb


Reports:

reports/customer_analysis/


✅ Transaction Analytics Module

Notebook:

notebooks/02_transaction_analysis.ipynb


Reports:

reports/transaction_analysis/


✅ Loan Analytics Module

Notebook:

notebooks/03_loan_analysis.ipynb


Reports:

reports/loan_analysis/


The next phase is:

STEP 7: Build Executive Banking Analytics Dashboard


Goal:

Create an interactive banking analytics dashboard using Streamlit that presents insights from all analytics modules.

The dashboard should look like a professional internal banking Business Intelligence tool.


--------------------------------------------------

TECHNOLOGY:

Use:

- Streamlit
- Pandas
- Plotly
- Matplotlib
- Seaborn


Create:

dashboards/app.py


--------------------------------------------------

DASHBOARD STRUCTURE:


Create the following pages:


1. Executive Overview

2. Customer Analytics

3. Transaction Analytics

4. Loan Portfolio Analytics



Use Streamlit sidebar navigation.


Example:


Sidebar:


🏦 Banking Analytics Platform


Pages:

📊 Executive Overview

👥 Customer Analytics

💳 Transaction Analytics

🏦 Loan Analytics



--------------------------------------------------

PAGE 1:
EXECUTIVE OVERVIEW


Purpose:

Provide management with a quick summary of bank performance.


Load:


customers_clean.csv

accounts_clean.csv

transactions_clean.csv

loans_clean.csv



Create KPI cards:


Customer KPIs:


Total Customers


Active Accounts


Premium Customers



Transaction KPIs:


Total Transactions


Total Transaction Value (TZS)


Average Transaction Amount



Loan KPIs:


Total Loan Portfolio


Total Loans


NPL Rate



Display using Streamlit metrics:



Example:


Total Customers

100,000


Transaction Volume

1M


Loan Portfolio

TZS 300B



--------------------------------------------------

Add Executive Charts:


Chart 1:

Customer Growth Trend


Chart 2:

Transaction Volume Trend


Chart 3:

Loan Portfolio Distribution


Chart 4:

Channel Usage Distribution



Use Plotly interactive charts.



--------------------------------------------------

PAGE 2:
CUSTOMER ANALYTICS


Purpose:

Understand customer base.



Create:


Section:

Customer Demographics



Charts:


1. Customers by Region


2. Customers by Age Group


3. Customers by Customer Type


4. Top Occupations



Section:


Customer Value Analysis



Charts:


1. Average Balance by Customer Type


2. Customer Segment Distribution



Add filters:


Region

Gender

Customer Type



--------------------------------------------------

PAGE 3:
TRANSACTION ANALYTICS


Purpose:

Monitor banking activity.



Create:


Section:

Transaction Overview



KPIs:


Transaction Count


Transaction Value


Average Transaction Amount



Charts:


1. Transactions Over Time


2. Transaction Value Trend


3. Transaction Type Distribution


4. Channel Performance



Channels:


Mobile App

USSD

ATM

Branch

Internet Banking



Add filters:


Date range

Region

Channel

Transaction Type



--------------------------------------------------

PAGE 4:
LOAN ANALYTICS


Purpose:

Monitor credit portfolio.


Create:


Loan Portfolio KPIs:


Total Loans


Total Loan Amount


Average Loan Size


NPL Rate



Charts:


1. Loan Product Distribution


2. Repayment Status


3. Risk Category Distribution


4. Default Rate by Region


5. Loan Amount Distribution



Add filters:


Region

Loan Type

Risk Category



--------------------------------------------------

DATA HANDLING:


Create reusable functions:


Example:


load_data()

calculate_kpis()

create_customer_charts()

create_transaction_charts()

create_loan_charts()



Avoid writing all code inside app.py.


Create:


src/dashboard_utils.py


for reusable functions.



--------------------------------------------------

VISUAL DESIGN:


Create professional banking style:


Requirements:


- Clean layout
- Clear section headings
- Consistent formatting
- Currency formatting in TZS
- Professional chart titles
- Use columns for KPI cards
- Avoid unnecessary charts



Example:


st.metric(
"Total Customers",
"100,000"
)



--------------------------------------------------

ERROR HANDLING:


Add:


- File existence checks
- Empty dataframe checks
- Friendly error messages



Example:


if file not found:

"Dataset missing. Please run data generation pipeline first."



--------------------------------------------------

PROJECT STRUCTURE AFTER THIS STEP:


Banking-Analytics-Platform/


├── dashboards/

│   ├── app.py

│   └── dashboard_utils.py


├── data/

├── notebooks/

├── src/

├── reports/

└── README.md



--------------------------------------------------

README UPDATE:


Add:


## Banking Analytics Dashboard


Explain:


- Purpose
- Features
- Technologies
- How to run


Running instructions:


streamlit run dashboards/app.py



--------------------------------------------------

FINAL REQUIREMENT:


The dashboard should demonstrate:

✅ Banking business understanding

✅ Data analysis skills

✅ Python programming

✅ Data visualization skills

✅ Ability to communicate insights


Do not add Machine Learning yet.

Do not add deployment yet.

Focus on creating a polished local Streamlit banking analytics dashboard.