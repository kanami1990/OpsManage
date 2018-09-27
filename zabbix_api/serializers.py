#!/usr/bin/env python  
# _#_ coding:utf-8 _*_  
from rest_framework import serializers
from zabbix_api.models import *

class ZabbixAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZabbixAlert
        fields = ('id','event_id','send_to','subject','message')
    def create(self, data):
        alertllog = ZabbixAlert.objects.create(**data)
        return alertllog
