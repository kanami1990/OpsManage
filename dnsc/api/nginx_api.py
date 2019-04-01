# Created by redial at 2019-03-28
# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from dnsc.models import (Nginx,Nginx_Server,Dns_Zone)
from dnsc import serializers
from OpsManage.utils.nginx_util import genNginxConfig
from OpsManage.models import Server_Assets
from OpsManage.utils.ansible_api_v2 import ANSRunner
import dns.resolver,dns.zone,dns.tsigkeyring,dns.update

@api_view(['PUT','DELETE','GET'])
@permission_required('dnsc.can_add_nginx',raise_exception=True)
def nginx_detail(request,id,format=None):
    try:
        snippet = Nginx.objects.get(id=id)
    except Nginx.DoesNotExist:
        return Response({'rtnMsg': 'Nginx不存在'},status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        if snippet.ng_server_id != int(request.data['ng_server_id']):
            try:
                nssize = len(Nginx_Server.objects.filter(ns_ng_id=id))
            except:
                nssize = 0
            if not nssize == 0:
                return Response({'rtnMsg': 'Remove All Old Server under this Nginx first'},status=status.HTTP_501_NOT_IMPLEMENTED)
        if request.data['ng_config_path'] and request.data['ng_log_path'] and request.data['ng_tag'] and request.data['ng_server_id']:
            Nginx.objects.filter(id=id).update(ng_config_path = request.data['ng_config_path'],
                                                   ng_log_path = request.data['ng_log_path'],
                                                   ng_tag = request.data['ng_tag'],
                                                   ng_server_id = request.data['ng_server_id']
                                                   )
            return Response({'rtnMsg': 'Nginx Modify Ok'})
        return Response({'rtnMsg': 'Meta Data Error'}, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if not request.user.has_perm('dnsc.can_delete_nginx'):
            return Response({'rtnMsg': '权限校验失败'},status=status.HTTP_403_FORBIDDEN)
        snippet.delete()
        return Response({'rtnMsg': 'Nginx已删除'},status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_required('dnsc.can_add_nginx',raise_exception=True)
def nginx(request):
    if request.method == 'POST':
        ng_tag = request.data['ng_tag']
        ng_server_id = request.data['ng_server_id']
        ng_config_path = request.data['ng_config_path']
        ng_log_path = request.data['ng_log_path']
        Nginx.objects.create(ng_tag=ng_tag,
                                   ng_server_id=ng_server_id,
                                   ng_config_path=ng_config_path,
                                   ng_log_path=ng_log_path,
                                   ng_status=0
                             )
        return Response({'rtnMsg': 'Nginx Add ok'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_required('dnsc.can_add_nginx',raise_exception=True)
def nginx_server(request):
    if request.method == 'POST':
        print request.data
        ns_rr = request.data['ns_rr']
        ns_domain_id = request.data['ns_domain_id']
        ns_rport = request.data['ns_rport']
        ns_sport = request.data['ns_sport']
        ns_sip_id = request.data['ns_sip_id']
        ns_ng_id = request.data['ns_ng']
        if  not (0<int(ns_rport)<65535 and 0<int(ns_sport)<65535):
            return Response({'rtnMsg': 'Port Range is not allowed'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            domain_info = Dns_Zone.objects.get(id=ns_domain_id)
            nginx_info = Nginx.objects.get(id=ns_ng_id)
            server_info = Server_Assets.objects.get(id=ns_sip_id)
        except:
            return Response({'rtnMsg': 'Meta info Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:

            (filename,conffilepath) = genNginxConfig(ns_rr,domain_info.domain_zone,ns_sport,server_info.ip,ns_rport,'',nginx_info.ng_log_path)
            # print conffilepath
            resource = [{"ip": nginx_info.ng_server.ip, "port": 22, "username": nginx_info.ng_server.username}]
            ANS = ANSRunner(resource)
            dest='{}{}'.format(nginx_info.ng_config_path,filename)
            sList = [nginx_info.ng_server.ip]
            file_args = """src={src} dest={dest} owner={user} group={user} mode=644""".format(src=conffilepath, dest=dest,
                                                                                              user='root')
            # print file_args
            ANS.run_model(host_list=sList, module_name="copy", module_args=file_args)


            # print ANS.get_model_result()
            systemctl_args = """name=nginx state=reloaded"""
            ANS.run_model(host_list=sList, module_name="systemd", module_args=systemctl_args)
            # print ANS.get_model_result()

            key = domain_info.zone_key
            secret = domain_info.zone_secret
            domain = domain_info.domain_zone
            dns_host = domain_info.dns_server
            keyring = dns.tsigkeyring.from_text({key: secret})
            update = dns.update.Update(domain, keyring=keyring)
            update.add(ns_rr, 86400, 'a', nginx_info.ng_server.ip)
            dns.query.tcp(update, dns_host)

            Nginx_Server.objects.create(ns_rr=ns_rr,
                                        ns_rport=ns_rport,
                                        ns_sport=ns_sport,
                                        ns_sip_id=int(ns_sip_id),
                                        ns_status=0,
                                        ns_ng_id=int(ns_ng_id),
                                        ns_domain_id=int(ns_domain_id)
                                 )
        except Exception,e:
            return Response({'rtnMsg': e.__str__()}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'rtnMsg': 'Nginx Server Add ok'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_required('dnsc.can_add_nginx',raise_exception=True)
def nginx_server_detail(request,id):
    try:
        snippet = Nginx_Server.objects.get(id=id)
    except Nginx.DoesNotExist:
        return Response({'rtnMsg': 'Nginx Server不存在'},status=status.HTTP_404_NOT_FOUND)
    if request.method == 'DELETE':
        if not request.user.has_perm('dnsc.can_delete_nginx'):
            return Response({'rtnMsg': '权限校验失败'}, status=status.HTTP_403_FORBIDDEN)
        ns_rr = snippet.ns_rr
        ns_domain = snippet.ns_domain
        ns_rport = snippet.ns_rport
        ns_sport = snippet.ns_sport
        ns_ng = snippet.ns_ng

        filepath = '{}{}.{}_{}_{}.conf'.format(ns_ng.ng_config_path,ns_rr,ns_domain.domain_zone,ns_sport,ns_rport)
        resource = [{"ip": ns_ng.ng_server.ip, "port": 22, "username": ns_ng.ng_server.username}]
        ANS = ANSRunner(resource)
        file_args = """state=absent path={}""".format(filepath)
        ANS.run_model(host_list=[ns_ng.ng_server.ip], module_name="file", module_args=file_args)
        systemctl_args = """name=nginx state=reloaded"""
        ANS.run_model(host_list=[ns_ng.ng_server.ip], module_name="systemd", module_args=systemctl_args)
        snippet.delete()
        return Response({'rtnMsg': 'Nginx已删除'}, status=status.HTTP_200_OK)