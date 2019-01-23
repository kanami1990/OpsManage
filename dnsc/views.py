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
from . import serializers
from dnsc.models import (Dns_Zone)
import dns.resolver,dns.zone,dns.tsigkeyring,dns.update

# Create your views here.
@permission_required('dnsc.can_read_dns_zone',login_url='/noperm/')
def listZone(request):
    try:
        zonelist = Dns_Zone.objects.all()
    except:
        zonelist = []
    return render(request, 'dns/zone_list.html', {'zonelist':zonelist})

def addZone(request):
    return render(request, 'dns/zone_add.html', {})

@api_view(['GET', 'POST' ])
@permission_required('dnsc.can_add_dns_zone',raise_exception=True)
def zones(request):
    if request.method == 'POST':
        serializer = serializers.DnsZoneSerializer(data=request.data['data'])
        # print(request.data['data'])
        if serializer.is_valid():
            serializer.save()
            # recordAssets.delay(user=str(request.user), content="添加资产：{name}".format(name=request.data.get("name")),
            #                    type="assets", id=serializer.data.get('id'))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT','DELETE','GET'])
@permission_required('dnsc.can_add_dns_zone',raise_exception=True)
def zone_detail(request,id,format=None):
    try:
        snippet = Dns_Zone.objects.get(id=id)
    except Dns_Zone.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        print(request.data)
        serializer = serializers.DnsZoneSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not request.user.has_perm('dnsc.can_delete_dns_zone'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@permission_required('dnsc.can_read_dns_zone',login_url='/noperm/')
def listRecord(request,aid):
    try:
        zone = Dns_Zone.objects.get(id=aid)
        # key = zone.zone_key
        # secret = zone.zone_secret
        dns_host = zone.dns_server
        domain = zone.domain_zone
        # keyring = dnsc.tsigkeyring.from_text({key:secret})
        query = dns.zone.from_xfr(dns.query.xfr(dns_host,domain))
        dnsRRList = []
        for i in query.iterkeys():
            i =  i.to_text()
            if  '@'not in  i:
                tempDict = {}
                r = dns.resolver.query("{}.{}".format(i,domain),'A')
                tempDict['rr_record'] = i.__str__()
                tempDict['rr_ttl'] = r.__getattr__('ttl')
                tempDict['rr_type'] = 'A'
                tempDict['rr_value'] = []
                tempDict['rr_zid'] = aid
                for j in r.response.answer[0].items:
                    tempDict['rr_value'].append(j.address)
                dnsRRList.append(tempDict)
    except:
        dnsRRList = []
    return render(request, 'dns/record_list.html', {'recordlist':dnsRRList})