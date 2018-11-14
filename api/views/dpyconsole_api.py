# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from dao.itop import ItopSource
import jenkins,json
from deployconsole import serializers
from deployconsole.models import *

@api_view(['POST' ])
# @permission_required('dns.can_change_dns_zone',raise_exception=True)
def take_req(request):
    reqId = request.data['rid']
    its = ItopSource()
    objectDict={}
    its.pending_objects_by_requestid('DeployRequest',objectDict,reqId)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST' ])
def close_req(request):
    reqId = request.data['rid']
    its = ItopSource()
    objectDict = {}
    x = its.close_object_by_requestid('DeployRequest',objectDict,reqId)
    print x
    return Response(status=status.HTTP_200_OK)

@api_view(['POST' ])
@permission_required('deployconsole.can_add_dpy_app',raise_exception=True)
def do_task(request):
    if request.method == 'POST':
        try:
            jenkinsinfo = Jenkins_Config.objects.get(id=1)
            if jenkinsinfo.user and jenkinsinfo.passwd:
                server = jenkins.Jenkins(jenkinsinfo.host, username=jenkinsinfo.user, password=jenkinsinfo.passwd)
            else:
                server = jenkins.Jenkins(jenkinsinfo.host)
        except:
            return Response({'rtnMsg': 'jenkins配置不存在'}, status=status.HTTP_404_NOT_FOUND)
        taskname = request.data['dpy_jk_appname']
        params = {}
        if server.job_exists(taskname):
            # print server.get_job_info(taskname)['nextBuildNumber']
            objDict = request.data.copy()
            objDict['dpy_cnt'] = server.get_job_info(taskname)['nextBuildNumber']
            snippet = dpy_log.objects.filter(dpy_id=request.data['dpy_id'],
                                                 dpy_jk_appname=request.data['dpy_jk_appname'],
                                                 dpy_no=request.data['dpy_no']).first()
            if snippet:
                serializer = serializers.dpyLogSerializer(snippet,data=objDict)
                if serializer.is_valid():
                    serializer.save()
                    server.build_job(taskname, parameters=params)
                    return Response({'rtnMsg': 'jenkins任务已提交,记录更新'}, status=status.HTTP_200_OK)
                else:
                    return Response({'rtnMsg': '数据入库错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                serializer = serializers.dpyLogSerializer(data=objDict)
                if serializer.is_valid():
                    serializer.save()
                    server.build_job(taskname, parameters=params)
                    return Response({'rtnMsg': 'jenkins任务已提交，记录新建'}, status=status.HTTP_200_OK)
                else:
                    return Response({'rtnMsg': '数据入库错误'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'rtnMsg':'jenkins任务不存在'},status=status.HTTP_404_NOT_FOUND)