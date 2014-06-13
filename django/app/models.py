# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class Address(models.Model):
    id = models.IntegerField(primary_key=True)    
    street_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'address'

class Company(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    class Meta:
        managed = False
        db_table = 'company'

class Crime(models.Model):
    id = models.IntegerField(primary_key=True)
    address = models.ForeignKey(Address)
    incident_num = models.IntegerField(unique=True)
    occurred = models.DateTimeField()
    category = models.CharField(max_length=200, blank=True)
    description = models.CharField(max_length=200, blank=True)
    class Meta:
        managed = False
        db_table = 'crime'

# NOTE: the model name is different from the table name
class House(models.Model):
    id = models.IntegerField(primary_key=True)
    address = models.ForeignKey(Address)
    price = models.DecimalField(max_digits=9, decimal_places=0)
    source = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'housing'

class Job(models.Model):
    id = models.IntegerField(primary_key=True)
    company = models.ForeignKey(Company)
    address = models.ForeignKey(Address)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'job'

class JobRating(models.Model):
    id = models.IntegerField(primary_key=True)
    job = models.ForeignKey(Job)
    score = models.IntegerField(blank=True, null=True)
    review = models.TextField(blank=True)
    created = models.CharField(max_length=100, blank=True)
    class Meta:
        managed = False
        db_table = 'job_rating'

class JobSalary(models.Model):
    id = models.IntegerField(primary_key=True)
    job = models.ForeignKey(Job)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    class Meta:
        managed = False
        db_table = 'job_salary'

