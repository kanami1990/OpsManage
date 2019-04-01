# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from OpsManage.models import Server_Assets

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

class Nginx(models.Model):
    '''Nginx_List'''
    ng_tag = models.CharField(max_length=20,verbose_name='nginx标签',unique=True,null=False)
    ng_server = models.ForeignKey(Server_Assets,verbose_name='nginx服务器')
    ng_config_path = models.CharField(max_length=50,verbose_name='nginx配置基础路径',null=False)
    ng_log_path = models.CharField(max_length=50,verbose_name='nginx日志基础路径',null=False)
    ng_status = models.SmallIntegerField(verbose_name='nginx状态',null=False,default=0)
    class Meta:
        db_table = 'opsmanage_nginx'
        permissions = (
            ("can_read_nginx", "读取nginx权限"),
            ("can_change_nginx", "更改nginx权限"),
            ("can_add_nginx", "添加nginx权限"),
            ("can_delete_nginx", "删除nginx权限"),
        )
        verbose_name = 'nginx信息表'
        verbose_name_plural = 'nginx信息表'

class Nginx_Server(models.Model):
    ns_ng = models.ForeignKey(Nginx,verbose_name='Nginx服务器')
    ns_rr = models.CharField(max_length=20,verbose_name='二级域名',unique=True,null=False)
    ns_domain = models.ForeignKey(Dns_Zone,verbose_name='主域名')
    ns_rport = models.CharField(max_length=5,verbose_name='远程端口',default='80')
    ns_sport = models.CharField(max_length=5,verbose_name='本地端口',default='80')
    ns_sip = models.ForeignKey(Server_Assets,verbose_name='远程服务器',null=False)
    ns_status = models.SmallIntegerField(verbose_name='状态',null=False,default=0)
    class Meta:
        db_table = 'opsmanage_nginx_server'
        unique_together = (("ns_ng", "ns_rr","ns_rport"))
        verbose_name = 'nginx代理表'
        verbose_name_plural = 'nginx代理表'