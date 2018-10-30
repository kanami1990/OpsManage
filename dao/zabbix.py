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
        for item in r.json()['result']:
            if item['sendto']:
                # sendtolist.append(item['sendto'])
                sendtolist.extend(item['sendto'].split(','))
                subject = item['subject']
                message = item['message']
        return(','.join(sendtolist),subject,message)

    def queryLogbyEventid(self,eventId):
        za_cnt = ZabbixAlert.objects.filter(event_id=eventId).count()
        if za_cnt > 0:
            return False
        else:
            return True

    def addLog(self,event,subject,send_to,message,send_flag):
        log = ZabbixAlert.objects.create(event_id=event,subject=subject,send_to=send_to,message=message,send_flag=send_flag)
        return log




