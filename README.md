# UK Tech Job Market Analysis

An end-to-end data science project that scrapes, cleans, and analyzes UK tech job postings to uncover insights into salary trends, in-demand skills, and the geographic distribution of roles.

## Project Goal
The primary objective is to create a structured dataset from unstructured job postings to answer questions such as:
* What are the average salaries for key tech roles like Data Engineer, Software Engineer, and Data Scientist?
* How do salaries vary by location (e.g., London vs. other regions)?
* What are the most in-demand skills and technologies for each role?
* How does seniority level impact compensation and required skills?

## Tech Stack
* **Data Collection:** Python, Playwright, BeautifulSoup4
* **Data Processing:** Pandas, NumPy, SQLAlchemy
* **Database:** SQLite
* **Testing:** Pytest

## Project Structure

```text
tech-job-market-analysis/
│
├── jobs.db
├── README.md
├── requirements.txt
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── utils.py
│   │
│   ├── data_collection/
│   │   └── scraper.py
│   │
│   └── data_processing/
│       └── data_cleaning.py
│
└── tests/
    └── data_processing/
        └── test_data_cleaning.py
```

## The Data Pipeline

The project is built around a two-stage data pipeline:

### 1. Data Collection
A web scraper, built with **Python** and **Playwright**, automates a web browser to navigate the job site. It mimics human behavior (e.g., handling cookie pop-ups, performing searches, and clicking "Next Page") to bypass anti-bot measures. The scraper gathers URLs for individual job postings across multiple roles and pages, then visits each one to extract the raw, unstructured data. This raw data is then saved to a `jobs_raw` table in an **SQLite** database.

### 2. Data Cleaning and Processing
A separate Python script reads the raw data from the database using **Pandas** and **SQLAlchemy**. It then performs a series of transformations to create a clean, analysis-ready dataset:
* **Salary Parsing:** Converts varied text formats (e.g., "£50k - £60k", "£500 per day", "Competitive") into a single, numeric annual salary.
* **Location Standardization:** Parses messy location strings into clean `city` and `region` columns.
* **Date Conversion:** Transforms relative dates (e.g., "2 weeks ago") into absolute `datetime` objects.
* **Feature Engineering:** Creates new features by classifying job `seniority` and `employment_type`, and extracts a list of required `skills` from the full description.

The final, cleaned DataFrame is saved to a new table, `jobs_processed`, in the same database.

## Next Steps
* **Analysis & Visualization:** Connect Tableau to the `jobs_processed` table to create an interactive dashboard that explores the key insights.
* **Predictive Modeling:** Develop a text-classification model to to determine job seniority from job description text.
