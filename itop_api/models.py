# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class ITOP_Config(models.Model):
    site = models.CharField(max_length=100,verbose_name='部署站点')
    host = models.CharField(max_length=100,verbose_name='itopapi服务器')
    # port = models.SmallIntegerField(verbose_name='zabbixapi服务器端口')
    user = models.CharField(max_length=100,verbose_name='itop用户账户')
    passwd = models.CharField(max_length=100,verbose_name='itop用户密码')
    # userid = models.SmallIntegerField(null=True, verbose_name='认证用户id')
    # token = models.CharField(null=True,max_length=50, verbose_name='认证用户token')
    class Meta:
        db_table = 'opsmanage_itop_config'