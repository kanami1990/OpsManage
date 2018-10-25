from django.conf.urls import url
from . import views
urlpatterns = [
            url(r'^add/$', views.addApp),
            url(r'^list/$', views.listApp),
            url(r'^app/$', views.apps),
            url(r'^app/(?P<id>[0-9]+)/$', views.apps_detail),
            url(r'^app_list/$', views.app_list),
            url(r'^message/$', views.send_msg),
            url(r'^listlog/$', views.alert_list),
    ]