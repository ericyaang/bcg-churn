# PowerCo Customer Churn Prediction Dashboard

This repository contains the code for an interactive dashboard that predicts and visualizes customer churn for PowerCo, a major gas and electricity utility. The dashboard is built with Streamlit and Plotly and provides various insights including churn metrics, risk categorization, and revenue impact.

## Overview

The dashboard is divided into several sections:

1. **Churn and Revenue Metrics**: Provides a summary of key metrics including the churn rate, retention rate, number of customers at risk, revenue at risk, and monthly revenue.

2. **Customer Churn Risk**: Interactive visualizations of churn risk for different categories.

3. **Average Revenue and Churn Risk by Category**: Further visualizations showing the average revenue by category and churn risk against different categories.

4. **Preview of At-Risk Customers**: Displays a table with the top 10 customers at risk, sorted by their probability of churn.

## Data

The dashboard uses data from a file named `preds.parquet` located in a specific directory. This file should be a Parquet file containing the data needed for the dashboard, including predictions of customer churn.

## Installation & Usage

Clone the repository and navigate to the project directory.

```bash
git clone https://github.com/<your-username>/powerco-customer-churn.git
cd powerco-customer-churn

If you don't have Poetry installed, you can install it by following the instructions on the official Poetry website.

Once you have Poetry, you can install the project dependencies:

```
poetry install
```

You can now run the dashboard using Streamlit:

```
poetry run streamlit run app.py
```

Open your web browser and visit http://localhost:8501 to view the dashboard.