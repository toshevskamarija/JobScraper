import os
import re
import requests
import pandas as pd
import sqlite3
from bs4 import BeautifulSoup
import seaborn as sns
import matplotlib.pyplot as plt

# Step 0: Setup folders
os.makedirs("analysis/plots", exist_ok=True)  # folder for saving plots

# Step 1: Web scraping

def extract(pageNum):
    url = f'https://devjobs.at/jobs/search?text=wien&page={pageNum}'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def transform(soup, joblist):
    #Collect data about title, company, salary, position summary
    listElements = soup.find_all('li', class_='bg-dj-mono-50')
    for item in listElements:
        title = item.find('h2').text
        company = item.find('p').text
        pills = item.find_all(
            'li',
            class_='transition-all text-sm flex place-items-center whitespace-nowrap rounded bg-opacity-5 dark:bg-opacity-10 text-dj-pill-shade-tertiary dark:text-white bg-dj-pill-tertiary dark:bg-dj-pill-tertiary py-1.5 px-3 first:ml-4'
        )
        salary = ''
        try:
            for pill in pills:
                text = pill.get_text(strip=True)
                if re.search(r'\d+\s?k\s?€', text):
                    salary = text
                    break
        except:
            salary = ''
        
        summary_tag = item.find('p', class_='text-dj-mono-500 dark:text-dj-mono-dark-400 line-clamp-2 px-4 font-normal')
        summary = summary_tag.text.strip().replace('\n', '') if summary_tag else ''

        #create dictionary
        job = {
            'title': title,
            'company': company,
            'salary': salary,
            'summary': summary
        }
        joblist.append(job)

# Step 2: Scrape multiple pages

def scrape_jobs(pages=30):
    joblist = []
    for i in range(0, pages*10, 2):  # loop through pages 0 till 99
        print(f'Getting page, {i}')
        soup = extract(i)
        transform(soup, joblist)
        #return dataframe with data
    return pd.DataFrame(joblist)

# Step 3: Save data

def save_data(df):
    #create csv with the data
    df.to_csv("jobs.csv", index=False)
    #create SQLite database
    conn = sqlite3.connect("jobs.db")
    # store dataframe in database
    df.to_sql("jobs", conn, if_exists="replace", index=False)
    conn.close()
    print("Data saved to CSV and SQLite database.")

# Step 4: Data cleaning & categorization

def clean_data(df):
    # Remove rows without salary
    df = df[df["salary"] != ""]
    # Extract numeric part of salary and convert to int
    df["salary_k"] = df["salary"].apply(lambda x: int(re.search(r"\d+", x).group()))
    
    def categorize_role(title):
        #Normalize job positions
        title = title.lower()
        if "head" in title or "leitung" in title or "director" in title:
            return "Higher level management"
        elif "machine learning" in title:
            return "Machine Learning"
        elif "data scientist" in title or "data science" in title:
            return "Data Scientist"
        elif "data engineer" in title:
            return "Data Engineer"
        elif "data analytics" in title or "data analyst" in title:
            return "Data Analytics"
        elif "ai" in title:
            return "AI Engineer"
        elif "fullstack" in title:
            return "Fullstack"
        elif "backend" in title:
            return "Backend"
        elif "frontend" in title:
            return "Frontend"
        elif "mobile" in title:
            return "Mobile Engineer"
        elif "software engineer" in title:
            return "Software Engineering"
        elif "qa" in title or "test" in title:
            return "QA"
        elif "architect" in title:
            return "IT Architect"
        elif "devops" in title or "cloud" in title:
            return "DevOps / Cloud"
        elif "cyber" in title or "security" in title:
            return "Cyber Security"
        elif "product owner" in title:
            return "Product Owner"
        elif "business analyst" in title:
            return "Business Analyst"
        elif "projekt manager" in title or "projektmanager" in title or "project manager" in title:
            return "Project Manager"
        elif "ux" in title or "ui" in title:
            return "UI/UX"
        elif "marketing" in title:
            return "Marketing"
        else:
            return "Other"
    
    df["role"] = df["title"].apply(categorize_role)
    df = df[df["role"] != "Other"]
    
    return df

# Step 5: Analysis with pandas

def analyze_data(df):
    summary = df.groupby("role")["salary_k"].agg(
        count="count",
        min_salary="min",
        max_salary="max",
        avg_salary="mean"
    ).reset_index()
    print(summary)

# Step 6: Plotting functions

def plot_avg_salary(df):
    #Bar chart – average salary per role
    plt.figure(figsize=(12,6))
    sns.barplot(
        data=df,
        x="role",
        y="salary_k",
        estimator="mean",
        order=df.groupby("role")["salary_k"].mean().sort_values().index
    )
    plt.title("Average Salary by Role")
    plt.ylabel("Salary (k €)")
    plt.xlabel("Role")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("analysis/plots/avg_salary_by_role.png")
    plt.show()

def plot_salary_distribution(df):
    #Violin plot – salary distribution
    variance_order = df.groupby("role")["salary_k"].var().sort_values().index
    plt.figure(figsize=(12,6))
    sns.violinplot(
        data=df,
        x="role",
        y="salary_k",
        order=variance_order
    )
    plt.title("Salary Distribution by Role (sorted by variance)")
    plt.ylabel("Salary (k €)")
    plt.xlabel("Role")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("analysis/plots/salary_violinplot.png")
    plt.show()

def plot_job_counts(df):
    #Bar chart – number of job postings
    plt.figure(figsize=(12,6))
    sns.countplot(
        data=df,
        x="role",
        order=df["role"].value_counts().index
    )
    plt.title("Number of Job Listings per Role")
    plt.ylabel("Count")
    plt.xlabel("Role")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("analysis/plots/salary_count_by_role.png")
    plt.show()


# Step 7: Main function

def main():
    df = scrape_jobs(pages=4)
    save_data(df)
    df = clean_data(df)
    analyze_data(df)
    plot_avg_salary(df)
    plot_salary_distribution(df)
    plot_job_counts(df)

if __name__ == "__main__":
    main()
