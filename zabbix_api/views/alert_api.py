#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import json,re,traceback
from rest_framework import viewsets,permissions,status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import Http404,JsonResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required
from OpsManage.utils.logger import logger
from dao.alert import ZabbixSource
from zabbix_api import serializers
from zabbix_api.models import ZabbixAlert
from OpsManage.models import Email_Config
from OpsManage.utils import base


@api_view(['GET', 'POST' ])
@permission_required('OpsManage.can_add_project_assets',raise_exception=True)
def alert_list(request,format=None):
    if request.method == 'GET':
        zas = ZabbixAlert.objects.all()
        serializer = serializers.ZabbixAlertSerializer(zas, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        return None

@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('zabbix_api.can_read_zabbix',raise_exception=True)
def alert_detail(request, id,format=None):
    if request.method == 'GET':
        zs = ZabbixSource()
        if zs.queryLogbyEventid(id):
            (send_to,subject,message) = zs.queryAlertsbyEventid(id,None)
            zs.addLog(int(id),subject,str(send_to),message)

            config = Email_Config.objects.get(id=1)

            base.sendEmail(e_from=config.user,e_to=send_to,cc_to=None,
                   e_host=config.host,e_passwd=config.passwd,
                   e_sub=subject,e_content=message,format='plain')
            rtnMsg = {"send_to":send_to,"subject":subject,"message":message}
        else:
            rtnMsg = {"rtnCode":"300"}
        return Response(rtnMsg, status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)