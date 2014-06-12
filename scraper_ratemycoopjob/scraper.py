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

    class Meta:
        db_table    = 'companies'

class Job(MySQLModel):
    company         = ForeignKeyField(Company)
    title           = CharField(max_length=100)
    description     = TextField(null=True)
    
    class Meta:
        db_table    = 'jobs'

class Address(MySQLModel):
    owner_id        = IntegerField()
    type            = IntegerField()
    street_address  = CharField(max_length=200, null=True)
    city            = CharField(max_length=100)
    country         = CharField(max_length=100)
    longitude       = DecimalField(max_digits=18, decimal_places=12, null=True)
    latitude        = DecimalField(max_digits=18, decimal_places=12, null=True)
    
    class Meta:
        db_table    = 'addresses'

class Rating(MySQLModel):
    owner_id        = IntegerField()
    type            = IntegerField()
    rating          = IntegerField(null=True)
    review          = TextField(null=True)
    created         = DateField()
    
    class Meta:
        db_table    = 'ratings'

class Salary(MySQLModel):
    job             = ForeignKeyField(Job)
    amount          = DecimalField(max_digits=9, decimal_places=2)
    
    class Meta:
        db_table    = 'salaries'

#------------------------------------------------------------------------------
# Scraper
#------------------------------------------------------------------------------

class Scraper:
    current_company_id = -1
    current_job_id     = -1
    current_address_id = -1

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
            return True
        else:
            return False

    def parse_job_info_box(self, soup):
        raw_label       = soup.find('div', class_='job_title')
        company_name    = raw_label.find('a').string
        job_title       = raw_label.text.replace('at', '').replace(company_name, '').strip()
        job_location    = soup.find('span', text=re.compile('\s*Location:\s*')).find_next_sibling('span', class_='job_information_content').text.strip()
        job_description = soup.find('span', text=re.compile('\s*Job Description:\s*')).find_next_sibling('span', class_='job_information_content').text.strip()

        self.current_company_id = Scraper.save_company(company_name)
        self.current_job_id     = Scraper.save_job(self.current_company_id, job_title, job_description)
        self.current_address_id = Scraper.save_address(self.current_job_id, job_location)

    def parse_job_rating_list(self, soup):
        job_listings = soup.find_all('div', class_='job_rating_box')
        for listing in job_listings:
            rating     = listing.find('div', class_='job_rating')
            comment    = listing.find('div', class_='job_rating_comment')
            raw_salary = listing.find('div', class_='job_rating_salary_label')

            created = comment.find('span', class_='rating_date').text.strip()
            review  = comment.text.replace(created, '').strip()
            salary  = re.findall(r'\d+', raw_salary.text)[0]

            Scraper.save_rating(self.current_job_id, rating, review, created, salary)

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
    def save_job(company_id, job_title, job_description):
        try:
            job = Job.select().where(Job.company == company_id, Job.title == job_title).get()
        except Job.DoesNotExist:
            job = Job()
            job.company = company_id
            job.title = job_title
            job.description = job_description
            job.save()
        return job.id

    @staticmethod
    def save_address(job_id, job_location):
        try:
            address = Address.select().where(Address.owner_id == job_id).get()
        except Address.DoesNotExist:
            job_location_params = job_location.split(',')
            address = Address()
            address.owner_id = job_id
            address.type = JOB_TYPE
            address.city = job_location_params[0]
            address.country = job_location_params[-1]
            address.save()
        return address.id

    @staticmethod
    def save_rating(job_id, rating, review, created, salary_amount):
        try:
            rating = Rating.select().where(Rating.owner_id == job_id, Rating.review == review).get()
        except Rating.DoesNotExist:
            rating = Rating()
            rating.owner_id = job_id
            rating.type = JOB_TYPE
            rating.review = review
            rating.created = created
            rating.save()

            salary = Salary()
            salary.job = job_id
            salary.amount = salary_amount
            salary.save()
        return rating.id

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

setup_logging()

scraper = Scraper()
scraper.run()
