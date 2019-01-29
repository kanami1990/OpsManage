#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import json
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from django.http import JsonResponse
from logmonitor import serializers
from logmonitor.models import (LogSignup)

@api_view(['POST'])
@permission_required('logmonitor.can_add_LogSign',raise_exception=True)
def signuplog(request):
    if request.method == 'POST':
        if not request.user.id == int(request.data['log_userid']):
            return Response({'msg':"用户请求id不匹配"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # return JsonResponse({'msg':"用户请求id不匹配","code":500,'data':[]})
        groups = (','.join(request.user.groups.values_list('name',flat=True)))
        if not groups == request.data['log_groups']:
            return Response({'msg': "用户请求组不匹配"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        logpath = request.data['log_path']
        # or '.log' != logpath.encode('utf-8')[-4:]
        if  ' ' in logpath.encode('utf-8').strip(' ') or '/' not in logpath.encode('utf-8'):
            return Response({'msg': "log路径非法，不能包含空格，填写完整路径"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        print(dict(request.data)['log_ip[]'])
        # serializer = serializers.LogListSerializer(data=request.data)
        tList = dict(request.data)['log_ip[]']
        fList = list(set(tList))
        for ip in fList:
            td = {}
            td['log_tag']=request.data['log_tag']
            td['log_systag']=request.data['log_systag']
            td['log_path']=request.data['log_path']
            td['log_userid']=request.data['log_userid']
            td['log_groups']=request.data['log_groups']
            td['log_ip']=ip
            serializer = serializers.LogListSerializer(data=td)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response({'msg': '部分失败'}, status=status.HTTP_207_MULTI_STATUS)
        return Response({'msg':'OK'}, status=status.HTTP_200_OK)

@api_view(['PUT','DELETE'])
@permission_required('logmonitor.can_change_LogSign',raise_exception=True)
def editlog(request,id):
    try:
        snippet = LogSignup.objects.get(id=id)
    except LogSignup.DoesNotExist:
        return Response({'msg': "无此记录"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        if not request.user.id == snippet.log_userid:
            return Response({'msg':"用户请求id不匹配，你不是该条记录的提交者"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = serializers.LogListSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':serializer.data})
        else:return Response({'msg':serializer.errors},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'DELETE':
        if not request.user.id == snippet.log_userid:
            return Response({'msg':"用户请求id不匹配，你不是该条记录的提交者"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not request.user.has_perm('logmonitor.can_delete_LogSign'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


