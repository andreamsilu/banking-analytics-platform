You are continuing the project:

"Banking Analytics Intelligence Platform Using Python"


Current progress:

Completed:

✅ Synthetic Banking Data Generator

Created:

data/raw/

- customers.csv
- accounts.csv
- transactions.csv
- loans.csv


✅ Data Cleaning Pipeline

Created:

data/processed/

- customers_clean.csv
- accounts_clean.csv
- transactions_clean.csv
- loans_clean.csv


✅ Customer Analytics Module

Created:

notebooks/01_customer_analysis.ipynb


The next phase is:

STEP 5: Transaction Analytics Exploratory Data Analysis (EDA)


Goal:

Analyze banking transaction behavior and provide insights that would help a bank understand:

- Transaction volume
- Transaction value
- Customer activity
- Digital banking adoption
- Channel performance
- Regional transaction patterns


Focus only on transaction analytics.

Do not analyze loans yet.


--------------------------------------------------

Create notebook:

notebooks/02_transaction_analysis.ipynb


Use:

- pandas
- numpy
- matplotlib
- seaborn
- plotly


--------------------------------------------------

PROJECT BUSINESS QUESTIONS:


Answer these questions:


1. How much money flows through the bank?

2. Which transaction channels are most used?

3. Which transaction types dominate?

4. When do customers transact most?

5. Which regions generate the highest activity?

6. How are customers adopting digital banking?



--------------------------------------------------

SECTION 1:
Load Data


Load:


data/processed/transactions_clean.csv


Also load:


data/processed/customers_clean.csv


Display:

- first records
- shape
- columns
- data types


Check:

- missing values
- duplicates



--------------------------------------------------

SECTION 2:
Transaction Portfolio Overview


Calculate:


Total Transactions


Total Transaction Value (TZS)


Average Transaction Amount


Maximum Transaction Amount


Minimum Transaction Amount


Number of Active Customers



Create KPI summary:



Example:


Total Transactions:

1,000,000


Total Value:

TZS 500 Billion


Average Transaction:

TZS 500,000



--------------------------------------------------

SECTION 3:
Transaction Type Analysis


Analyze:


Transaction types:


- Deposit
- Withdrawal
- Transfer
- Bill Payment
- Merchant Payment
- Loan Repayment


Calculate:


transaction_count

total_amount

average_amount



Create summary:


transaction_type_summary.csv



Visualization:


1. Transaction volume by type

Bar chart


2. Transaction value by type

Bar chart



Business questions:


- Are customers mainly depositing or withdrawing?
- Which transaction types create the highest value?



--------------------------------------------------

SECTION 4:
Digital Banking Channel Analysis


Analyze:


Channels:


Mobile App

USSD

ATM

Branch

Internet Banking



Calculate:


channel_transaction_count

channel_total_value

channel_percentage



Create:


channel_summary.csv



Visualizations:


1. Channel usage distribution

Bar chart


2. Channel transaction value comparison

Bar chart



Generate insight:


Example:


"Mobile channels represent the majority of transactions, indicating strong digital adoption."



--------------------------------------------------

SECTION 5:
Transaction Trend Analysis


Analyze transaction behavior over time.


Create:


transaction_month

transaction_year

transaction_day


Analyze:


Monthly transaction volume


Monthly transaction value



Visualizations:


Line chart:

Transactions per month


Line chart:

Transaction value per month



Business questions:


- Are transactions growing?
- Which months have highest activity?



--------------------------------------------------

SECTION 6:
Time-Based Transaction Analysis


Analyze:


Transaction hour


Create:


hourly_transaction_summary



Visualize:


Heatmap:


Day of week vs Transaction volume



Questions:


- What are peak banking hours?
- When should digital systems expect higher traffic?



--------------------------------------------------

SECTION 7:
Regional Transaction Analysis


Merge:

transactions_clean

customers_clean


Analyze by region:


region

transaction_count

transaction_value

average_transaction


Create:


regional_transaction_analysis.csv



Visualization:


Top regions by transaction value


Bar chart



Business questions:


- Which regions generate the highest banking activity?
- Which regions may need more banking services?



--------------------------------------------------

SECTION 8:
Customer Transaction Behavior


Calculate per customer:


number_of_transactions

total_transaction_amount

average_transaction_amount



Create:


customer_transaction_profile



Classify:


High Activity Customers

Medium Activity Customers

Low Activity Customers



Rules:


High Activity:

top 20% transaction frequency


Medium:

middle 50%


Low:

bottom 30%



Visualization:


Customer activity distribution



--------------------------------------------------

SECTION 9:
Generate Banking Insights


Create markdown section:


## Transaction Analytics Insights


Generate at least 10 business insights.


Examples:


1. Mobile App transactions contribute the highest transaction volume.

2. Peak transaction periods occur during business hours.

3. Dar es Salaam generates the highest transaction value.

4. Digital channels reduce dependence on branch transactions.

5. Certain transaction types contribute most of the banking volume.



--------------------------------------------------

SECTION 10:
Export Results


Create folder:


reports/transaction_analysis/


Save:


transaction_summary.csv

channel_summary.csv

transaction_type_summary.csv

regional_transaction_analysis.csv

customer_transaction_profile.csv



Save charts:


reports/transaction_analysis/charts/


Examples:


channel_usage.png

transaction_trends.png

transaction_by_region.png

transaction_heatmap.png



--------------------------------------------------

Coding Requirements:


- Use reusable functions
- Write clean Python
- Add comments explaining banking relevance
- Use TZS currency formatting
- Use meaningful chart titles
- Avoid unnecessary charts
- Focus on insights, not only visualization


Final output should represent a professional transaction analytics report used by a banking analytics team.


Do not create dashboards yet.

Do not analyze loans yet.

Only complete Transaction Analytics EDA.