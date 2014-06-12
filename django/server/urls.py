from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
    (r'^$', TemplateView.as_view(template_name="index.html")),
    (r'^statics/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_URL}),
    (r'^api/', include('app.urls')),
)
