#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import json,requests
from django.http import JsonResponse,StreamingHttpResponse
from django.utils.encoding import smart_unicode
from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group,User
from OpsManage.utils.logger import logger
from dao import itop
from deployconsole.models import *
import jenkins

@login_required(login_url='/login')
def request_view(request,aid):
    iconn = itop.ItopSource()
    res = iconn.query_by_id('DeployRequest',aid,None)
    resDict = json.loads(res)
    orgDict = resDict['objects']
    try:
        jenkinsList = Jenkins_Config.objects.all()
    except:
        jenkinsList = []
    try:
        jid = task_jk.objects.filter(rid=int(aid)).first()
        jenkinsSourceDict = Jenkins_Config.objects.get(id=jid.jid)
        jenkinsSource = jenkinsSourceDict.tag
        jkvalue = jenkinsSourceDict.id
    except:
        jenkinsSource = jkvalue = ''
    if orgDict:
        for jekninstask in orgDict['DeployRequest::{}'.format(aid)]['fields']['jenkins_task']:
            snippet = dpy_log.objects.filter(dpy_id=aid,
                                             dpy_jk_appname=jekninstask['jk_appname'],
                                             dpy_no=jekninstask['jk_dpno']).first()
            if snippet:
                print snippet.dpy_time
                jekninstask['dpy_time'] = snippet.dpy_time
                jekninstask['dpy_cnt'] = snippet.dpy_cnt
        #     # pass
        return render(request,'deployconsole/dpyreq_view.html',{"dpyRequest":orgDict['DeployRequest::{}'.format(aid)]['fields'],"jenkinsList":jenkinsList,"jenkinsSource":jenkinsSource,"jkvalue":jkvalue})
    else:
        return render(request,'deployconsole/dpyreq_view.html',{"aid":aid})

@login_required(login_url='/login')
# @permission_required('deployconsole.can_add_dpy_app',raise_exception=True)
def review_output(request,jid,tname,tid):
    jenkinsinfo = Jenkins_Config.objects.get(id=int(jid))
    if jenkinsinfo.user and jenkinsinfo.passwd:
        server = jenkins.Jenkins(jenkinsinfo.host,username=jenkinsinfo.user,password=jenkinsinfo.passwd)
    else:
        server = jenkins.Jenkins(jenkinsinfo.host)
    try:
        output = server.get_build_console_output(tname, int(tid))
        return render(request, 'deployconsole/jenkinsoutput.html', {"output": smart_unicode(output)})
    except:
        return render(request, 'deployconsole/jenkinsoutput.html', {"output": u'任务编号不存在'})
