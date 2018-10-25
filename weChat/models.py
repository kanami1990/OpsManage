# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class WeChat_App(models.Model):
    '''微信App'''
    app_type = models.CharField(max_length=20,verbose_name='app类型',unique=True,null=False)
    app_name = models.CharField(max_length=20,verbose_name='app名称',null=False)
    app_agentid = models.IntegerField(verbose_name='appAgentId',null=False)
    app_secret = models.CharField(max_length=50,verbose_name='appSecret',null=False)
    app_corpid = models.CharField(max_length=20, verbose_name='组织ID',null=False)
    app_mark = models.CharField(max_length=200, blank=True, null=True)
    app_token = models.CharField(max_length=250, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = 'opsmanage_wechat_app'
        permissions = (
            ("can_read_wechat_app", "读取微信app信息权限"),
            ("can_change_wechat_app", "更改微信app信息权限"),
            ("can_add_wechat_app", "添加微信app信息权限"),
            ("can_delete_wechat_app", "删除微信app信息权限"),
        )
        verbose_name = '微信App信息表'
        verbose_name_plural = '微信App信息表'


class WeChat_send_msg_log(models.Model):
    '''微信App'''
    msg_source = models.CharField(max_length=20,verbose_name='app来源',null=False)
    msg_title = models.CharField(max_length=100,verbose_name='app来源',blank=True,null=True)
    msg_content = models.TextField(verbose_name='消息内容',null=False)
    msg_status = models.CharField(max_length=20,verbose_name='发送状态',null=False)
    create_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'opsmanage_wechat_sendmsg_log'
        permissions = (
            ("can_read_wechat_log", "读取微信log信息权限"),
            ("can_change_wechat_log", "更改微信log信息权限"),
            ("can_add_wechat_log", "添加微信log信息权限"),
            ("can_delete_wechat_log", "删除微信log信息权限"),
        )
        verbose_name = '微信log信息表'
        verbose_name_plural = '微信log信息表'