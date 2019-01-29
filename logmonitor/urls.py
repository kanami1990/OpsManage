from django.conf.urls import url
from . import (views)
from .api import (logmon_api)

urlpatterns = [
    url(r'^log/$', views.log_signup),
    url(r'^add/$', logmon_api.signuplog),
    url(r'^edit/(?P<id>[0-9]+)/$', logmon_api.editlog),
    url(r'^search/$', views.log_search),
    url(r'^show/(?P<id>[0-9]+)/$', views.log_show),
    url(r'^show2/(?P<id>[0-9]+)/$', views.log_show2),
    url(r'^filelist/(?P<id>[0-9]+)/$', views.file_list),

]