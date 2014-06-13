from django.forms import widgets
from rest_framework import serializers
from app.models import Address, Company, Crime, House, Job, JobRating, JobSalary


class AddressSerializer(serializers.ModelSerializer):
	class Meta: 
		model = Address
		fields = ('street_address', 'city',  'country', 'longitude', 'latitude')

class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name')

class CrimeSerializer(serializers.ModelSerializer):
	address = AddressSerializer()
	class Meta:
		model = Crime
		fields = ('id', 'address', 'incident_num', 'occurred', 'category', 'description')

class HouseSerializer(serializers.ModelSerializer):
	address = AddressSerializer()
	class Meta:
		model = House
		fields = ('id', 'address', 'price', 'source')

class JobSerializer(serializers.ModelSerializer):
	company = CompanySerializer()
	address = AddressSerializer()
	class Meta:
		model = Job
		fields = ('id', 'company', 'address', 'title', 'description')

class JobRatingSerializer(serializers.ModelSerializer):
	job = JobSerializer()
	class Meta:
		model = JobRating
		fields = ('id', 'job', 'source', 'review', 'created')

class JobSalarySerializer(serializers.ModelSerializer):
	job = JobSerializer()
	class Meta:
		model = JobRating
		fields = ('id', 'job', 'amount')
		