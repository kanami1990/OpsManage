from django.conf.urls import url
from .api import (db_api,sql_api,zabbix_api)
from .views import (dbconfig,sqlconfig)
urlpatterns = [
            url(r'^db/config/$', db_api.db_list),
            url(r'^db/config/(?P<id>[0-9]+)/$', db_api.db_detail),
            url(r'^db/list/$', dbconfig.db_config),
            url(r'^api/asset/$', db_api.assets),
            url(r'^sql/config/$', sql_api.sql_list),
            url(r'^sql/config/(?P<id>[0-9]+)/$', sql_api.sql_detail),
            url(r'^sql/list/$', sqlconfig.sql_config),
            url(r'^zabbix/query/$', zabbix_api.keyQuery),
            url(r'^zabbix/mquery/$', zabbix_api.sqlQuery),

            # url(r'^alert/(?P<id>[0-9]+)/$', alert_api.alert_detail),
    ]