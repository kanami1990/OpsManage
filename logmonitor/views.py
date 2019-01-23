# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse,HttpResponseForbidden
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
import operator
from logmonitor.models import (LogSignup)
from OpsManage.models import Assets,Server_Assets

# Create your views here.
@login_required()
@permission_required('logmonitor.can_read_LogSign',login_url='/noperm/')
def log_signup(request):
    if request.method == 'GET':
        userid = request.user.id
        groups = ','.join(request.user.groups.values_list('name',flat=True))
        gids = request.user.groups.values_list('id',flat=True)
        query = reduce(operator.and_, (Q(log_groups__contains = g_name) for g_name in request.user.groups.values_list('name',flat=True)))
        loglist = LogSignup.objects.filter(query)
        assetsList = Assets.objects.filter(assets_type='server',status=0,group__in=gids)
        serverList = [{'management_ip': a.server_assets.ip} for a in assetsList]
        print serverList
        return render(request,'logmonitor/loglist.html',{'loglist':loglist, 'userid':userid, 'groups':groups,'serverList':serverList})

def log_search(request):
    if request.method == 'GET':
        sysmodList = [m.log_systag for m in LogSignup.objects.raw('SELECT id,log_systag from logmonitor_logsignup WHERE log_systag is not null  GROUP BY log_systag')]
        return render(request, 'logmonitor/log_search.html', {'sysmodList':sysmodList})
    elif request.method == 'POST':
        try:
            sys_mod = request.POST.get('sysmod')
            query = reduce(operator.and_, (Q(log_groups__contains=g_name) for g_name in
                                           request.user.groups.values_list('name', flat=True)))
            loglist = LogSignup.objects.filter(query).filter(log_systag=sys_mod)
            dataList = []
            for log in loglist:
                opt = '''
                <a href="/logmon/show/{id}" style="text-decoration:none;" target="_blank"><button  type="button" class="btn btn-default"><abbr title="查看日志"><i class="glyphicon glyphicon-screenshot"></button></i></abbr></a>
                '''.format(id=log.id)
                dataList.append(
                    {
                     'ID': '<td class="text-center">{id}</td>'.format(id=log.id),
                     '日志标签': log.log_tag,
                     '系统标签': log.log_systag,
                     '服务器': log.log_ip,
                     '路径': log.log_path,
                     '操作': opt}
                )
            return JsonResponse({'msg': "数据查询成功", "code": 200, 'data': dataList, 'count': 0})
        except:
            pass

@login_required()
@permission_required('logmonitor.can_read_LogSign',login_url='/noperm/')
def log_show(request,id):
    if request.method == 'GET':
        log_info = LogSignup.objects.get(id=id)
        log_gs = log_info.log_groups.split(',')
        user_gs = request.user.groups.values_list('name',flat=True)
        print log_gs
        print list(user_gs)
        if list(set(log_gs).intersection(user_gs)):

            return render(request,'logmonitor/log_show.html',{'id':id,'logname':'{}:{}'.format(log_info.log_ip,log_info.log_path)})
        else:
            return HttpResponseForbidden()

