# Created by redial at 2019-03-07
# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect,JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from backupconsole.models import (Backup_Task)
from OpsManage.models import (Assets)

@login_required()
@permission_required('OpsManage.can_add_cron_config',login_url='/noperm/')
def task_view(request):
    try:
        bak_task_list = Backup_Task.objects.all()
    except:
        bak_task_list = []
    try:
        if request.user.is_superuser:
            assetsList = Assets.objects.filter(assets_type='server', status=0)
        else:
            gids = request.user.groups.values_list('id', flat=True)
            assetsList = Assets.objects.filter(assets_type='server', status=0, group__in=gids)
    except:
        assetsList = []
    if request.method == 'GET':
        return render(request,'bakconsole/bak_task_list.html',{'bakTaskList':bak_task_list,'assetsList':assetsList})
