# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class LogSignup(models.Model):
    '''日志登陆记录表'''
    log_tag = models.CharField(max_length=50, verbose_name='日志标签', null=False)
    log_ip = models.GenericIPAddressField(verbose_name='日志所在服务器',null=False)
    log_path = models.CharField(max_length=250, verbose_name='日志路径', null=False)
    log_userid = models.SmallIntegerField(verbose_name='登陆日志所有者',null=False)
    log_groups = models.CharField(max_length=250, verbose_name='登陆日志所有者组', null=False)
    log_systag = models.CharField(max_length=250, verbose_name='日志系统分类', null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'logmonitor_logsignup'
        permissions = (
            ("can_read_LogSign", "读取登陆日志信息权限"),
            ("can_change_LogSign", "更改登陆日志信息权限"),
            ("can_add_LogSign", "添加登陆日志信息权限"),
            ("can_delete_LogSign", "删除登陆日志信息权限"),
        )
        verbose_name = '日志登陆记录表'
        verbose_name_plural = '日志登陆记录表'