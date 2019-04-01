#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from sqlmanage import serializers
from sqlmanage.models import (SqlMon_Sql)

@api_view(['POST'])
@permission_required('sqlmanage.can_add_sqlmon_sqlinfo',raise_exception=True)
def sql_list(request,format=None):
    if request.method == 'POST':
        serializer = serializers.SqlMonSQLInfoSerializer(data=request.data)
        if not request.data['sql_info'][-1] == ';':
            return Response({'data':'sql必须以\';\'结尾'},status=status.HTTP_400_BAD_REQUEST)
        elif not request.data['sql_info'].find(';') == len(request.data['sql_info'])-1:
            return Response({'data': '只能提交一条SQL'}, status=status.HTTP_400_BAD_REQUEST)
        elif '*' in request.data['sql_info']:
            return Response({'data': '* is not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        # elif ',' in request.data['sql_info']:
        #     return Response({'data': '仅支持单返回SQL'}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT','DELETE'])
@permission_required('sqlmanage.can_change_sqlmon_sqlinfo',raise_exception=True)
def sql_detail(request,id,format=None):
    try:
        snippet = SqlMon_Sql.objects.get(id=id)
    except SqlMon_Sql.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        if not request.data['sql_info'][-1] == ';':
            return Response({'data':'sql必须以\';\'结尾'},status=status.HTTP_400_BAD_REQUEST)
        elif not request.data['sql_info'].find(';') == len(request.data['sql_info'])-1:
            return Response({'data': '只能提交一条SQL'}, status=status.HTTP_400_BAD_REQUEST)
        elif '*' in request.data['sql_info']:
            return Response({'data': '* is not allowed'}, status=status.HTTP_400_BAD_REQUEST)
        # elif ',' in request.data['sql_info']:
        #     return Response({'data': '仅支持单返回SQL'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = serializers.SqlMonSQLInfoSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    if request.method == 'DELETE':
        if not request.user.has_perm('sqlmanage.can_delete_sqlmon_sqlinfo'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
