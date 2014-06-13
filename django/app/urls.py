from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url(r'^companies/$', 'company_list'),
    url(r'^crimes/$', 'crime_list'),
    url(r'^houses/$', 'house_list'),
    url(r'^jobs/$', 'job_list'),
    url(r'^weights/$', 'weight_list')
)

