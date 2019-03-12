# Created by redial at 2019-03-01
# _#_ coding:utf-8 _*_
from rest_framework import serializers
from djcelery.models  import CrontabSchedule,IntervalSchedule
from .models import (Tenant_passwd,Backup_Task)

class TenantPassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant_passwd
        fields = ('id','bc_name_id','bc_passwd')

class BackupTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup_Task
        fields = ('id', 'bt_minute', 'bt_hour', 'bt_day', 'bt_week', 'bt_month')