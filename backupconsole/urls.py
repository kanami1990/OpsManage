# Created by redial at 2019-02-27
# -*- coding: utf-8 -*-
from django.conf.urls import url
from .views import (tenant_config,task)
from .api import (tenant_api,task_api)

urlpatterns = [
            url(r'^tenant_add/$', tenant_config.tenant_add,name='tt_add'),
            url(r'^api/tplist/$', tenant_api.tenant_pass_list, name='bkapi_atp'),
            url(r'^api/tpmod/$', tenant_api.tenant_pass_mod, name='bkapi_mtp'),
            url(r'^api/taskadd/$', task_api.task_add,name='bktask_add'),
            url(r'^api/taskdel/$', task_api.task_del,name='bktask_del'),
            url(r'^api/regenconf/$', task_api.fix_config,name='bktask_rgc'),
            url(r'^api/taskmod/$', task_api.task_mod,name='bktask_mod'),
            url(r'^list/$', task.task_view,name='bktask_list'),
    ]