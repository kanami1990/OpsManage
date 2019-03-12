# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import Group,User
from OpsManage.models import Server_Assets
from django.db import models

class Tenant_rule(models.Model):
    bc_name = models.OneToOneField(Group)
    bc_minute = models.CharField(max_length=10, verbose_name='分', default=None)
    bc_hour = models.CharField(max_length=10, verbose_name='时', default=None)
    bc_day = models.CharField(max_length=10, verbose_name='天', default=None)
    bc_week = models.CharField(max_length=10, verbose_name='周', default=None)
    bc_month = models.CharField(max_length=10, verbose_name='月', default=None)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'opsmanage_bakcons_tenant_rule'
        permissions = (
            ("can_read_tenant_rule", "读取租户规则信息权限"),
            ("can_change_tenant_rule", "更改租户规则信息权限"),
            ("can_add_tenant_rule", "添加租户规则信息权限"),
            ("can_delete_tenant_rule", "删除租户规则信息权限"),
        )
        verbose_name = '租户规则表'
        verbose_name_plural = '租户规则表'

class Tenant_passwd(models.Model):
    bc_name = models.OneToOneField(Group)
    bc_passwd = models.CharField(max_length=20, verbose_name='密码', blank=False)
    class Meta:
        db_table = 'opsmanage_bakcons_tenant_passwd'
        verbose_name = '租户密码表'
        verbose_name_plural = '租户密码表'

class Rsync_Config(models.Model):
    server = models.GenericIPAddressField(verbose_name='备份服务器', null=False)
    base_bak_path = models.CharField(max_length=50, verbose_name='基础路径', blank=False)
    bak_user= models.CharField(max_length=20, verbose_name='全局基础用户', blank=False)
    config_path = models.CharField(max_length=50, verbose_name='config文件路径', blank=False)
    pass_path = models.CharField(max_length=50, verbose_name='pass文件路径', blank=False)
    class Meta:
        db_table = 'opsmanage_bakcons_rsync_config'

class Backup_Task(models.Model):
    bt_group = models.ForeignKey(Group,verbose_name='租户信息')
    bt_user = models.ForeignKey(User,verbose_name='用户信息')
    bt_asset = models.ForeignKey(Server_Assets,verbose_name='服务器信息')
    bt_name = models.CharField(max_length=50, verbose_name='任务名称', blank=False)
    bt_source_path = models.CharField(max_length=50, verbose_name='源路径', blank=False)
    bt_minute = models.CharField(max_length=10, verbose_name='分', default=None)
    bt_hour = models.CharField(max_length=10, verbose_name='时', default=None)
    bt_day = models.CharField(max_length=10, verbose_name='天', default=None)
    bt_week = models.CharField(max_length=10, verbose_name='周', default=None)
    bt_month = models.CharField(max_length=10, verbose_name='月', default=None)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'opsmanage_bakcons_backup_task'
        permissions = (
            ("can_read_backup_task", "读取备份任务权限"),
            ("can_change_backup_task", "更改备份任务权限"),
            ("can_add_backup_task", "添加备份任务权限"),
            ("can_delete_backup_task", "删除备份任务权限"),
        )
        verbose_name = '备份任务表'
        verbose_name_plural = '备份任务表'