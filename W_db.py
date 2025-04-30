import sqlite3
import pandas as pd

def store_jobs_in_db(jobs_df):
    conn = sqlite3.connect("job.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        job_id TEXT PRIMARY KEY,
        title TEXT,
        company TEXT,
        location TEXT,
        posted_date TEXT,
        job_type TEXT,
        search_query TEXT,
        page INTEGER,
        job_link TEXT,
        description TEXT,
        skills TEXT,
        experience TEXT
    )
    """)

    for _, row in jobs_df.iterrows():
        cursor.execute("""
        INSERT INTO jobs (
            job_id, title, company, location, posted_date,
            job_type, search_query, page, job_link,
            description, skills, experience
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(job_id) DO UPDATE SET
            title = excluded.title,
            company = excluded.company,
            location = excluded.location,
            posted_date = excluded.posted_date,
            job_type = excluded.job_type,
            search_query = excluded.search_query,
            page = excluded.page,
            job_link = excluded.job_link,
            description = excluded.description,
            skills = excluded.skills,
            experience = excluded.experience
        """, (
            row["ID"],
            row["Title"],
            row["Company"],
            row["Location"],
            row["Posted_Date"],
            row["Job_Type"],
            row["Search_Query"],
            int(row["Page"]),
            row["Job_Link"],
            row["Description"],
            row["Skills"],
            row["Experience_Needed"]
        ))

    conn.commit()

    df = pd.read_sql_query("SELECT * FROM jobs", conn)
    # print(df.head())

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    # print("Tables in the database:", tables)

    cursor.execute("PRAGMA table_info(jobs);")
    columns = cursor.fetchall()
    # print("\nStructure of 'jobs' table:")
    # for col in columns:
        # print(col)

    query = """
    SELECT * FROM jobs
    WHERE location LIKE '%Cairo%'
    """
    df_cairo = pd.read_sql_query(query, conn)
    # print("\nJobs in Cairo:")
    # print(df_cairo)

    df_company_count = pd.read_sql_query("""
    SELECT company, COUNT(*) as total_jobs
    FROM jobs
    GROUP BY company
    ORDER BY total_jobs DESC
    """, conn)
    # print("\nJob count per company:")
    # print(df_company_count)

    conn.close()