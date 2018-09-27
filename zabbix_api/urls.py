from django.conf.urls import url
from .views import (alert_api)
urlpatterns = [
            url(r'^alert/$', alert_api.alert_list),
            url(r'^alert/(?P<id>[0-9]+)/$', alert_api.alert_detail),
    ]