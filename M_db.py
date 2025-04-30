import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
import time


def save_jobs_to_db(jobs_df):
    conn = sqlite3.connect("MostaqelJobs.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        date TEXT,
        link TEXT,
        budget TEXT,
        skills TEXT
    )
    """)

    for _, row in jobs_df.iterrows():
        cursor.execute("""
        INSERT INTO jobs (
            id, title, description, date, link, budget, skills
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            description = excluded.description,
            date = excluded.date,
            link = excluded.link,
            budget = excluded.budget,
            skills = excluded.skills
        """, (
            row["id"],
            row["title"],
            row["description"],
            row["date"],
            row["link"],
            row["budget"],
            row["skills"]
        ))

    conn.commit()
    conn.close()


def review_jobs_database(db_name="jobs.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables in the database:", cursor.fetchall())

    cursor.execute("PRAGMA table_info(jobs);")
    print("Structure of 'jobs' table:")
    for col in cursor.fetchall():
        print(col)

    df_all = pd.read_sql_query("SELECT * FROM jobs", conn)
    print("Sample Jobs:")
    print(df_all.head())

    df_cairo = pd.read_sql_query("SELECT * FROM jobs WHERE location LIKE '%Cairo%'", conn)
    print("Jobs in Cairo:")
    print(df_cairo)

    df_company_count = pd.read_sql_query("""
    SELECT company, COUNT(*) as total_jobs
    FROM jobs
    GROUP BY company
    ORDER BY total_jobs DESC
    """, conn)
    print("Job count per company:")
    print(df_company_count)

    conn.close()

if __name__ == "__main__":
    search_term = "Data Analyst"
    print(f"Scraping jobs for: {search_term}")

    # jobs_df = scrape_wuzzuf(search_term, max_pages=3)

    # if not jobs_df.empty:
    #     save_jobs_to_db(jobs_df)
    #     review_jobs_database()
    # else:
    #     print("No data to save.")
