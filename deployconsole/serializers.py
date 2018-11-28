#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from .models import *

class dpyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = dpy_log
        fields = ('id','dpy_id','dpy_no','dpy_jk_appname','dpy_cnt')

class JenkinsListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(required=False)
    passwd = serializers.CharField(required=False)
    class Meta:
        model = Jenkins_Config
        fields = ('id','tag','host','user','passwd')

class taskjkSerializer(serializers.ModelSerializer):
    class Meta:
        model = task_jk
        fields = ('id','rid','jid')

