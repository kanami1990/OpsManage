#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import json,requests
from django.http import JsonResponse,StreamingHttpResponse
from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group,User
from OpsManage.utils.logger import logger
from dao import itop

@login_required(login_url='/login')
def request_view(request,aid):
    iconn = itop.ItopSource()
    res = iconn.query_by_id('DeployRequest',aid,None)
    resDict = json.loads(res)
    orgDict = resDict['objects']
    if orgDict:
        return render(request,'deployconsole/dpyreq_view.html',{"dpyRequest":orgDict['DeployRequest::{}'.format(aid)]['fields']})
    else:
        return render(request,'deployconsole/dpyreq_view.html',{"aid":aid})