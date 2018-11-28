#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import requests,json
from zabbix_api.models import Zabbix_Config
from OpsManage.utils.logger import logger
from zabbix_api.models import ZabbixAlert

class ZabbixSource(object):
    def __init__(self):
        try:
            zcc = Zabbix_Config.objects.filter(id=1).count()
        except:
            zcc = 0
        if zcc > 0:
            try:
                zabbix = Zabbix_Config.objects.get(id=1)
                self.zabbixapi = '{}/api_jsonrpc.php'.format(zabbix.host)
                self.zabbixuser = zabbix.user
                self.zabbixpwd = zabbix.passwd
                print(zabbix.token)
                if zabbix.token:
                    self.token = zabbix.token
                    self.zabbixuid = zabbix.userid
                else:
                    self.token = self.getToken()
            except:
                zabbix = None
        super(ZabbixSource,self).__init__()

    def reSyncToken(self):
        zabbix = Zabbix_Config.objects.get(id=1)
        self.zabbixapi = '{}/api_jsonrpc.php'.format(zabbix.host)
        self.zabbixuser = zabbix.user
        self.zabbixpwd = zabbix.passwd
        self.token = self.getToken()

    def getToken(self):
        headers = {'content-type': 'application/json'}
        d1 = {}
        d1['jsonrpc'] = '2.0'
        d1['method'] = 'user.login'
        d1['id'] = '1'
        d1['auth'] = None
        d2 = {}
        d2['user'] = self.zabbixuser
        d2['password'] = self.zabbixpwd
        d1['params'] = d2
        payload = json.dumps(d1)
        # payload = '{"jsonrpc":"2.0","method":"user.login","params":{"user":"{}","password":"{}"},"id":1,"auth":null}'.format(self.zabbixuser,self.zabbixpwd)
        r = requests.post(self.zabbixapi, data=payload, headers=headers)
        if r.json().has_key('error'):
            print(r.json())
        else:
            Zabbix_Config.objects.filter(id=1).update(
                userid = r.json()['id'],
                token = r.json()['result']
            )
            self.token = r.json()['result']
            self.zabbixuid = r.json()['id']
            Zabbix_Config.objects.filter(id=1).update(token=self.token,userid=self.zabbixuid)
            return self.token


    def queryAlertsbyEventid(self,eventId):
        headers = {'content-type': 'application/json'}
        d1 = {}
        d1['jsonrpc'] = '2.0'
        d1['method'] = 'alert.get'
        d2 = {}
        d2['output'] = 'extend'
        d2['eventids'] = eventId
        d1['params'] = d2
        d1['id'] = int(self.zabbixuid)
        d1['auth'] = self.token
        payload = json.dumps(d1)
        r = requests.post(self.zabbixapi, data=payload, headers=headers)
        subject = ''
        message = ''
        sendtolist = []
        # if not r.json()['error']['code'] == -32602 :
        try:
            for item in r.json()['result']:
                if item['sendto']:
                    # sendtolist.append(item['sendto'])
                    sendtolist.extend(item['sendto'].split(','))
                    subject = item['subject']
                    message = item['message']
            return(','.join(sendtolist),subject,message)
        except:
            if 'login' in r.json()['error']['code']:
                self.reSyncToken()
                self.queryAlertsbyEventid()


    def queryLogbyEventid(self,eventId):
        za_cnt = ZabbixAlert.objects.filter(event_id=eventId).count()
        if za_cnt > 0:
            return False
        else:
            return True

    def addLog(self,event,subject,send_to,message,send_flag):
        log = ZabbixAlert.objects.create(event_id=event,subject=subject,send_to=send_to,message=message,send_flag=send_flag)
        return log

    def queryDisabledUserGroupId(self):
        headers = {'content-type': 'application/json'}
        d1 = {}
        d1['jsonrpc'] = '2.0'
        d1['method'] = 'usergroup.get'
        d2 = {}
        d2['output'] = 'extend'
        # d3 = {}
        # d3['name'] = 'Disabled'
        # d1['search'] = d3
        d1['params'] = d2
        d1['id'] = int(self.zabbixuid)
        d1['auth'] = self.token
        payload = json.dumps(d1)
        r = requests.post(self.zabbixapi, data=payload, headers=headers)
        print json.dumps(r.json(),ensure_ascii=False)
        gid = ''
        try:
            for item in r.json()['result']:
                if item['name'] == 'Disabled':
                    gid = item['usrgrpid']
            return gid
        except:
            if 'login' in r.json()['error']['code']:
                self.reSyncToken()
                self.queryDisabledUserGroupId()

    def addUser(self,username):
        headers = {'content-type': 'application/json'}
        d1 = {}
        d1['jsonrpc'] = '2.0'
        d1['method'] = 'user.create'
        d2 = {}
        d2['alias'] = username
        d2['passwd'] = '111111'
        d3 = {}
        d3['usrgrpid'] = self.queryDisabledUserGroupId()
        # d3['usrgrpid'] = '9'
        d2['usrgrps'] = [d3]
        d1['params'] = d2
        d1['id'] = int(self.zabbixuid)
        d1['auth'] = self.token
        payload = json.dumps(d1)
        print payload
        r = requests.post(self.zabbixapi, data=payload, headers=headers)
        print json.dumps(r.json(),ensure_ascii=False)
        try:
            if r.json()['result']['userids'][0]:
                return True
            else:
                return False
        except:
            if 'login' in r.json()['error']['code']:
                self.reSyncToken()
                self.addUser(username)





