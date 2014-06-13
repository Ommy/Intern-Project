from django.forms import widgets
from rest_framework import serializers
from app.models import Companies, Crimes, Addresses


class CompanySerializer(serializers.ModelSerializer):
	address = AddressSerializer()
    class Meta:
        model = Companies
        fields = ('id', 'name', 'address')

class CrimeSerilizer(serializers.ModelSerializer):
	address = AddressSerializer()
	class Meta:
		model = Crimes
		fields = ('id', 'occurred', 'address', 'occurred', 'description')

class AddressSerializer(serializers.ModelSerializer):
	class Meta: 
		model = Addresses
		fields = ('street_address', 'city',  'country', 'longitude', 'latitude')
