from django.conf.urls import patterns, url

urlpatterns = patterns('app.views',
    url(r'^companies/$', 'company_list'),
)