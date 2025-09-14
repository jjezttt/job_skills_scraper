# pipeline.py
import pandas as pd
import sqlite3
import re
from playwright.sync_api import sync_playwright
from collections import Counter
import time

# Define the skills dictionary
SKILLS = {
    'Python': ['python'], 'R': ['r language', ' r,'], 'SQL': ['sql'], 'Spark': ['spark', 'pyspark'],
    'Hadoop': ['hadoop'], 'AWS': ['aws', 's3', 'ec2', 'redshift'], 'Azure': ['azure'], 'GCP': ['gcp', 'google cloud'],
    'TensorFlow': ['tensorflow', 'keras'], 'PyTorch': ['pytorch'], 'Scikit-learn': ['scikit-learn', 'sklearn'],
    'Pandas': ['pandas'], 'NumPy': ['numpy'], 'Tableau': ['tableau'], 'Power BI': ['power bi', 'powerbi'],
    'Docker': ['docker'], 'Git': ['git'], 'Excel': ['excel']
}

def extract_skills(description):
    found_skills = set()
    if not isinstance(description, str): return []
    description_lower = description.lower()
    for skill, keywords in SKILLS.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', description_lower):
                found_skills.add(skill)
                break
    return list(found_skills)

def run_pipeline():
    """Main function to run the entire data collection and processing pipeline."""
    print("Starting the data pipeline...")
    job_title = "Data Scientist"
    location = "New York, NY"
    pages_to_scrape = 5 # Scrape 5 pages for a good sample size

    all_links = set()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, timeout=60000)
        page = browser.new_page()

        # Scrape links first
        for page_num in range(pages_to_scrape):
            url = f"https://www.indeed.com/jobs?q={job_title.replace(' ', '+')}&l={location.replace(' ', '+')}&start={page_num * 10}"
            print(f"Navigating to link search page {page_num + 1}...")
            page.goto(url, timeout=120000)
            
            # This is the point for manual CAPTCHA solving
            print("You have 2 minutes to solve any CAPTCHA...")
            try:
                page.wait_for_selector('a.jcs-JobTitle', timeout=120000)
            except Exception:
                print(f"Could not find job cards. Stopping.")
                break

            job_links_locator = page.locator('a.jcs-JobTitle')
            count = job_links_locator.count()
            for i in range(count):
                href = job_links_locator.nth(i).get_attribute('href')
                if href:
                    all_links.add("https://www.indeed.com" + href)
            time.sleep(2)

        print(f"Found {len(all_links)} unique job links.")
        
        # Scrape descriptions for each link
        job_data = []
        for i, link in enumerate(list(all_links)):
            print(f"Scraping description {i+1}/{len(all_links)}...")
            try:
                page.goto(link, timeout=60000)
                page.wait_for_selector('#jobDescriptionText', timeout=10000)
                description = page.locator('#jobDescriptionText').inner_text()
                job_data.append({'url': link, 'description': description})
            except Exception as e:
                print(f"Could not scrape {link}: {e}")
            time.sleep(1)

        browser.close()

    print("Scraping complete. Processing data...")
    df = pd.DataFrame(job_data)
    df.dropna(subset=['description'], inplace=True)
    df['skills'] = df['description'].apply(extract_skills)
    
    # Convert skills list to a string for SQLite compatibility
    df['skills'] = df['skills'].apply(str)

    # Save to database
    print("Saving data to jobs.db...")
    conn = sqlite3.connect('jobs.db')
    df.to_sql('job_postings', conn, if_exists='replace', index=False)
    conn.close()
    
    print("Pipeline finished successfully!")

if __name__ == '__main__':
    run_pipeline()