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
from dao.zabbix import ZabbixSource

@api_view(['POST' ])
# @permission_required('OpsManage.can_add_project_assets',raise_exception=True)
def add_user(request,format=None):
    username = request.data['username']
    zs = ZabbixSource()
    if zs.addUser(username):
        return Response(status=status.HTTP_201_CREATED)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)
