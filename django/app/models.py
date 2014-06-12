from django.db import models

class Addresses(models.Model):
    id = models.IntegerField(primary_key=True)
    owner_id = models.IntegerField()
    type = models.IntegerField()
    street_address = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    longitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    latitude = models.DecimalField(max_digits=18, decimal_places=12, blank=True, null=True)
    class Meta:
        db_table = 'addresses'

class Companies(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    class Meta:
        db_table = 'companies'

class Housing(models.Model):
    id = models.IntegerField(primary_key=True)
    price = models.DecimalField(max_digits=10, decimal_places=0)
    source = models.IntegerField()
    class Meta:
        db_table = 'housing'

class Jobs(models.Model):
    id = models.IntegerField(primary_key=True)
    company = models.ForeignKey(Companies)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    class Meta:
        db_table = 'jobs'

class Ratings(models.Model):
    id = models.IntegerField(primary_key=True)
    owner_id = models.IntegerField()
    type = models.IntegerField()
    rating = models.IntegerField(blank=True, null=True)
    review = models.TextField(blank=True)
    created = models.CharField(max_length=100, blank=True)
    class Meta:
        db_table = 'ratings'

class Salaries(models.Model):
    id = models.IntegerField(primary_key=True)
    job = models.ForeignKey(Jobs)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    class Meta:
        db_table = 'salaries'
