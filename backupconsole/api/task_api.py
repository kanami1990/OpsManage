# Created by redial at 2019-03-05
# -*- coding: utf-8 -*-
import ConfigParser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from OpsManage.models import Server_Assets
from django.contrib.auth.models import Group,User
from backupconsole.models import (Tenant_rule,Rsync_Config,Tenant_passwd,Backup_Task)
from OpsManage.utils.logger import logger
from OpsManage.utils import rsync
from OpsManage.utils.ansible_api_v2 import ANSRunner
import os,json,time
from backupconsole import serializers

@api_view(['GET','POST' ])
@permission_required('backupconsole.can_add_backup_task',raise_exception=True)
def task_add(request):
    if request.method == 'POST':
        if not request.user.has_perm('backupconsole.can_add_backup_task'):
            return Response(status.HTTP_403_FORBIDDEN)
        try:
            server_asset_id = request.data['server_asset_id']
            source_path = request.data['source_path'][:-1] if str(request.data['source_path']).endswith('/') else request.data['source_path']
            task_name = request.data['task_name']
            server_asset_info = Server_Assets.objects.get(id=server_asset_id)
            tenant_id = server_asset_info.assets.group
            tenant_info = Group.objects.get(id=tenant_id)
            user_id = request.user.id
            user_info = User.objects.get(id=user_id)
            default_rule = Tenant_rule.objects.get(bc_name_id=tenant_id)
        except Exception,e:
            logger.error(msg="必要信息不全: {ex}".format(ex=e))
            return Response({'rtnMsg':'必要信息不全'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            rsync_server = Rsync_Config.objects.get(id=1)
        except Rsync_Config.DoesNotExist,e:
            logger.info(msg="Rsync服务器未配置".format(ex=e))
            return Response({'rtnMsg': 'Rsync服务器未配置'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        tenant_name = tenant_info.name
        host_ip = server_asset_info.ip
        rhost_ip = rsync_server.server

        '''
        start process server config
        step1: copy rsync server config to opsmanage local
        step2: modify rsync config
        step3: transfile to rsync server
        setp4: mkdir bakpath on rsync server
        Note: if remove the rsync node ,the file which already on rsync server will not be deleted
        '''
        logger.info(msg='------------- start process server config -------------')
        resource = [{"ip": rsync_server.server, "port": 22, "username": rsync_server.bak_user}]
        ANS = ANSRunner(resource)
        sList = [rsync_server.server]
        # src = '/etc/rsyncd/rsyncd.conf'
        src = rsync_server.config_path
        dest = '/tmp/opsfile'
        file_args = """src={src} dest={dest}""".format(src=src, dest=dest)
        ANS.run_model(host_list=sList, module_name="fetch", module_args=file_args)
        resultDict = json.loads(ANS.get_model_result())
        if not resultDict['success'].has_key(rsync_server.server):
            logger.info(msg=json.dumps(resultDict))
            return Response({'rtnMsg': '下载 rsync 配置文件失败'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        rsync_config_path = '{}/{}{}'.format(dest,rhost_ip,src)
        if not os.path.exists(rsync_config_path):
            logger.info(msg="rsync服务器无法联通或找不到配置文件,{}".format(src))
            return Response({'rtnMsg':'rsync服务器无法联通或找不到配置文件,{}'.format(src)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        (rtnCode,tag_name,local_path) = rsync.addSection(rsync_server.base_bak_path,rsync_server.pass_path,rsync_config_path,source_path,host_ip,tenant_name)
        if rtnCode == 0:
            # src = rsync_config_path
            # dest = '/etc/rsyncd/rsyncd.conf'
            # file_args = """src={src} dest={dest} owner={user} group={user} mode=644""".format(src=src,dest=dest,user='opsadm')
            # ANS.run_model(host_list=sList, module_name="copy", module_args=file_args)
            # cmd_args = """name={service_name} state={state}""".format(service_name='xinetd',state='restarted')
            # ANS.run_model(host_list=sList, module_name="service", module_args=cmd_args)

            logger.info(msg='rtnMsg: rsync配置文件已存在节点 {}'.format(tag_name))
        if rtnCode == 1:
            src = rsync_config_path
            dest = rsync_server.config_path
            file_args = """src={src} dest={dest} owner={user} group={user} mode=644""".format(src=src, dest=dest,user=rsync_server.bak_user)
            ANS.run_model(host_list=sList, module_name="copy", module_args=file_args)
            logger.info(msg='rtnMsg: rsync配置文件已新增节点 {}'.format(tag_name))
            mkdir_args = """path={path} state={state}""".format(path=local_path, state='directory',owner=rsync_server.bak_user)
            ANS.run_model(host_list=sList, module_name="file", module_args=mkdir_args)
            logger.info(msg='rsync服务器已创建文件夹 {}'.format(local_path))
        logger.info(msg='------------- end process server config -------------')

        '''
        start process client
        step1: gen passwd file
        step2: transfile to client /home/opsadm
        step3: config client crontab
        '''
        if rtnCode == 1:
            logger.info(msg='------------- start process client crontab -------------')
            resource = [{"ip": server_asset_info.ip, "port": 22, "username": rsync_server.bak_user}]
            ANS = ANSRunner(resource)
            sList=[server_asset_info.ip]
            if not os.path.exists('/tmp/opsfile/{}'.format(tenant_name)):
                os.mkdir('/tmp/opsfile/{}'.format(tenant_name))
            passwd_file = '/tmp/opsfile/{}/rsync.passwd'.format(tenant_name)
            tenant_passwd_info = Tenant_passwd.objects.get(bc_name_id=tenant_id)
            with open(passwd_file, 'w+') as f:
                line = '{}:{}'.format(tenant_passwd_info.bc_name.name, tenant_passwd_info.bc_passwd)
                f.write('{}\n'.format(line))

            src = passwd_file
            dest = '/home/{}/rsyncd.passwd'.format(rsync_server.bak_user)
            file_args = """src={src} dest={dest} owner={user} group={user} mode=600""".format(src=src, dest=dest,
                                                                                              user=rsync_server.bak_user)
            ANS.run_model(host_list=sList, module_name="copy", module_args=file_args)

            rsync_cmd = 'rsync -az --progress {source_path} {tenant_name}@{rsync_server}::{tag_name} --password-file={passwd_file}'.format(source_path=source_path,
                                                                                                                                           tenant_name=tenant_name,
                                                                                                                                           rsync_server=rsync_server.server,
                                                                                                                                           tag_name=tag_name,
                                                                                                                                           passwd_file=dest)
            logger.info(msg='rsync_cmd: {}'.format(rsync_cmd))
            cron_args = """name={name} minute='{minute}' hour='{hour}' day='{day}' weekday='{weekday}' month='{month}' user='{user}' job='{job}'""".format(
                name=tag_name, minute=default_rule.bc_minute,
                hour=default_rule.bc_hour, day=default_rule.bc_day,
                weekday=default_rule.bc_week, month=default_rule.bc_month,
                user=rsync_server.bak_user, job=rsync_cmd
                )
            logger.info(msg='cron_args: {}'.format(cron_args))
            ANS.run_model(host_list=sList, module_name="cron", module_args=cron_args)

            Backup_Task.objects.create(bt_group_id=tenant_id,
                                       bt_user_id=user_id,
                                       bt_asset_id=server_asset_id,
                                       bt_name=task_name,
                                       bt_source_path=source_path,
                                       bt_minute=default_rule.bc_minute,
                                       bt_hour=default_rule.bc_hour,
                                       bt_day=default_rule.bc_day,
                                       bt_week=default_rule.bc_week,
                                       bt_month=default_rule.bc_month,)
        return Response({'rtnMsg': '已创建Crontab任务'})

# @api_view(['GET','POST' ])
# @permission_required('backupconsole.can_read_backup_task',raise_exception=True)
# def disable_cron(request,pid):
#     if request.method == 'POST':
#         #TODO ADD code query db by id to get backuptaskinfo then use tagname disable crontab
#         tag_name = '172.21.14.24-data-testls'
#         serverip = '172.21.14.24'
#         sList = [serverip]
#         resource = [{"ip": serverip, "port": 22, "username": 'opsadm'}]
#         ANS = ANSRunner(resource)
#         cron_args = """name='{name}' user='{user}' state={state}""".format(name=tag_name, user='opsadm',state='absent')
#         ANS.run_model(host_list=sList, module_name="cron", module_args=cron_args)
#         logger.info(msg=json.loads(ANS.get_model_result()))
#         return Response({'rtnMsg': 'debuging disable cron'})
#
#
# @api_view(['GET','POST' ])
# @permission_required('backupconsole.can_read_backup_task',raise_exception=True)
# def enable_cron(request,pid):
#     if request.method == 'POST':
#         tag_name = '172.21.14.24-data-testls'
#         serverip = '172.21.14.24'
#         sList = [serverip]
#         resource = [{"ip": serverip, "port": 22, "username": 'opsadm'}]
#         ANS = ANSRunner(resource)
#         rsync_cmd = 'rsync -az --progress {source_path} {tenant_name}@{rsync_server}::{tag_name} --password-file={passwd_file}'.format(
#             source_path='/data/testls',
#             tenant_name='DBA',
#             rsync_server='172.21.14.24',
#             tag_name=tag_name,
#             passwd_file='/home/opsadm/rsyncd.passwd')
#         cron_args = """name='{name}' minute='{minute}' hour='{hour}' day='{day}' weekday='{weekday}' month='{month}' user='{user}' job='{job}'""".format(
#             name=tag_name, minute='*/4',
#             hour='*', day='*',
#             weekday='*', month='*',
#             user='opsadm', job=rsync_cmd
#         )
#         logger.info(msg='cron_args: {}'.format(cron_args))
#         ANS.run_model(host_list=sList, module_name="cron", module_args=cron_args)
#         logger.info(msg=json.loads(ANS.get_model_result()))
#         return Response({'rtnMsg': 'debuging enable cron'})


@api_view(['GET','POST' ])
@permission_required('backupconsole.can_delete_backup_task',raise_exception=True)
def task_del(request):
    logger.info(msg='start funcfion taskdel')
    bid = request.data['bid']
    try:
        snippet = Backup_Task.objects.get(id=bid)
    except Backup_Task.DoesNotExist:
        return Response({'rtnMsg': '任务不存在'},status=status.HTTP_404_NOT_FOUND)
    '''
    start process server config
    step1: copy rsync server config to opsmanage local
    step2: modify rsync config
    step3: transfile to rsync server
    setp4: mkdir bakpath on rsync server
    Note: if remove the rsync node ,the file which already on rsync server will not be deleted
    '''
    rsync_server = Rsync_Config.objects.get(id=1)
    source_path = snippet.bt_source_path[:-1] if str(snippet.bt_source_path).endswith('/') else snippet.bt_source_path
    host_ip=snippet.bt_asset.ip
    rhost_ip = rsync_server.server
    tag_name='{}{}'.format(host_ip,source_path.replace('/','-'))
    tenant_name = snippet.bt_group.name
    logger.info(msg='tag_name={}'.format(tag_name))
    logger.info(msg='------------- start process server config -------------')
    resource = [{"ip": rsync_server.server, "port": 22, "username": rsync_server.bak_user}]
    ANS = ANSRunner(resource)
    sList = [rsync_server.server]
    src = rsync_server.config_path
    dest = '/tmp/opsfile'
    file_args = """src={src} dest={dest}""".format(src=src, dest=dest)
    ANS.run_model(host_list=sList, module_name="fetch", module_args=file_args)
    resultDict = json.loads(ANS.get_model_result())
    if not resultDict['success'].has_key(rsync_server.server):
        logger.info(msg=json.dumps(resultDict))
        return Response({'rtnMsg': '下载 rsync 配置文件失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    rsync_config_path = '{}/{}{}'.format(dest, rhost_ip, src)
    if not os.path.exists(rsync_config_path):
        logger.info(msg="rsync服务器无法联通或找不到配置文件,{}".format(src))
        return Response({'rtnMsg': 'rsync服务器无法联通或找不到配置文件,{}'.format(src)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    (rtnCode, tag_name, local_path) = rsync.delSection(rsync_server.base_bak_path,rsync_config_path, source_path, host_ip, tenant_name)
    if rtnCode == 0:
        src = rsync_config_path
        dest = rsync_server.config_path
        file_args = """src={src} dest={dest} owner={user} group={user} mode=644""".format(src=src, dest=dest,user=rsync_server.bak_user)
        ANS.run_model(host_list=sList, module_name="copy", module_args=file_args)
        logger.info(msg='rtnMsg: rsync配置文件删除节点 {}'.format(tag_name))
    elif rtnCode == '1':
        logger.info(msg='rtnMsg: rsync配置文件不存在节点 {}'.format(tag_name))

    '''
    start process client
    step1: del passwd file
    step2: del crontab
    '''
    if rtnCode == 0:
        path = '/home/{}/rsyncd.passwd'.format(rsync_server.bak_user)
        resource = [{"ip": snippet.bt_asset.ip, "port": 22, "username": rsync_server.bak_user}]
        ANS = ANSRunner(resource)
        sList = [snippet.bt_asset.ip]
        file_args = """path={path} state={state}""".format(path=path, state='absent')
        ANS.run_model(host_list=sList, module_name="file", module_args=file_args)
        logger.info(msg='del passwd file：{}'.format(json.loads(ANS.get_model_result())))
        cron_args = """name='{name}' user='{user}' state={state}""".format(name=tag_name, user=rsync_server.bak_user,state='absent')
        ANS.run_model(host_list=sList, module_name="cron", module_args=cron_args)
        logger.info(msg='del crontab：{}'.format(json.loads(ANS.get_model_result())))
        snippet.delete()
    logger.info(msg='finish funcfion taskdel')
    return Response({'rtnMsg': '任务已删除'})

@api_view(['POST' ])
@permission_required('backupconsole.can_delete_backup_task',raise_exception=True)
def fix_config(request):
    if request.method == 'POST':
        timestamp = request.data['timestamp']
        if not (timestamp[:7] ==  str(time.time())[:7]):
            logger.info(msg='客户用时间戳与服务器不匹配: Client=[{}],Server=[{}]'.format(timestamp[:7],time.time()))
            return Response({'rtnMsg':'系统错误，不被授权'},status=status.HTTP_403_FORBIDDEN)
        rsync_server = Rsync_Config.objects.get(id=1)
        rhost_ip = rsync_server.server
        src = rsync_server.config_path
        dest = '/tmp/opsfile'
        rsync_config_path = '{}/{}{}'.format(dest, rhost_ip, src)
        resource = [{"ip": rsync_server.server, "port": 22, "username": rsync_server.bak_user}]
        ANS = ANSRunner(resource)
        sList = [rsync_server.server]
        file_args = """src={src} dest={dest}""".format(src=src, dest=dest)
        ANS.run_model(host_list=sList, module_name="fetch", module_args=file_args)
        resultDict = json.loads(ANS.get_model_result())
        if not resultDict['success'].has_key(rsync_server.server):
            logger.info(msg=json.dumps(resultDict))
            return Response({'rtnMsg': '下载 rsync 配置文件失败'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not os.path.exists(rsync_config_path):
            logger.info(msg="rsync服务器无法联通或找不到配置文件,{}".format(src))
            return Response({'rtnMsg': 'rsync服务器无法联通或找不到配置文件,{}'.format(src)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        tasks = Backup_Task.objects.all()
        sectionsMap = {}
        for task in tasks:
            section = {}
            section['host_ip']=task.bt_asset.ip
            section['source_path']=task.bt_source_path
            section['tenant_name']=task.bt_group.name
            sectionsMap[task.id] = section
        rtnCode = rsync.genConfig(rsync_server.base_bak_path,rsync_server.pass_path,rsync_config_path,sectionsMap)
        if rtnCode == 0:
            src = rsync_config_path
            dest = rsync_server.config_path
            file_args = """src={src} dest={dest} owner={user} group={user} mode=644""".format(src=src, dest=dest,user=rsync_server.bak_user)
            ANS.run_model(host_list=sList, module_name="copy", module_args=file_args)
            return Response({'rtnMsg':'Finished'})
        else:
            return Response({'rtnMsg': '发生写盘异常'})


@api_view(['PUT'])
@permission_required('backupconsole.can_change_backup_task',raise_exception=True)
def task_mod(request):
    if request.method == 'PUT':
        task_id = request.data['taskid']
        reqData = {}
        reqData['bt_minute'] = request.data['bk_minute']
        reqData['bt_hour'] = request.data['bk_hour']
        reqData['bt_day'] = request.data['bk_day']
        reqData['bt_week'] = request.data['bk_week']
        reqData['bt_month'] = request.data['bk_month']
        try:
            snippet = Backup_Task.objects.get(id=task_id)
            rsync_server = Rsync_Config.objects.get(id=1)
        except Backup_Task.DoesNotExist:
            return Response({'rtnMsg':'Record not exist'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        serializer = serializers.BackupTaskSerializer(snippet,data=reqData)
        if serializer.is_valid():
            tag_name = '{}{}'.format(snippet.bt_asset.ip,snippet.bt_source_path.replace('/','-'))
            tag_name = tag_name[:-1] if tag_name.endswith('-') else tag_name
            sList = [snippet.bt_asset.ip]
            dest = '/home/{}/rsyncd.passwd'.format(rsync_server.bak_user)
            rsync_cmd = 'rsync -az --progress {source_path} {tenant_name}@{rsync_server}::{tag_name} --password-file={passwd_file}'.format(
                source_path=snippet.bt_source_path,
                tenant_name=snippet.bt_group.name,
                rsync_server=rsync_server.server,
                tag_name=tag_name,
                passwd_file=dest)
            cron_args = """name={name} minute='{minute}' hour='{hour}' day='{day}' weekday='{weekday}' month='{month}' user='{user}' job='{job}'""".format(
                name=tag_name, minute=reqData['bt_minute'],
                hour=reqData['bt_hour'], day=reqData['bt_day'],
                weekday=reqData['bt_week'], month=reqData['bt_month'],
                user=rsync_server.bak_user,job=rsync_cmd
            )
            logger.info(msg='cron_args: {}'.format(cron_args))
            resource = [{"ip": snippet.bt_asset.ip, "port": 22, "username": rsync_server.bak_user}]
            ANS = ANSRunner(resource)
            ANS.run_model(host_list=sList, module_name="cron", module_args=cron_args)
            serializer.save()
            logger.info(msg=ANS.get_model_result())
            return Response({'rtnMsg': '任务已更新'})
        else:
            return Response({'rtnMsg': 'input parameter is not valid'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







