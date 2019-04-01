#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import StreamingHttpResponse,HttpResponse
from django.contrib.auth.models import Group
from sqlmanage.models import (SqlMon_DB)

@login_required()
@permission_required('sqlmanage.can_read_sqlmon_dbinfo',login_url='/noperm/')
def db_config(request):
    if request.method == 'GET':
        dbinfoList = SqlMon_DB.objects.all()
        groupList = Group.objects.all()
        # serverList = Assets.objects.filter(assets_type='server').filter(status=0)
        return render(request,'sqlmanage/db_config.html',{'dblist':dbinfoList,"groupList":groupList})
