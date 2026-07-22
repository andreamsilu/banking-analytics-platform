You are continuing the project:

"Banking Analytics Intelligence Platform Using Python"


Current progress:

Completed:

✅ Synthetic Banking Data Generator

Generated:

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


Outputs:

reports/customer_analysis/


✅ Transaction Analytics Module

Created:

notebooks/02_transaction_analysis.ipynb


Outputs:

reports/transaction_analysis/


The next phase is:

STEP 6: Loan Portfolio & Credit Analytics Exploratory Data Analysis (EDA)


Goal:

Analyze the bank's loan portfolio and generate insights that help management understand:

- Loan growth
- Portfolio composition
- Repayment performance
- Default risk
- High-risk segments
- Regional loan performance


Focus only on loan analytics.

Do not build machine learning models yet.

This is pure analytics and visualization.


--------------------------------------------------

Create notebook:

notebooks/03_loan_analysis.ipynb


Use:

- pandas
- numpy
- matplotlib
- seaborn
- plotly


--------------------------------------------------

BUSINESS QUESTIONS TO ANSWER:


1. How large is the bank's loan portfolio?

2. Which loan products are most popular?

3. How healthy is the repayment performance?

4. Which customer groups have higher risk?

5. Which regions have higher loan exposure?

6. What areas require management attention?


--------------------------------------------------

SECTION 1:
Load Data


Load:


data/processed/loans_clean.csv


Also load:


data/processed/customers_clean.csv


Display:


- first records
- dataset shape
- columns
- data types


Check:


- missing values
- duplicates
- invalid values



--------------------------------------------------

SECTION 2:
Loan Portfolio Overview


Calculate:


Total Number of Loans


Total Loan Amount


Average Loan Size


Maximum Loan Amount


Minimum Loan Amount


Average Interest Rate


Active Loans Count



Create KPI summary:


Example:


Total Loans:

50,000


Portfolio Value:

TZS 300 Billion


Average Loan:

TZS 6 Million



--------------------------------------------------

SECTION 3:
Loan Product Analysis


Analyze:


Loan types:


- Personal Loan
- Business Loan
- Education Loan
- Vehicle Loan
- Mortgage


Calculate:


loan_count

total_loan_amount

average_loan_amount



Create:


loan_product_summary.csv



Visualizations:


1. Number of loans by type

Bar chart


2. Loan value by type

Bar chart



Business insights:


Example:


"Business loans represent the largest share of the bank's lending portfolio."



--------------------------------------------------

SECTION 4:
Loan Status Analysis


Analyze:


Loan status:


- Active
- Completed
- Defaulted


Calculate:


loan_status_distribution



Visualization:


Pie chart


or


Bar chart



Business question:


"What percentage of loans are performing well?"



--------------------------------------------------

SECTION 5:
Repayment Performance Analysis


Analyze:


repayment_status:


- On Time
- Late
- Default


Calculate:


repayment_count

percentage_distribution



Create:


repayment_analysis.csv



Visualization:


Bar chart


Example:


On Time:

85%


Late:

10%


Default:

5%



Calculate:


Non Performing Loan Rate (NPL)


Formula:


NPL Rate =

(Default Loans + Late Loans) /
Total Loans



Display:


Example:


NPL Rate:

7.5%



--------------------------------------------------

SECTION 6:
Loan Risk Analysis


Use existing:


risk_category


Values:


Low Risk

Medium Risk

High Risk



Analyze:


risk distribution



Visualization:


Risk category distribution chart



Business questions:


- How much exposure does the bank have to risky loans?
- What percentage of customers are high risk?



--------------------------------------------------

SECTION 7:
Customer Risk Profile Analysis


Merge:


loans_clean

customers_clean



Analyze risk by:


Age group

Occupation

Income level

Customer type

Region



Examples:


Default Rate by Occupation


Business Owner

Government Employee

Private Employee



Visualization:


Bar charts



Insights:


Example:


"Self-employed customers show higher default rates compared with salaried customers."



--------------------------------------------------

SECTION 8:
Regional Loan Analysis


Analyze:


Loan distribution by region



Calculate:


region

loan_count

total_loan_amount

default_rate



Create:


regional_loan_analysis.csv



Visualizations:


1. Loan amount by region

2. Default rate by region



Business questions:


- Which regions have the highest loan exposure?
- Which regions require closer monitoring?



--------------------------------------------------

SECTION 9:
Loan Size Analysis


Analyze loan amounts:


Create categories:


Small Loan

< 1 Million


Medium Loan

1M - 10M


Large Loan

> 10M



Analyze:


- Loan distribution
- Default rate by loan size



Visualization:


Histogram


--------------------------------------------------

SECTION 10:
Generate Banking Insights


Create:


## Loan Analytics Insights


Generate at least 10 professional banking insights.


Examples:


1. Business loans represent the largest percentage of the portfolio.

2. Default rates are higher among certain customer segments.

3. High-value loans require stronger monitoring.

4. Some regions have higher credit risk exposure.

5. The bank maintains a healthy repayment rate.



--------------------------------------------------

SECTION 11:
Export Results


Create folder:


reports/loan_analysis/


Save:


loan_portfolio_summary.csv

loan_product_summary.csv

repayment_analysis.csv

risk_analysis.csv

regional_loan_analysis.csv

customer_risk_profile.csv



Save charts:


reports/loan_analysis/charts/


Examples:


loan_products.png

repayment_status.png

risk_distribution.png

regional_loan_analysis.png

loan_size_distribution.png



--------------------------------------------------

Coding Standards:


- Use reusable functions
- Add comments explaining banking meaning
- Format currency in TZS
- Use professional chart titles
- Include interpretation after each visualization
- Avoid creating ML models


Final output should look like a Credit Analytics Report prepared for a bank management team.


Do not create dashboards yet.

Do not create machine learning models.

Only complete Loan Portfolio & Credit Analytics EDA.