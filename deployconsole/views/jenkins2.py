#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from django.http import HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from deployconsole.models import (Jenkins_Config)
from deployconsole import serializers

@login_required(login_url='/login')
def jenkins_list(request):
    if request.method == 'GET':
        try:
            jenkinslist = Jenkins_Config.objects.all()
        except:
            jenkinslist = []
        return render(request, 'deployconsole/jenkins_list.html', {"jenkinslist": jenkinslist})

@api_view(['PUT','DELETE','GET'])
def jenkins_detail(request,id):
    try:
        snippet = Jenkins_Config.objects.get(id=id)
    except Jenkins_Config.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        print(request.data)
        serializer = serializers.JenkinsListSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def add_jenkins(request):
    if request.method == 'POST':
        serializer = serializers.JenkinsListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)