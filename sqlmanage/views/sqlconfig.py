#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import StreamingHttpResponse,HttpResponse
from sqlmanage.models import (SqlMon_Sql,SqlMon_DB)

@login_required()
@permission_required('sqlmanage.can_read_sqlmon_sqlinfo',login_url='/noperm/')
def sql_config(request):
    if request.method == 'GET':
        sqlList = SqlMon_Sql.objects.all()
        dblist = SqlMon_DB.objects.all()
        return render(request,'sqlmanage/sql_config.html',{'sqlList':sqlList,"dblist":dblist})