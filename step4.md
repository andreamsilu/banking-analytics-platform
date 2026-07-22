You are continuing the project:

"Banking Analytics Intelligence Platform Using Python"


Current progress:

Completed:

✅ Synthetic banking data generation

Created:

data/raw/

- customers.csv
- accounts.csv
- transactions.csv
- loans.csv


✅ Data cleaning pipeline

Created:

data/processed/

- customers_clean.csv
- accounts_clean.csv
- transactions_clean.csv
- loans_clean.csv


The next phase is:

STEP 4: Customer Analytics Exploratory Data Analysis (EDA)


Goal:

Analyze customer behavior and create business insights that would be useful for a bank's management team.

Focus only on customer analytics.

Do not analyze transactions or loans yet.


--------------------------------------------------

Create notebook:

notebooks/01_customer_analysis.ipynb


Use:

- pandas
- numpy
- matplotlib
- seaborn
- plotly


--------------------------------------------------

PROJECT OBJECTIVE:

Answer these banking questions:


1. Who are our customers?

2. Which customer groups generate the most value?

3. Where are customers located?

4. What customer segments exist?

5. What insights can improve banking decisions?


--------------------------------------------------

SECTION 1:
Import Libraries and Load Data


Load:

data/processed/customers_clean.csv

data/processed/accounts_clean.csv


Create:

customers dataframe

accounts dataframe


Display:

- first 5 records
- shape
- columns
- data types


--------------------------------------------------

SECTION 2:
Customer Overview Statistics


Calculate:

Total customers

Total accounts

Average customer age

Gender distribution

Customer type distribution

Regional distribution


Display KPI summary:


Example:


Total Customers:
100,000


Premium Customers:
25,000


Average Age:
38 years



--------------------------------------------------

SECTION 3:
Customer Demographic Analysis


Analyze:


### Age Distribution


Create:

- Histogram
- Box plot


Business question:

"What age groups does the bank serve most?"



Create:

age_group_summary


Example:


Age Group     Customers

18-30         25%

31-45         45%

46-60         25%

60+            5%



Visualization:

Bar chart



--------------------------------------------------

### Gender Analysis


Analyze:

Male vs Female customers


Visualization:

Pie chart or bar chart


Insight example:


"Customer base has balanced gender representation."



--------------------------------------------------

### Occupation Analysis


Find:

Top occupations by customer count.


Visualization:

Horizontal bar chart



Example:

Business Owner
Government Employee
Private Employee
Student



--------------------------------------------------

SECTION 4:
Regional Customer Analysis


Analyze:

Customer distribution by region.


Create:

region_summary


Columns:

region

customer_count

percentage



Visualization:

Bar chart



Questions:

- Which regions have the highest customers?
- Which regions are underserved?



--------------------------------------------------

SECTION 5:
Customer Value Analysis


Merge:

customers_clean

accounts_clean


Analyze:


Average balance by customer type


Example:


Customer Type        Average Balance


Premium              8,500,000 TZS

Standard             2,000,000 TZS

Basic                300,000 TZS



Visualization:

Bar chart



--------------------------------------------------

SECTION 6:
Customer Segmentation (Rule-Based)


Create simple banking segments.


Do NOT use machine learning yet.


Create:


customer_segment



Rules:


Premium Customers:

balance > 5,000,000


High Activity:

large number of accounts


Standard:

middle balance


Low Value:

low balance



Example output:


Customer ID     Segment


CUST001         Premium

CUST002         Standard

CUST003         Low Value



--------------------------------------------------

SECTION 7:
Generate Banking Insights


At the end create a markdown section:

## Key Business Insights


Generate at least 10 insights.


Examples:


1. Premium customers represent X% of the customer base.

2. Dar es Salaam has the highest customer concentration.

3. Mobile-focused customers may require more digital banking investment.

4. Customers aged 31-45 form the largest customer group.



--------------------------------------------------

SECTION 8:
Export Analysis Results


Save important summaries:


Create folder:

reports/customer_analysis/


Save:


customer_summary.csv

regional_analysis.csv

customer_segments.csv


Save charts:

reports/customer_analysis/charts/


Examples:


age_distribution.png

customer_by_region.png

customer_segments.png



--------------------------------------------------

Coding Standards:

- Write clean Python
- Add comments explaining banking relevance
- Use reusable functions where possible
- Avoid hard-coded analysis
- Make charts professional
- Include meaningful titles and axis labels


Final output should look like a real banking analytics report prepared by a data analyst.

Do not create dashboards yet.

Do not analyze transactions or loans yet.

Only complete Customer Analytics EDA.