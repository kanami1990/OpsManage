#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from django.http import HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from dao import itop
import json


# @login_required(login_url='/login')
def deploy_console(request):
    if request.method == 'GET':
        iconn = itop.ItopSource()
        dataModel = 'DeployRequest'
        OQL = "SELECT {} WHERE status IN ('assigned','pending','reassigned')".format(dataModel)
        fields = 'ref,project_team,deploy_windows,title'
        response = iconn.query_by_oql(dataModel,OQL,fields)
        resDict = json.loads(response)
        dpyReqIdList = []
        if resDict['objects']:
            for key,value in resDict['objects'].items():
                task = {}
                task['key'] = value['key']
                for item in fields.split(','):
                    task[item] = value['fields'][item]
                dpyReqIdList.append(task)
        return render(request,'deployconsole/dpyconsole.html',{"dpyReqIdList":dpyReqIdList})