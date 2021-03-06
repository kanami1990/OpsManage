import os
import json
import time
import subprocess
import threading
from .utils import stop_thread
from django.conf import settings
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
import urlparse
from models import LogSignup

@channel_session_user_from_http
def ws_connect(message):
    log_id = message.reply_channel.name.split('.')[-1]
    log_id = log_id.replace('!', '1')
    message.reply_channel.send({"accept": True})
    params = urlparse.parse_qs(message.content['query_string'])
    dbid = params.get('id', (None,))[0]
    filename = params.get('filename', (None,))[0]
    print('keyid = {}'.format(filename))
    print('filename = {}'.format(id))
    loginfo = LogSignup.objects.get(id=dbid)
    if filename:
        if not loginfo.log_path.endswith('/'):
            filepath = '{}/{}'.format(loginfo.log_path,filename)
        else:filepath = '{}{}'.format(loginfo.log_path,filename)
    else:filepath = loginfo.log_path
    log_ip = loginfo.log_ip

    tail_cmd = 'ssh opsadm@{} "tail -200f {}"'.format(log_ip,filepath)
    tail_popen = subprocess.Popen(tail_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    def make_tail(message,tp,dbid):
        def tail():
            while True:
                line = tp.stdout.readline()
                # line = line.replace('<','&lt;').replace('>','&gt;').replace('&','&amp').replace('"','&quot;')
                message.reply_channel.send({'text': json.dumps({dbid: line.decode('utf-8')})})
        return tail

    print('create thread')
    tailThread = threading.Thread(name='log{}'.format(str(time.time()).replace('.','')), target=make_tail(message,tail_popen,dbid))
    tailThread.start()
    print threading.enumerate()



@channel_session_user
def ws_disconnect(message):
    print('disconnect')
    log_id = message.reply_channel.name.split('.')[-1]
    log_id = log_id.replace('!', '1')
    Group('logs' + log_id).send({
        'text': json.dumps({
            'is_logged_in': False
        })
    })

    Group('logs' + log_id).discard(message.reply_channel)

    # stop_thread(tailThread)
