from django.conf.urls import url
from . import views
from api.views import (dns_api)
urlpatterns = [
            url(r'^add/$', views.addZone),
            url(r'^list/$', views.listZone),
            url(r'^zone/$', views.zones),
            url(r'^zone/(?P<id>[0-9]+)/$', views.zone_detail),
            url(r'^record_view/(?P<aid>[0-9]+)/$',views.listRecord),
            url(r'^updateRR/$', dns_api.update_rr),
            url(r'^delRecord/$', dns_api.del_record),
            url(r'^add_record/$', dns_api.add_record),

            # url(r'^app_list/$', views.app_list),
            # url(r'^message/$', views.send_msg),
            # url(r'^listlog/$', views.alert_list),
    ]