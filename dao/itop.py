#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import requests,json,ConfigParser
from itop_api.models import ITOP_Config
from OpsManage.utils.logger import logger
from OpsManage.settings import ITOP_CONF_DIR


class ItopSource(object):
    def __init__(self):
        # self.path = ITOP_CONF_DIR
        # itop_conf = ConfigParser.ConfigParser()
        # itop_conf.read(self.path)
        # self.itop_url = itop_conf.get('itop','url')
        # self.itop_user = itop_conf.get('itop','user')
        # self.itop_pwd = itop_conf.get('itop','password')
        try:
            itopConf = ITOP_Config.objects.get(id=1)
            self.itop_url = itopConf.host + 'webservices/rest.php?version=1.3'
            self.itop_user = itopConf.user
            self.itop_pwd = itopConf.passwd
        except:
            self.itop_url = self.itop_user =self.itop_pwd = None
        # print('url = {}\nuser = {}\npasswd = {}'.format(self.itop_url,self.itop_user,self.itop_pwd))
        super(ItopSource,self).__init__()

    def query_by_id(self,dataModel,requestid,fields):
        jsonDict = {}
        jsonDict['operation'] = 'core/get'
        jsonDict['class'] = dataModel
        jsonDict['key'] = requestid
        jsonDict['output_fields'] = '*'
        if fields:
            # print fields
            jsonDict['output_fields'] = fields
        json_str = json.dumps(jsonDict)
        r = requests.post(self.itop_url, verify=False,
                          data={'auth_user': self.itop_user, 'auth_pwd': self.itop_pwd, 'json_data': json_str})
        return r.text

    def query_by_oql(self,dataModel, oql, fields):
        jsonDict = {}
        jsonDict['operation'] = 'core/get'
        jsonDict['class'] = dataModel
        jsonDict['key'] = oql
        jsonDict['output_fields'] = '*'
        if fields:
            # print fields
            jsonDict['output_fields'] = fields
        json_str = json.dumps(jsonDict)
        r = requests.post(self.itop_url, verify=False,
                          data={'auth_user': self.itop_user, 'auth_pwd': self.itop_pwd, 'json_data': json_str})
        return r.text

    def create_object_without_callerid(self,dataModel, objDict):
        baseDict = {}
        baseDict['operation'] = "core/create"
        baseDict['comment'] = "create {} by interface".format(dataModel)
        baseDict['class'] = dataModel
        baseDict['output_fields'] = "id"
        baseDict['fields'] = objDict
        json_str = json.dumps(baseDict)
        r = requests.post(self.itop_url, verify=False,
                          data={'auth_user': self.itop_user, 'auth_pwd': self.itop_pwd, 'json_data': json_str})
        return r.text

    def update_object_by_dict(self,dataModel, objDict, filterDict):
        baseDict = {}
        baseDict['operation'] = "core/update"
        baseDict['comment'] = "update {} by interface".format(dataModel)
        baseDict['class'] = dataModel
        baseDict['output_fields'] = "id"
        baseDict['key'] = filterDict
        baseDict['fields'] = objDict
        json_str = json.dumps(baseDict)
        r = requests.post(self.itop_url, verify=False,
                          data={'auth_user': self.itop_user, 'auth_pwd': self.itop_pwd, 'json_data': json_str})
        return r.text