#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from django.db import models
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

class ZabbixAlert(models.Model):
    send_flag_choices = (
        ('sended',u'已发送'),
        ('error',u'错误'),
    )
    event_id = models.BigIntegerField(null=False,verbose_name='事件Id',unique=True)
    send_to = models.CharField(max_length=200,verbose_name='收件人')
    subject = models.CharField(max_length=200,verbose_name='邮件标题')
    message = models.TextField(verbose_name='邮件正体')
    send_flag = models.CharField(choices=send_flag_choices,max_length=100,default='sended',verbose_name='发送状态')
    class Meta:
        db_table = 'zabbix_alert_sendlog'
        permissions = (
            ("can_read_zabbix", "读取zabbix信息"),
            ("can_change_zabbix", "更改zabbix信息"),
            ("can_add_zabbix", "添加zabbix信息"),
            ("can_delete_zabbix", "删除zabbix信息"),
            ("can_dumps_zabbix", "导出zabbix信息"),
        )
        verbose_name = 'zabbix报警发送记录表'
        verbose_name_plural = 'zabbix报警发送记录表'

class Zabbix_Config(models.Model):
    site = models.CharField(max_length=100,verbose_name='部署站点')
    host = models.CharField(max_length=100,verbose_name='zabbixapi服务器')
    port = models.SmallIntegerField(verbose_name='zabbixapi服务器端口')
    user = models.CharField(max_length=100,verbose_name='zabbix用户账户')
    passwd = models.CharField(max_length=100,verbose_name='zabbix用户密码')
    userid = models.SmallIntegerField(null=True, verbose_name='认证用户id')
    token = models.CharField(null=True,max_length=50, verbose_name='认证用户token')
    class Meta:
        db_table = 'opsmanage_zabbix_config'