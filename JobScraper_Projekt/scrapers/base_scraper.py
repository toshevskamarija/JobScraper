import re
from bs4 import BeautifulSoup
import requests
import pandas as pd
import sqlite3

def extract(pageNum):
  url= f'https://devjobs.at/jobs/search?text=wien&page={pageNum}'
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
  }
  r = requests.get(url, headers=headers)
  soup = BeautifulSoup(r.content, 'html.parser')
  return soup

def transform(soup):
  #Collect data about title, company, salary, position summary
  listElements= soup.find_all('li', class_= 'bg-dj-mono-50')
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
      salary=''
    
    summary = item.find('p', class_='text-dj-mono-500 dark:text-dj-mono-dark-400 line-clamp-2 px-4 font-normal').text.strip().replace('\n', '')

    #create dictionary
    job = {
      'title': title,
      'company': company,
      'salary': salary,
      'summary': summary
    }
    joblist.append(job)

  return
    
joblist=[]

#loop through pages 0,10,20,30
for i in range(0, 40, 10):
    print(f'Getting page, {i}')
    c=extract(i)
    transform(c)

#add data to dataframe
df=pd.DataFrame(joblist)
print(df.head())
#create csv with the data
df.to_csv('jobs.csv')

# create SQLite database
conn = sqlite3.connect("jobs.db")

# store dataframe in database
df.to_sql("jobs", conn, if_exists="replace", index=False)

conn.close()

print("Data successfully stored in SQLite database.")

