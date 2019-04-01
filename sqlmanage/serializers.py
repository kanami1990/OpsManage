#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from sqlmanage.models import *

class SqlMonDBInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SqlMon_DB
        fields = ('id','db_role','db_owner','db_type','db_ip','db_port','db_user','db_passwd','db_name')

class SqlMonSQLInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SqlMon_Sql
        fields = ('id','sql_key','sql_tag','sql_db','sql_info','sql_enabled')