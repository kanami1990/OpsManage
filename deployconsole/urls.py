# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import (console,request,jenkins2)
from api.views import (dpyconsole_api)
urlpatterns = [
            url(r'^list/$', console.deploy_console),
            url(r'^dpytask_view/(?P<aid>[0-9]+)/$',request.request_view),
            url(r'^take_req/$',dpyconsole_api.take_req),
            url(r'^close_req/$',dpyconsole_api.close_req),
            url(r'^do_task/$',dpyconsole_api.do_task),
            url(r'^mod_jktask/$',dpyconsole_api.mod_jktask),
            url(r'^taskoutput/(?P<jid>[\S]+)/(?P<tname>[\S]+)/(?P<tid>[0-9]+)/$',request.review_output),
            url(r'^jenkins_list/$',jenkins2.jenkins_list),
            url(r'^jenkins_list/(?P<id>[0-9]+)/$', jenkins2.jenkins_detail),
            url(r'^add_jenkins/$',jenkins2.add_jenkins),
    ]
