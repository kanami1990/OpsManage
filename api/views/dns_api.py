#!/usr/bin/env python
# _#_ coding:utf-8 _*_

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from dnsc.models import *
import dns.resolver,dns.zone,dns.tsigkeyring,dns.update

@api_view(['POST' ])
@permission_required('dnsc.can_change_dns_zone',raise_exception=True)
def update_rr(request):
    if request.method == 'POST':
        if request.data['zid']:
            zone = Dns_Zone.objects.get(id=request.data['zid'])
            key = zone.zone_key
            secret = zone.zone_secret
            domain = zone.domain_zone
            dns_host = zone.dns_server
            keyring = dns.tsigkeyring.from_text({key: secret})
            update = dns.update.Update(domain, keyring=keyring)
            try:
                update.replace(request.data['rr_record'], int(request.data['rr_ttl']), 'a', request.data['rr_value'])
                dns.query.tcp(update, dns_host)
            except:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK)

@api_view(['POST' ])
@permission_required('dnsc.can_delete_dns_zone',raise_exception=True)
def del_record(request):
    if request.method == 'POST':
        if request.data['zid']:
            zone = Dns_Zone.objects.get(id=request.data['zid'])
            key = zone.zone_key
            secret = zone.zone_secret
            domain = zone.domain_zone
            dns_host = zone.dns_server
            keyring = dns.tsigkeyring.from_text({key: secret})
            update = dns.update.Update(domain, keyring=keyring)
            update.delete(request.data['rr_record'])
            dns.query.tcp(update, dns_host)
    return Response(status=status.HTTP_200_OK)

@api_view(['POST' ])
@permission_required('dnsc.can_add_dns_zone',raise_exception=True)
def add_record(request):
    if request.method == 'POST':
        if request.data['zid']:
            zone = Dns_Zone.objects.get(id=request.data['zid'])
            key = zone.zone_key
            secret = zone.zone_secret
            domain = zone.domain_zone
            dns_host = zone.dns_server
            keyring = dns.tsigkeyring.from_text({key: secret})
            update = dns.update.Update(domain, keyring=keyring)
            update.add(request.data['rr_record'], int(request.data['rr_ttl']), 'a', request.data['rr_value'])
            dns.query.tcp(update, dns_host)
    return Response(status=status.HTTP_200_OK)