import urllib2
import re
import sys
import logging
import json

from peewee import *
from datetime import datetime
from bs4 import BeautifulSoup

#------------------------------------------------------------------------------
# Helpers
#------------------------------------------------------------------------------

SOURCE_URL = 'http://data.sfgov.org/resource/gxxq-x39z.json'
CITY       = 'San Francisco'
COUNTRY    = 'United States'
CRIME_TYPE = 2

def request_json(url):
    logging.info('Getting json of ' + url)
    try:
        request  = urllib2.Request(url) 
        jsonText = urllib2.urlopen(request).read()
        return json.loads(jsonText)
    except urllib2.HTTPError, err:
        logging.error('Received ' +  str(err.code) + ' error from ' + url)
        return None

def convert_to_seconds(clock):
    params = clock.split(':')
    hours = int(params[0])
    minutes = int(params[1])
    return (hours * 3600) + (minutes * 60)

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

class Address(MySQLModel):
    owner_id       = IntegerField()
    type           = IntegerField()
    street_address = CharField(max_length=200, null=True)
    city           = CharField(max_length=100)
    country        = CharField(max_length=100)
    longitude      = DecimalField(max_digits=18, decimal_places=12, null=True)
    latitude       = DecimalField(max_digits=18, decimal_places=12, null=True)
    
    class Meta:
        db_table   = 'addresses'

class Crime(MySQLModel):
    incident_num   = IntegerField()
    occurred       = DateTimeField()
    category       = CharField(max_length=200)
    description    = CharField(max_length=200)

    class Meta:
        db_table   = 'crimes'

#------------------------------------------------------------------------------
# Scraper
#------------------------------------------------------------------------------

class Scraper:
    def __init__(self):
        mysql_db.connect()

    def run(self):
        crimes = request_json(SOURCE_URL)
        for crime in crimes:
            Scraper.save_crime(
                int(crime['incidntnum']),
                datetime.fromtimestamp(int(crime['date']) + convert_to_seconds(crime['time'])),
                crime['category'].title(),
                crime['descript'].title(),
                crime['location']['longitude'],
                crime['location']['latitude']
            )

    @staticmethod
    def save_crime(incident_num, occurred, category, description, longitude, latitude):
        try:
            crime = Crime.select().where(Crime.incident_num == incident_num).get()
        except Crime.DoesNotExist:
            crime = Crime()
            crime.incident_num = incident_num
            crime.occurred = occurred
            crime.category = category
            crime.description = description
            crime.save()

            address = Address()
            address.owner_id = crime.id
            address.type = CRIME_TYPE
            address.city = CITY
            address.country = COUNTRY
            address.longitude = longitude
            address.latitude = latitude
            address.save()
        return crime.id

#------------------------------------------------------------------------------
# Main
#------------------------------------------------------------------------------

setup_logging()

scraper = Scraper()
scraper.run()