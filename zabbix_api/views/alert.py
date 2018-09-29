#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import random,os
from OpsManage.utils import base
from django.http import HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from zabbix_api.models import (ZabbixAlert)
from orders.models import Order_System
from zabbix_api.models import Zabbix_Config
from django.contrib.auth.decorators import permission_required

@login_required(login_url='/login')
@permission_required('ZabbixAlert.can_read_zabbix',login_url='/noperm/')
def alert_list(request):
    if request.method == 'GET':
        orderList = ZabbixAlert.objects.order_by("id")
        return render(request,'zabbix/alert_list.html',{"orderList":orderList})