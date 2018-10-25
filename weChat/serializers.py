#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from .models import *

class WeChatAppSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChat_App
        fields = ('id','app_type','app_name','app_agentid','app_secret','app_mark','app_corpid')

class WeChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeChat_send_msg_log
        fields = ('id','msg_source','msg_content','msg_status','msg_title')