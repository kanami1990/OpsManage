#!/usr/bin/env python
# _#_ coding:utf-8 _*_
# from zabbix_api.models import Alerts
import ConfigParser,pymysql
from OpsManage.utils.logger import logger
from zabbix_api.models import ZabbixAlert
from OpsManage.settings import ZABBIX_CONF_DIR

class ZabbixSource(object):
    def __init__(self):
        self.path = ZABBIX_CONF_DIR
        zabbix_conf = ConfigParser.ConfigParser()
        zabbix_conf.read(self.path)
        host = zabbix_conf.get('zabbix','host')
        user = zabbix_conf.get('zabbix','user')
        pwd = zabbix_conf.get('zabbix','password')
        db = zabbix_conf.get('zabbix','db')
        charset = zabbix_conf.get('zabbix','charset')
        self.db = pymysql.connect(host=host,user=user,passwd=pwd,db=db,charset=charset)
        super(ZabbixSource,self).__init__()

    def queryAlertsbyEventid(self,eventId,field):
        if not field:field='*'
        sql = "select {} from alerts where eventid={}".format(','.join(field),eventId)
        print(sql)
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            result = cursor.fetchall()
            subject = ''
            message = ''
            send_to = []
            for line in result:
                if line[6]:
                    send_to.append(line[6])
                    subject = line[7]
                    message = line[8]

            return(','.join(send_to),subject,message)
        except:
            pass

    def queryLogbyEventid(self,eventId):
        za_cnt = ZabbixAlert.objects.filter(event_id=eventId).count()
        if za_cnt > 0:
            return False
        else:
            return True

    def addLog(self,event,subject,send_to,message):
        log = ZabbixAlert.objects.create(event_id=event,subject=subject,send_to=send_to,message=message)
        return log




