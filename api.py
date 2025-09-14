# api.py
import sqlite3
import pandas as pd
from fastapi import FastAPI
from ast import literal_eval

app = FastAPI()

@app.get("/api/analysis")
def get_analysis():
    """
    Provides analysis on the pre-scraped job data.
    """
    try:
        conn = sqlite3.connect('jobs.db')
        # Use pandas to read the SQL table into a DataFrame
        df = pd.read_sql_query("SELECT * FROM job_postings", conn)
        conn.close()

        # The 'skills' column was stored as a string representation of a list.
        # Use literal_eval to safely convert it back to a list.
        df['skills_list'] = df['skills'].apply(literal_eval)

        # Explode the DataFrame to have one row per skill per job
        all_skills_df = df.explode('skills_list')

        # Calculate top skills
        top_skills = all_skills_df['skills_list'].value_counts().nlargest(20)

        return {
            "total_jobs_analyzed": len(df),
            "top_skills": top_skills.to_dict()
        }
    except Exception as e:
        return {"error": str(e)}