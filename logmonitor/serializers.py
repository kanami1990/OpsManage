#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from logmonitor.models import *

class LogListSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogSignup
        fields = ('id', 'log_tag', 'log_ip', 'log_path', 'log_userid', 'log_groups', 'log_systag')