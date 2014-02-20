from django.conf.urls import patterns, include, url

from persistence.api.v1 import amber_api as amber_api_v1
import persistence.views

urlpatterns = patterns('',
    url(r'^v1/checkpoint/', persistence.views.checkpoint, name='checkpoint'),
    url(r'^', include(amber_api_v1.urls)),
)
