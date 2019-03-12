# Created by redial at 2019-03-01
# -*- coding: utf-8 -*-
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from backupconsole.models import Tenant_passwd
from backupconsole import serializers
from django.contrib.auth.models import Group

@api_view(['GET','POST' ])
@permission_required('backupconsole.can_read_tenant_rule',raise_exception=True)
def tenant_pass_list(request):
    if request.method == 'POST':
        gid = request.data['tenant_id']
        try:
            Tenant_passwd.objects.get(bc_name_id=int(gid))
            return Response({'msg': '已存在对应租户的密码，请使用密码修改功能'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Tenant_passwd.DoesNotExist:
            passwd = request.data['tenant_passwd']
            Tenant_passwd.objects.create(bc_name_id=int(gid),
                                         bc_passwd = passwd)
            return Response({'msg': 'OK'}, status=status.HTTP_200_OK)


@api_view(['PUT','DELETE' ])
@permission_required('backupconsole.can_change_tenant_rule',raise_exception=True)
def tenant_pass_mod(request):
    try:
        snippet = Tenant_passwd.objects.get(bc_name_id=int(request.data['bc_name_id']))
    except Tenant_passwd.DoesNotExist:
        return Response({'msg': "无此记录"}, status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = serializers.TenantPassSerializer(snippet,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'msg':serializer.data},status=status.HTTP_200_OK)
        else:
            return Response({'msg':serializer.errors},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if request.method == 'DELETE':
        if not request.user.has_perm('backupconsole.can_delete_tenant_rule'):
            return Response({'msg': 'no perm'}, status=status.HTTP_403_FORBIDDEN)
        else:
            snippet.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
