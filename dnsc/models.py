# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Dns_Zone(models.Model):
    '''DnsZone'''
    dns_tag = models.CharField(max_length=20,verbose_name='zone标签',unique=True,null=False)
    dns_server = models.CharField(max_length=20,verbose_name='dns服务器',null=False)
    domain_zone = models.CharField(max_length=20,verbose_name='域名',null=False)
    zone_key = models.CharField(max_length=20,verbose_name='zoneKey',null=False)
    zone_secret = models.CharField(max_length=50,verbose_name='zone密钥',null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'opsmanage_dns_zone'
        permissions = (
            ("can_read_dns_zone", "读取dns_zone权限"),
            ("can_change_dns_zone", "更改dns_zone权限"),
            ("can_add_dns_zone", "添加dns_zone权限"),
            ("can_delete_dns_zone", "删除dns_zone权限"),
        )
        verbose_name = 'dns_zone信息表'
        verbose_name_plural = 'dns_zone信息表'
