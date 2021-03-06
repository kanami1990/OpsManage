# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class dpy_log(models.Model):
    '''投产记录'''
    dpy_id = models.CharField(max_length=20,verbose_name='itop_reqid',null=False)
    dpy_no = models.CharField(max_length=20,verbose_name='itop_jkdpno',null=False)
    dpy_jk_appname = models.CharField(max_length=20,verbose_name='itop_jkappname',null=False)
    dpy_time = models.DateTimeField(auto_now=True)
    dpy_cnt = models.CharField(max_length=20, verbose_name='jenkins_cnt',null=False)
    dpy_status = models.CharField(max_length=20, blank=True)
    class Meta:
        db_table = 'dpyconsole_dpy_log'
        permissions = (
            ("can_read_dpy_app", "读取投产记录权限"),
            ("can_change_dpy_app", "更改投产记录权限"),
            ("can_add_dpy_app", "添加投产记录权限"),
            ("can_delete_dpy_app", "删除投产记录权限"),
        )
        verbose_name = '投产记录表'
        verbose_name_plural = '投产记录表'

class Jenkins_Config(models.Model):
    tag = models.CharField(max_length=100,verbose_name='jenkins标签')
    host = models.CharField(max_length=100,verbose_name='jenkins服务器')
    user = models.CharField(max_length=100,verbose_name='jenkins用户账户')
    passwd = models.CharField(max_length=100,verbose_name='jenkins用户密码')
    class Meta:
        db_table = 'opsmanage_jenkins_config'

class task_jk(models.Model):
    rid = models.SmallIntegerField(null=False,verbose_name='任务id')
    jid = models.SmallIntegerField(null=False,verbose_name='jenkinsid')
    class Meta:
        db_table = 'opsmanage_task_jk'