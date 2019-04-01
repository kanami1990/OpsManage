# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class SqlMon_DB(models.Model):
    '''监控DB基础信息表'''
    type = (
        ('1', u'Mysql'),
        ('2', u'Oracle'),
    )
    db_role = models.CharField(max_length=20, verbose_name='db角色', null=False)
    db_owner = models.SmallIntegerField(verbose_name='db租户', null=False)
    db_type = models.SmallIntegerField(choices=type,verbose_name='db类型',default=1)
    db_ip = models.GenericIPAddressField(verbose_name='IP',null=False)
    db_port = models.IntegerField(verbose_name='端口',null=False)
    db_user = models.CharField(max_length=40, verbose_name='db用户', null=False)
    db_passwd = models.CharField(max_length=40, verbose_name='db密码', null=False)
    db_name = models.CharField(max_length=40, verbose_name='db库名', null=False)
    class Meta:
        db_table = 'sqlmon_dbinfo'
        permissions = (
            ("can_read_sqlmon_dbinfo", "读取监控DB表权限"),
            ("can_change_sqlmon_dbinfo", "更改监监控DB表权限"),
            ("can_add_sqlmon_dbinfo", "添加监控DB表权限"),
            ("can_delete_sqlmon_dbinfo", "删除监控DB表权限"),
        )
        unique_together = (("db_port", "db_ip", "db_owner", "db_name"))
        verbose_name = '监控DB基础信息表'
        verbose_name_plural = '监控DB基础信息表'

class SqlMon_Sql(models.Model):
    '''监控sql配置表'''
    enabled = (
        ('0',u'True'),
        ('1', u'False'),
    )
    sql_key = models.CharField(max_length=10,verbose_name='zabbix查询键',unique=True,null=False)
    sql_tag = models.CharField(max_length=40,verbose_name='sql标签',null=False)
    sql_db = models.SmallIntegerField(verbose_name='db配置表id')
    sql_info = models.TextField(max_length=2000,verbose_name='sql内容')
    sql_enabled = models.SmallIntegerField(choices=enabled,verbose_name='sql开关',default=0)
    class Mate:
        db_table = 'sqlmon_sqlinfo'
        permissions = (
            ("can_read_sqlmon_sqlinfo", "读取监控sql权限"),
            ("can_change_sqlmon_sqlinfo", "更改监监控sql权限"),
            ("can_add_sqlmon_sqlinfo", "添加监控sql权限"),
            ("can_delete_sqlmon_sqlinfo", "删除监控sql权限"),
        )
    verbose_name = '监控SQL表'
    verbose_name_plural = '监控SQL表'