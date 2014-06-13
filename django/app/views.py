import math
import decimal

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

from app.models import Address, Company, Crime, House, Job, JobRating, JobSalary
from app.serializers import AddressSerializer, CompanySerializer, CrimeSerializer, HouseSerializer, JobSerializer, JobRatingSerializer, JobSalarySerializer


CRIME_SEVERITY = { 
    'Arson'                       : 4,
    'Assault'                     : 6,
    'Burglary'                    : 5,
    'Disorderly Conduct'          : 3,
    'Drunkenness'                 : 2,
    'Driving Under The Influence' : 4,
    'Drug/Narcotic'               : 7,
    'Forgery/Counterfeiting'      : 1,
    'Fraud'                       : 1,
    'Gambling'                    : 1,
    'Kidnapping'                  : 8,
    'Larceny/Theft'               : 7,
    'Missing Person'              : 8,
    'Non-Criminal'                : 0,
    'Other Offenses'              : 2,
    'Prostitution'                : 4,
    'Robbery'                     : 5,
    'Runaway'                     : 0,
    'Sex Offenses, Forcible'      : 8,
    'Suspicious Occ'              : 4,
    'Trespass'                    : 3,
    'Vandalism'                   : 4,
    'Vehicle Theft'               : 8,
    'Warrants'                    : 2,
    'Weapon Laws'                  : 5
}

LOOKOUT_LAT = 37.791841
LOOKOUT_LONG = -122.398637
MAX_SEVERITY = 10

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
        houses = House.objects.all()
        serializer = HouseSerializer(houses, many=True)
        return JSONResponse(serializer.data)

def job_list(request):
    if request.method == 'GET':
        jobs = Job.objects.all()
        serializer = JobSerializer(jobs, many=True)
        return JSONResponse(serializer.data)


def weight_list(request):
    if request.method == 'GET':
        safety = float(request.GET.get('safety', None))

        max_distance =  float(request.GET.get('distance[max]', None))
        min_distance = float(request.GET.get('distance[min]', None))
        max_price = float(request.GET.get('price[max]', None))
        min_price = float(request.GET.get('price[min]', None))

        houses = House.objects.all()
        crimes = Crime.objects.all()

        house_in_range = []
        for house in houses:
            work_distance = coordinatesToMiles(house.address.latitude, house.address.longitude , LOOKOUT_LAT, LOOKOUT_LONG)
            price = float(house.price)
            if ((work_distance <= max_distance 
               and work_distance >= min_distance)
               and (price <= max_price
               and price >= min_price)):
                distance_score = (work_distance/max_distance)
                price_score = (price/max_price)
                crime_count = 0
                crime_score = 0
                for crime in crimes:
                    crime_distance = coordinatesToMiles(house.address.latitude, house.address.longitude , crime.address.latitude, crime.address.longitude)
                    if crime_distance <= work_distance:
                        crime_distance_score = (work_distance - crime_distance)/work_distance
                        severity = CRIME_SEVERITY[crime.category]
                        crime_score += severity*crime_distance_score
                crime_score = (MAX_SEVERITY*work_distance)/(crime_score)
                weight = (crime_score*safety) + distance_score + price_score
                house_in_range.append([float(house.address.latitude), float(house.address.longitude), weight])
        return JSONResponse(house_in_range)


"""
HELPER FUNCTION
"""
def coordinatesToMiles(lat1, long1, lat2, long2):

    lat1 = float(lat1)
    long1 = float(long1)
    lat2 = float(lat2)
    long2 = float(long2)

    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
        
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
        
    # Compute spherical distance from spherical coordinates.
        
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc*3960