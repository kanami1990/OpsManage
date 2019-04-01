#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from sqlmanage import serializers
from sqlmanage.models import (SqlMon_DB)
from OpsManage.models import (Assets)

@api_view(['POST'])
@permission_required('sqlmanage.can_add_sqlmon_dbinfo',raise_exception=True)
def db_list(request,format=None):
    """
    create a sqlmon_db.
    """
    if request.method == 'POST':
        serializer = serializers.SqlMonDBInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT','DELETE'])
@permission_required('sqlmanage.can_change_sqlmon_dbinfo',raise_exception=True)
def db_detail(request,id,format=None):
    try:
        snippet = SqlMon_DB.objects.get(id=id)
    except SqlMon_DB.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = serializers.SqlMonDBInfoSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if not request.user.has_perm('sqlmanage.can_delete_sqlmon_dbinfo'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@permission_required('OpsManage.can_read_assets',login_url='/noperm/')
def assets(request):
    if request.method == "POST":
        dataList = []
        if request.POST.get('gid'):
            serverList = Assets.objects.filter(assets_type='server').filter(status=0).filter(group=int(request.POST.get('gid')))
            for host in serverList:
                dataList.append({"ip":host.management_ip})
        return JsonResponse({'msg':"主机查询成功","code":200,'data':dataList})
    else:JsonResponse({'msg':"不支持的操作","code":500,'data':[]})


@api_view(['PUT', 'DELETE'])
@permission_required('OpsManage.can_change_sqlmon_dbinfo', raise_exception=True)
def db_detail(request, id, format=None):
    """
    Retrieve, update or delete a server assets instance.
    """
    try:
        snippet = SqlMon_DB.objects.get(id=id)
    except SqlMon_DB.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = serializers.SqlMonDBInfoSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.has_perm('OpsManage.can_delete_sqlmon_dbinfo'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

