#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import json,re,traceback
from rest_framework import viewsets,permissions
from itop_api import serializers
from dao.itop import ItopSource
from OpsManage.models import *
from rest_framework import status
from django.http import Http404
from django.contrib.auth.models import Group
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from OpsManage.tasks.assets import recordAssets
from django.contrib.auth.decorators import permission_required
from OpsManage.utils.logger import logger
from django.http import JsonResponse

def statusDecode(status):
    if status == u'运行':
        return 'production'
    else:
        return 'stock'

def osDecode(os):
    centos = '^[Cc]entOS'
    win = '^[Ww]indows'
    ubuntu = '^[Uu]buntu'
    if re.match(centos, os):
        verR = '\d\.\d+'
        ver = re.search(verR, os)
        if ver:
            return ['centos', ver.group()]
        else:
            return ['centos', '6.9']
    elif re.match(win,os):
        verR='\d{4} \w\d'
        ver = re.search(verR, os)
        if ver:
            return  ['windows',ver.group().lower()]
        else:
            return ['windows','2008 r2']
    elif re.match(ubuntu,os):
        verR = '\d\+.\d+'
        ver = re.search(verR, os)
        if ver:
            return ['ubuntu', ver.group()]
        else:
            return ['ubuntu', '18.04']
    else:
        return [None,None]

@api_view(['GET', 'POST' ])
@permission_required('OpsManage.can_add_project_assets',raise_exception=True)
def vm_list(request,format=None):
    if request.method == 'GET':
        return None
    elif request.method == 'POST':
        req_info = json.loads(request.body)
        try:
            its = ItopSource()
            dataModel = "VirtualMachine"
            x = json.loads(its.query_by_oql(dataModel, 'SELECT {} WHERE name=\'{}\''.format(dataModel, req_info['ip']), '*'))
            msgDict = {}
            msgDict['name'] = req_info['ip']
            msgDict['org_id'] = 'SELECT Organization'
            msgDict['status'] = statusDecode(req_info['status'])
            msgDict['virtualhost_id'] = 'SELECT VirtualHost WHERE name =\'cluster1\''
            msgDict['cpu'] = req_info['cpu']
            msgDict['ram'] = req_info['ram']
            msgDict['exc_hostname'] = req_info['hostname']
            msgDict['exc_host'] = req_info['host']
            msgDict['exc_user'] = req_info['user']
            msgDict['finalclass'] = 'VirtualMachine'
            [os_family, os_ver] = osDecode(req_info['os'])
            if os_family:
                x_osf = json.loads(
                    its.query_by_oql('OSFamily', 'SELECT OSFamily WHERE name LIKE \'%{}%\''.format(os_family), '*'))
                if not x_osf['objects']:
                    osfDict = {}
                    osfDict['name'] = os_family
                    osfDict['finalclass'] = 'OSFamily'
                    its.create_object_without_callerid('OSFamily', osfDict)
                msgDict['osfamily_id'] = 'SELECT OSFamily WHERE name LIKE \'%{}%\''.format(os_family)
                x_osv = json.loads(
                    its.query_by_oql('OSVersion', 'SELECT OSVersion WHERE name LIKE \'%{}%\''.format(os_ver), '*'))
                if not x_osv['objects']:
                    osvDict = {}
                    osvDict['name'] = os_ver
                    osvDict['osfamily_id'] = msgDict['osfamily_id']
                    osvDict['finalclass'] = 'OSVersion'
                    its.create_object_without_callerid('OSVersion', osvDict)
                msgDict['osversion_id'] = 'SELECT OSVersion WHERE name LIKE \'%{}%\''.format(os_ver)
            if x['objects']:
                filterDict = {}
                filterDict['name'] = req_info['ip']
                res = json.loads(its.update_object_by_dict(dataModel, msgDict, filterDict))
            else:
                res = json.loads(its.create_object_without_callerid(dataModel, msgDict))
            return Response(res, status=status.HTTP_200_OK)
        except:
            print(traceback.format_exc())
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_required('OpsManage.can_change_server_assets',raise_exception=True)
def vm_detail(request, id,format=None):
    return Response({"data":"1234"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_required('OpsManage.can_change_assets',raise_exception=True)
def assets_syncitop(request):
    if request.method == "POST":
        fList = []
        sList = []
        for ast in request.POST.getlist('assetsIds[]'):
            try:
                assets = Assets.objects.get(id=int(ast))
            except Exception, ex:
                logger.warn(msg="批量更新获取资产失败: {ex}".format(ex=str(ex)))
                continue
            if assets.assets_type in ['vmser','server']:
                try:
                    server_assets = Server_Assets.objects.get(assets=assets)
                except Exception, ex:
                    logger.warn(msg="批量更新获取服务器资产失败: {ex}".format(ex=str(ex)))
                    if server_assets.ip not in fList:fList.append(server_assets.ip)
                    continue
            if assets.put_zone:
                try:
                    zone = Zone_Assets.objects.get(id=int(assets.put_zone))
                except Exception, ex:
                    logger.warn(msg="批量更新获取服务器租户失败: {ex}".format(ex=str(ex)))
                    if server_assets.ip not in fList:fList.append(server_assets.ip)
                    continue

                exc_host = ''
                if 'cn-' not in zone.zone_name:
                    exc_host = 'ESXi'
                else:
                    exc_host = ''

                its = ItopSource()
                dataModel = "VirtualMachine"
                x = json.loads(
                    its.query_by_oql(dataModel, 'SELECT {} WHERE name=\'{}\''.format(dataModel, server_assets.ip), '*'))
                msgDict = {}
                msgDict['name'] = server_assets.ip
                msgDict['org_id'] = 'SELECT Organization'
                msgDict['status'] = statusDecode(u'运行')
                msgDict['virtualhost_id'] = 'SELECT VirtualHost WHERE name =\'cluster1\''
                msgDict['cpu'] = server_assets.cpu_core
                msgDict['ram'] = int(server_assets.ram_total) / 1024
                msgDict['exc_hostname'] = server_assets.hostname
                msgDict['exc_host'] = exc_host
                msgDict['exc_user'] = zone.zone_name
                msgDict['finalclass'] = 'VirtualMachine'
                [os_family, os_ver] = osDecode(server_assets.system)
                if os_family:
                    x_osf = json.loads(
                        its.query_by_oql('OSFamily', 'SELECT OSFamily WHERE name LIKE \'%{}%\''.format(os_family), '*'))
                    if not x_osf['objects']:
                        osfDict = {}
                        osfDict['name'] = os_family
                        osfDict['finalclass'] = 'OSFamily'
                        its.create_object_without_callerid('OSFamily', osfDict)
                    msgDict['osfamily_id'] = 'SELECT OSFamily WHERE name LIKE \'%{}%\''.format(os_family)
                    x_osv = json.loads(
                        its.query_by_oql('OSVersion', 'SELECT OSVersion WHERE name LIKE \'%{}%\''.format(os_ver), '*'))
                    if not x_osv['objects']:
                        osvDict = {}
                        osvDict['name'] = os_ver
                        osvDict['osfamily_id'] = msgDict['osfamily_id']
                        osvDict['finalclass'] = 'OSVersion'
                        its.create_object_without_callerid('OSVersion', osvDict)
                    msgDict['osversion_id'] = 'SELECT OSVersion WHERE name LIKE \'%{}%\''.format(os_ver)
                if x['objects']:
                    filterDict = {}
                    filterDict['name'] = server_assets.ip
                    res = json.loads(its.update_object_by_dict(dataModel, msgDict, filterDict))
                else:
                    res = json.loads(its.create_object_without_callerid(dataModel, msgDict))
                if 'Error' not in res:
                    if server_assets.ip not in sList: sList.append(server_assets.ip)
                else:
                    if server_assets.ip not in fList: fList.append(server_assets.ip)
        if sList:
            return JsonResponse({'msg': "测试成功", "code": 200, 'data': {"success": sList,"failed":fList}})
        else:
            return JsonResponse({'msg':"测试失败","code":500,'data':{"success": sList,"failed":fList}})