from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from app.models import Companies
from app.serializers import CompanySerializer

class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)

@csrf_exempt
def company_list(request):
    if request.method == 'GET':
    	companies = Companies.objects.all()
    	serializer = CompanySerializer(companies, many=True)
    	return JSONResponse(serializer.data)