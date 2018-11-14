#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from .models import *

class dpyLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = dpy_log
        fields = ('id','dpy_id','dpy_no','dpy_jk_appname','dpy_cnt')

