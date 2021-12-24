
from selenium import webdriver
from selenium.webdriver.common.by import By
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import time
from listing import Listing

#set up web driver and urls needed for indeed.com
driver = webdriver.Chrome(executable_path='/Users/archiejones/Downloads/chromedriver')
indeed_url = 'https://www.indeed.com/jobs?q=software%20engineer%20intern&l=remote&jt=internship&remotejob=032b3046-06a3-4876-8dfd-474eb5e7ed11&vjk=254a1c3bc64b81c2'
simply_hired_url = 'https://www.simplyhired.com/search?q=software+engineer+intern&l=remote&fdb=1&sb=dd&jt=internship&job=QScUKskmSyUp4MN-F7tpJIjEKoROWoCh4pJfTuURGlkdKbhnJmQeGw'
driver.get(indeed_url)

#initialize jobList that will be filled with potential jobs
jobList = []

#find jobs from indeed.com
jobs = driver.find_elements(By.CLASS_NAME, 'slider_item')
for job in jobs:
	all = job.find_elements(By.CSS_SELECTOR, 'h2')
	for j in all:
		texts = j.find_elements(By.CSS_SELECTOR, 'span')
		if texts[0].text == 'new':
			companyName = job.find_element(By.CLASS_NAME, 'companyName').text
			jobSnippet = job.find_element(By.CLASS_NAME, 'job-snippet').text
			datePosted = job.find_element(By.CLASS_NAME, 'date').text
			datePosted = datePosted[7:] if datePosted[0:6] == 'Posted' else datePosted[9:]
			#add job to jobList as a new Listing
			jobList.append(Listing(texts[1].text, companyName,jobSnippet, datePosted, [], indeed_url))
driver.close()
#set up web driver from simplyhired.com
driver = webdriver.Chrome(executable_path='/Users/archiejones/Downloads/chromedriver')
driver.get(simply_hired_url)

#find relevant jobs
jobs = driver.find_element(By.CLASS_NAME, 'jobs')
joblist = jobs.find_elements(By.CSS_SELECTOR, 'li')
for job in joblist:
	companyName = None
	quals = []
	date = None
	#navigate through jobs and click on link to get more information
	job.find_element(By.CSS_SELECTOR, 'a').click()
	jobName = job.find_element(By.CSS_SELECTOR, 'a').text
	#wait for website to load each element so scraping is effective
	time.sleep(.5)
	#find company name
	spans = job.find_elements(By.TAG_NAME, 'span')
	for span in spans:
		if span.get_attribute('class') == 'JobPosting-labelWithIcon jobposting-company':
			companyName = span.text
	#get right pane with more information about job
	right_class = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div/div[2]/div/div')
	li = right_class.find_elements(By.TAG_NAME, 'li')
	for item in li:
		#find qualifications
		if item.get_attribute('class') == 'viewjob-qualification':
			quals.append(item.text)
	#get job snippet
	snippet =job.find_element(By.CLASS_NAME, 'jobposting-snippet').text
	spans = right_class.find_elements(By.TAG_NAME, 'span')
	for span in spans:
		#get date posted
		if span.get_attribute('class') == 'viewjob-labelWithIcon viewjob-age':
			date = span.text
			
			
	jobList.append(Listing(jobName, companyName, snippet, date, quals, simply_hired_url))
	
	
		
	
driver.close()








# Sending email section
email_from = 'archiejobsearch@gmail.com'
password = 'jobsearch123'
email_to = 'jonesarchie37@gmail.com'

date_str = pd.Timestamp.today().strftime('%d/%m/%Y')

htmlJobs = ''''''
for job in jobList:
	newHtml = f'''
		<h1>{job.listing_name}</h1>
		<h1>{job.companyName}</h1>
		<p>Snippet: {job.jobSnippet}</p>
		<p>Date posted: {job.datePosted}</p>
		<p>Qualifications: {', '.join(job.quals) if len(job.quals) != 0 else 'No qualifications provided'}</p>
		<a href = '{job.url}'>
		driver = {job.url}</a>
	'''
	htmlJobs += (newHtml)


html = f'''
    <html>
        <body>
            {htmlJobs}
        </body>
    </html>
    '''
email_message = MIMEMultipart()
email_message['From'] = email_from
email_message['To'] = email_to
email_message['Subject'] = f'Job Listing Report for {date_str}'

email_message.attach(MIMEText(html, "html"))

email_string = email_message.as_string()

context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
	server.login(email_from, password)
	server.sendmail(email_from, email_to, email_string)

	
