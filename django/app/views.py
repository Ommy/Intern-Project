from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from app.models import Address, Company, Crime, House, Job, JobRating, JobSalary
from app.serializers import AddressSerializer, CompanySerializer, CrimeSerializer, HouseSerializer, JobSerializer, JobRatingSerializer, JobSalarySerializer


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def company_list(request):
    if request.method == 'GET':
    	companies = Company.objects.all()
    	serializer = CompanySerializer(companies, many=True)
    	return JSONResponse(serializer.data)

def crime_list(request):
    if request.method == 'GET':
        crimes = Crime.objects.all()
        serializer = CrimeSerializer(crimes, many=True)
        return JSONResponse(serializer.data)

def house_list(request):
    if request.method == 'GET':
        house = House.objects.all()
        serializer = HouseSerializer(house, many=True)
        return JSONResponse(serializer.data)

def job_list(request):
    if request.method == 'GET':
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return JSONResponse(serializer.data)
