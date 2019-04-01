from django.conf.urls import url
from . import views
from dnsc.api import dns_api,nginx_api

urlpatterns = [
            url(r'^add/$', views.addZone),
            url(r'^list/$', views.listZone),
            url(r'^zone/$', views.zones),
            url(r'^zone/(?P<id>[0-9]+)/$', views.zone_detail),
            url(r'^record_view/(?P<aid>[0-9]+)/$',views.listRecord),
            url(r'^updateRR/$', dns_api.update_rr),
            url(r'^delRecord/$', dns_api.del_record),
            url(r'^add_record/$', dns_api.add_record),
            url(r'^nginx/$', views.listNginx),
            url(r'^add_nginx/$', nginx_api.nginx,name='nginx_add'),
            url(r'^nginx/(?P<id>[0-9]+)/$', nginx_api.nginx_detail),
            url(r'^ns_view/(?P<id>[0-9]+)/$', views.listNginxServer),
            url(r'^add_nginx_server/$', nginx_api.nginx_server,name='nginxserver_add'),
            url(r'^nginx_server/(?P<id>[0-9]+)/$', nginx_api.nginx_server_detail),

            # url(r'^app_list/$', views.app_list),
            # url(r'^message/$', views.send_msg),
            # url(r'^listlog/$', views.alert_list),
    ]