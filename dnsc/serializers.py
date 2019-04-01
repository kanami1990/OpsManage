#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from .models import *

class DnsZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dns_Zone
        fields = ('id','dns_tag','dns_server','domain_zone','zone_key','zone_secret')

class NginxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nginx
        fields = ('id','ng_tag','ng_server_id','ng_config_path','ng_log_path','ng_status')

# class WeChatLogSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = WeChat_send_msg_log
#         fields = ('id','msg_source','msg_content','msg_status','msg_title')