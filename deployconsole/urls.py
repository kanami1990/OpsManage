# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import (console,request)
urlpatterns = [
            url(r'^list/$', console.deploy_console),
            url(r'^dpytask_view/(?P<aid>[0-9]+)/$',request.request_view),
    ]
