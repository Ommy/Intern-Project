import urllib2
import re
import sys
import logging
import time

from peewee import *
from bs4 import BeautifulSoup

#------------------------------------------------------------------------------
# Helpers
#------------------------------------------------------------------------------

BASE_URL            = 'http://ratemycoopjob.com/job/'
MAX_JOB_PAGE        = 510
JOB_TYPE            = 0
DELAY_BETWEEN_PAGES = 2 # seconds

def request_soup(url):
    logging.info('Getting soup of ' + url)
    try:
        request  = urllib2.Request(url) 
        htmlText = urllib2.urlopen(request).read()
        return BeautifulSoup(htmlText)
    except urllib2.HTTPError, err:
        logging.error('Received ' +  str(err.code) + ' error from ' + url)
        return None

def setup_logging():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

#------------------------------------------------------------------------------
# Models
#------------------------------------------------------------------------------

mysql_db = MySQLDatabase('intern_project', 
                host='localhost', 
                user='root', 
                passwd='root')

class MySQLModel(Model):
    class Meta:
        database = mysql_db

class Company(MySQLModel):
    name            = CharField()

class Address(MySQLModel):
    street_address  = CharField(max_length=200, null=True)
    city            = CharField(max_length=100)
    country         = CharField(max_length=100)
    longitude       = DecimalField(max_digits=18, decimal_places=12, null=True)
    latitude        = DecimalField(max_digits=18, decimal_places=12, null=True)

class Job(MySQLModel):
    company         = ForeignKeyField(Company)
    address         = ForeignKeyField(Address)
    title           = CharField(max_length=100)
    description     = TextField(null=True)

class Job_Rating(MySQLModel):
    job             = ForeignKeyField(Job)
    score           = IntegerField(null=True)
    review          = TextField(null=True)
    created         = CharField(max_length=100, null=True)

class Job_Salary(MySQLModel):
    job             = ForeignKeyField(Job)
    amount          = DecimalField(max_digits=9, decimal_places=2)

#------------------------------------------------------------------------------
# Scraper
#------------------------------------------------------------------------------

class Scraper:
    current_job_id = -1

    def __init__(self):
        mysql_db.connect()

    def run(self):
        for page in range(1, MAX_JOB_PAGE):
            self.scrape_job(page)
            time.sleep(DELAY_BETWEEN_PAGES)

    def scrape_job(self, page_number):
        url  = BASE_URL + str(page_number)
        soup = request_soup(url)
        if soup is not None:
            self.parse_job_info_box(soup.find(id='job_info_box'))
            self.parse_job_rating_list(soup.find(id='job_rating_list'))

    def parse_job_info_box(self, soup):
        raw_label       = soup.find('div', class_='job_title')
        company_name    = raw_label.find('a').string
        job_title       = raw_label.text.replace('at', '').replace(company_name, '').strip()
        job_location    = soup.find('span', text=re.compile('\s*Location:\s*')).find_next_sibling('span', class_='job_information_content').text.strip()
        job_description = soup.find('span', text=re.compile('\s*Job Description:\s*')).find_next_sibling('span', class_='job_information_content').text.strip()

        company_id          = Scraper.save_company(company_name)
        self.current_job_id = Scraper.save_job(company_id, job_title, job_location, job_description)

    def parse_job_rating_list(self, soup):
        job_listings = soup.find_all('div', class_='job_rating_box')
        for listing in job_listings:
            raw_score   = listing.find('div', class_='job_rating')
            raw_comment = listing.find('div', class_='job_rating_comment')
            raw_salary  = listing.find('div', class_='job_rating_salary_label')

            score   = int(float(raw_score.find('img')['alt'][:3]) * 2)
            created = raw_comment.find('span', class_='rating_date').text.strip()
            review  = raw_comment.text.replace(created, '').strip()
            salary  = re.findall(r'\d+', raw_salary.text)[0]

            Scraper.save_rating(self.current_job_id, score, review, created, salary)

    @staticmethod
    def save_company(company_name):
        try:
            company = Company.select().where(Company.name == company_name).get()
        except Company.DoesNotExist:
            company = Company()
            company.name = company_name
            company.save()
        return company.id

    @staticmethod
    def save_job(company_id, job_title, job_location, job_description):
        try:
            job = Job.select().where(Job.company == company_id, Job.title == job_title).get()
        except Job.DoesNotExist:
            job_location_params = job_location.split(',')
            address          = Address()
            address.city     = job_location_params[0]
            address.country  = job_location_params[-1]
            address.save()

            job             = Job()
            job.company     = company_id
            job.address     = address.id
            job.title       = job_title
            job.description = job_description
            job.save()
        return job.id

    @staticmethod
    def save_rating(job_id, score, review, created, salary_amount):
        try:
            job_rating = Job_Rating.select().where(Job_Rating.job == job_id, Job_Rating.review == review).get()
        except Job_Rating.DoesNotExist:
            job_rating         = Job_Rating()
            job_rating.job     = job_id
            job_rating.score   = score
            job_rating.review  = review
            job_rating.created = created
            job_rating.save()

            job_salary        = Job_Salary()
            job_salary.job    = job_id
            job_salary.amount = salary_amount
            job_salary.save()
        return job_rating.id

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

setup_logging()

scraper = Scraper()
scraper.run()
