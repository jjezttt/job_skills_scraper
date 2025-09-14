# app.py
import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(layout="wide")
st.title("📊 Data Science Job Market Dashboard (New York, NY)")
st.markdown(f"An analysis of the most in-demand skills for Data Scientists. Data as of {time.strftime('%Y-%m-%d')}.")

# The URL of your FastAPI backend
API_URL = "http://127.0.0.1:8000/api/analysis"

# Fetch data from the API
@st.cache_data(ttl=600) # Cache the data for 10 minutes
def fetch_data():
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not connect to the API. Is it running? Error: {e}")
        return None

data = fetch_data()

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
    st.warning("Could not fetch data. Please run the data pipeline and ensure the API is running.")