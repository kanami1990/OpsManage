# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import JsonResponse,StreamingHttpResponse
from django.shortcuts import render,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from weChat.models import (WeChat_App,WeChat_send_msg_log)
from . import serializers
from dao import wechat as wc

# Create your views here.
@login_required(login_url='/login')
@permission_required('weChat.can_read_wechat_log',login_url='/noperm/')
def alert_list(request):
    if request.method == 'GET':
        orderList = WeChat_send_msg_log.objects.all().order_by("-id")
        return render(request,'wechat/alert_list.html',{"orderList":orderList})

def addApp(request):
    return render(request, 'wechat/app_add.html', {})

@permission_required('weChat.can_read_wechat_app',login_url='/noperm/')
def listApp(request):
    try:
        applist = WeChat_App.objects.all()
    except:
        applist = []
    return render(request, 'wechat/app_list.html', {'applist':applist})

@api_view(['GET', 'POST' ])
@permission_required('weChat.can_add_wechat_app',raise_exception=True)
def apps(request):
    if request.method == 'POST':
        serializer = serializers.WeChatAppSerializer(data=request.data['data'])
        # print(request.data['data'])
        if serializer.is_valid():
            serializer.save()
            # recordAssets.delay(user=str(request.user), content="添加资产：{name}".format(name=request.data.get("name")),
            #                    type="assets", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST' ])
@permission_required('weChat.can_add_wechat_app',raise_exception=True)
def app_list(request):
    if request.method == 'GET':
        snippets = WeChat_App.objects.all()
        serializer = serializers.WeChatAppSerializer(snippets, many=True)
        return Response(serializer.data)

@api_view(['PUT','DELETE','GET'])
@permission_required('weChat.can_add_wechat_app',raise_exception=True)
def apps_detail(request,id,format=None):
    try:
        snippet = WeChat_App.objects.get(id=id)
    except WeChat_App.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        print(request.data)
        serializer = serializers.WeChatAppSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not request.user.has_perm('weChat.can_delete_wechat_app'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'GET':
        token = wc.getAccesstoken(snippet.app_corpid,snippet.app_secret)
        snippet.app_token = token
        snippet.save()
        return Response(status=status.HTTP_200_OK)

@api_view(['POST','GET'])
@permission_required('weChat.can_add_wechat_log',raise_exception=True)
def send_msg(request):
    if request.method == 'POST':
        print(request.data)
        appinfocnt = WeChat_App.objects.filter(app_type=request.data['msg_source']).count()
        if appinfocnt > 0:
            appinfo  = WeChat_App.objects.filter(app_type=request.data['msg_source']).first()

            wf = wc.weChatFunc()
            content = {'content':request.data['msg_content'],
                       'title':request.data.get('msg_title',''),
                       'url':request.data.get('msg_url','http://bing.com')}
            if wf.sendMSG(content,appinfo.app_agentid,appinfo.app_token):
                request.data['msg_status'] = u'发送成功'
                serializer = serializers.WeChatLogSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'rtnMsg':'200'},status=status.HTTP_200_OK)
                return Response({'rtnMsg': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                token = wc.getAccesstoken(appinfo.app_corpid, appinfo.app_secret)
                appinfo.app_token = token
                appinfo.save()
                if wf.sendMSG(content, appinfo.app_agentid, appinfo.app_token):
                    request.data['msg_status'] = u'更新Token发送成功'
                    serializer = serializers.WeChatLogSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                    return Response({'rtnMsg': '200'}, status=status.HTTP_200_OK)
                else:
                    request.data['msg_status'] = u'更新Token发送失败'
                    serializer = serializers.WeChatLogSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                    return Response({'rtnMsg': '500'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif request.method == 'GET':
        message = WeChat_send_msg_log.objects.all()
        serializer = serializers.WeChatLogSerializer(message,many=True)
        return Response(serializer.data)
    # elif request.method == 'POST':
    #     return Response(status=status.HTTP_201_CREATED)
