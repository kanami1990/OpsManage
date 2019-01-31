#!/usr/bin/env python
# _#_ coding:utf-8 _*_
import urllib2,json,simplejson


def getAccesstoken(sCorpID, secret):
    gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + sCorpID + '&corpsecret=' + secret
    try:
        token_file = urllib2.urlopen(gettoken_url)
        token_data = token_file.read().decode('utf-8')
        token_json = json.loads(token_data)
        token_json.keys()
        accessToken = token_json['access_token']
    except:
        return None
    if accessToken:
        return accessToken
    else:
        return None

class weChatFunc(object):
    def __init__(self):
        super(weChatFunc,self).__init__()

    def sendMSG(self, content,agentid,accesstoken):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + accesstoken
        send_values = structMSG(content, agentid).getCardMSG()
        send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
        send_request = urllib2.Request(send_url, send_data)
        response = json.loads(urllib2.urlopen(send_request).read())
        print(response)
        if any(s in str(response['errcode']) for s in ('40014', '42001')):
            return False
        return True

class structMSG():
    def __init__(self,content,agentid):
        self._toUser = content.get('toUser','@all')
        self._toParty = content.get('toParty','')
        self._toTag = content.get('toTag','')
        self._mediaId = content.get('content','')
        self._title = content.get('title','')
        self._description = content.get('description','')
        self._content = content.get('content','')
        self._url = content.get('url','')
        self._btxtxt = content.get('btxtxt','')
        self._agentId = agentid

    def getTextMSG(self):
        _textMSG = {
                        "touser" : self._toUser,
                        "toparty" : self._toParty,
                        "totag" : self._toTag,
                        "msgtype" : "text",
                        "agentid" : self._agentId,
                        "text" : {
                            "content" : self._content
                        },
                        "safe":0
                    }
        return _textMSG

    def getImageMSG(self):
        _imageMSG = {
                        "touser" : self._toUser,
                        "toparty" : self._toParty,
                        "totag" : self._toTag,
                        "msgtype" : "image",
                        "agentid" : self._agentId,
                        "image" : {
                            "media_id" : self._content
                        },
                        "safe":0
                    }
        return _imageMSG

    def getVoiceMSG(self):
        _voiceMSG = {
                        "touser" : self._toUser,
                        "toparty" : self._toParty,
                        "totag" : self._toTag,
                        "msgtype" : "voice",
                        "agentid" : self._agentId,
                        "voice" : {
                            "media_id" : self._content
                        }
                    }
        return _voiceMSG

    def getVideoMSG(self):
        _videoMSG = {
                        "touser" : self._toUser,
                        "toparty" : self._toParty,
                        "totag" : self._toTag,
                        "msgtype" : "video",
                        "agentid" : self._agentId,
                        "video" : {
                            "media_id" : self._content,
                            "title" : self._content,
                            "description" : self._content
                        },
                        "safe": 0
                    }
        return _videoMSG

    def getFileMSG(self):
        _fileMSG = {
                        "touser" : self._toUser,
                        "toparty" : self._toParty,
                        "totag" : self._toTag,
                        "msgtype" : "file",
                        "agentid" : self._agentId,
                        "file" : {
                            "media_id" : self._content,
                        },
                        "safe": 0
                    }
        return _fileMSG

    def getCardMSG(self):
        _cardMSG = {
                        "touser" : self._toUser,
                        "toparty" : self._toParty,
                        "totag" : self._toTag,
                        "msgtype" : "textcard",
                        "agentid" : self._agentId,
                        "textcard" : {
                            "title" : self._title,
                            "description" : self._content,
                            "url" : self._url,
                            "btntxt" : self._btxtxt
                        }
                    }
        return _cardMSG
