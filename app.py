# app.py

import streamlit as st
import pandas as pd
import time
# --- NEW IMPORTS ---
import sqlite3
from ast import literal_eval

st.set_page_config(layout="wide")
st.title("📊 Data Science Job Market Dashboard (New York, NY)")
st.markdown(f"An analysis of the most in-demand skills for Data Scientists. Data as of {time.strftime('%Y-%m-%d')}.")

# This function replaces the call to your API.
# It contains the logic from your api.py file.
@st.cache_data(ttl=3600) # Cache the data for 1 hour to improve performance
def fetch_data_from_db():
    try:
        conn = sqlite3.connect('jobs.db')
        df = pd.read_sql_query("SELECT * FROM job_postings", conn)
        conn.close()

        # Safely convert the string representation of lists back into actual lists
        df['skills_list'] = df['skills'].apply(literal_eval)
        all_skills_df = df.explode('skills_list')
        top_skills = all_skills_df['skills_list'].value_counts().nlargest(20)

        return {
            "total_jobs_analyzed": len(df),
            "top_skills": top_skills.to_dict()
        }
    except Exception as e:
        # Return an error dictionary if something goes wrong
        return {"error": str(e)}

# Fetch the data using our new direct-from-database function
data = fetch_data_from_db()

if data and "error" not in data:
    st.metric(label="Total Job Postings Analyzed", value=data['total_jobs_analyzed'])

    st.header("Top 20 Most In-Demand Skills")

    top_skills = data['top_skills']
    skills_df = pd.DataFrame(list(top_skills.items()), columns=['Skill', 'Count'])

    st.bar_chart(skills_df.set_index('Skill'))

    st.write("---")
    st.header("Raw Data")
    st.dataframe(skills_df)
else:
    st.error(f"Could not load data from jobs.db. Error: {data.get('error', 'Unknown')}")