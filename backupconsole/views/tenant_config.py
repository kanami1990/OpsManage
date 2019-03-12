# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.db.models import Q
import operator
from backupconsole.models import Tenant_rule,Tenant_passwd


# Create your views here.


@login_required()
@permission_required('OpsManage.can_add_cron_config',login_url='/noperm/')
def tenant_add(request):
    query = reduce(operator.or_, (Q(id=gid) for gid in request.user.groups.values_list('id', flat=True)))
    tenantList = Group.objects.filter(query)
    if request.method == 'GET':
        return render(request, 'bakconsole/tenant_add.html', {"user": request.user, "tenantList": tenantList})
    if request.method == 'POST':
        id = request.POST.get('tenant_name')
        bc_minute = request.POST.get('cron_minute')
        bc_hour = request.POST.get('cron_hour')
        bc_day = request.POST.get('cron_day')
        bc_week = request.POST.get('cron_month')
        bc_month = request.POST.get('cron_week')
        try:
            tenant_rule = Tenant_rule.objects.create(bc_name_id=int(id),
                                                     bc_minute=bc_minute,
                                                     bc_hour=bc_hour,
                                                     bc_day=bc_day,
                                                     bc_week=bc_week,
                                                     bc_month=bc_month
                                                     )
        except Exception,e:
            tenant_rule = Tenant_rule.objects.filter(bc_name_id=int(id)).update(bc_minute=bc_minute,
                                                                                bc_hour=bc_hour,
                                                                                bc_day=bc_day,
                                                                                bc_week=bc_week,
                                                                                bc_month=bc_month
                                                                                )
            # return render(request, 'bakconsole/tenant_add.html', {"user": request.user, "tenantList": tenantList, "errorInfo":"提交失败，错误信息："+str(e)})
        return HttpResponseRedirect('/bakconsole/tenant_add/')

