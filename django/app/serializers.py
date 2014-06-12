from django.forms import widgets
from rest_framework import serializers
from app.models import Companies


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Companies
        fields = ('id', 'name')