#!/usr/bin/env python
# _#_ coding:utf-8 _*_
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import permission_required
from sqlmanage.models import (SqlMon_DB,SqlMon_Sql)

import pymysql.cursors
import re,string

@api_view(['POST'])
@permission_required('sqlmanage.can_read_sqlmon_sqlinfo',raise_exception=True)
def keyQuery(request,format=None):
    if request.method == 'POST':
        key = request.data['zabbix_key']
        sqlObj = SqlMon_Sql.objects.filter(sql_key=key).first()
        if sqlObj :
            sqlinfo = sqlObj.sql_info
            dbkey = sqlObj.sql_db
            if sqlObj.sql_enabled == 1:
                return Response({'rtnMsg': 'sql disabled'})
            dbObj = SqlMon_DB.objects.get(id=dbkey)
            if dbObj:
                result = sqlConn(dbObj,sqlinfo)

                # return Response({'rtnMsg':result[0]})
                return Response(result[0])
            else:
                return Response({'rtnMsg':'no paired db found'})
        else:
            return Response({'rtnMsg':'no key found'})

def sqlConn(dbObj,sql_info):
    dbDict = dbObj.__dict__
    result = False
    if dbDict['db_type'] == 1:
        connection = pymysql.connect(host = dbDict['db_ip'],
                                     user = dbDict['db_user'],
                                     port = dbDict['db_port'],
                                     password = dbDict['db_passwd'],
                                     charset = 'utf8mb4',
                                     database = dbDict['db_name'],
                                     # cursorclass=pymysql.cursors.DictCursor,  #Dict (k,v) mode
                                     )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_info)
                result = cursor.fetchone()
        except:
            result = [-1]
        finally:
            connection.close()
    return result

@api_view(['POST'])
@permission_required('sqlmanage.can_read_sqlmon_sqlinfo',raise_exception=True)
def sqlQuery(request,format=None):
    if request.method == 'POST':
        key = request.data['zabbix_key']
        print(key)
        sqlObj = SqlMon_Sql.objects.filter(sql_key=key).first()
        if sqlObj:
            sqlinfo = sqlObj.sql_info
            dbkey = sqlObj.sql_db
            if sqlObj.sql_enabled == 1:
                return Response({'rtnMsg': 'sql disabled'})
            dbObj = SqlMon_DB.objects.get(id=dbkey)
            if dbObj:
                result = sqlConn2(dbObj, sqlinfo,key) # return {'data':List}
                return Response(result)
            else:
                return Response({'rtnMsg': 'no paired db found'})
        else:
            return Response({'rtnMsg': 'no key found'})

def sqlConn2(dbObj, sql_info,unikey):
    basePAT = ur'^select (?P<fieldstr>.*?) from .*'
    basePat = re.compile(basePAT)
    fieldstr = basePat.match(sql_info)
    fieldlist = [a.strip(' ') for a in fieldstr.groupdict()['fieldstr'].split(',')]
    dbDict = dbObj.__dict__
    result = []
    slist = tuple(string.uppercase)
    if dbDict['db_type'] == 1:
        connection = pymysql.connect(host=dbDict['db_ip'],
                                     user=dbDict['db_user'],
                                     port=dbDict['db_port'],
                                     password=dbDict['db_passwd'],
                                     charset='utf8mb4',
                                     database=dbDict['db_name'],
                                     cursorclass=pymysql.cursors.DictCursor,  #Dict (k,v) mode
                                     )
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_info)
                result = cursor.fetchall()
                for line in result:
                    for i in range(len(fieldlist)):
                        line.update({'{}#{}{}{}'.format('{',unikey,slist[i],'}'):line.pop(fieldlist[i])})
        except Exception,ex:
            print ex
            result = {'data':[]}
        finally:
            connection.close()
    return {'data':result}