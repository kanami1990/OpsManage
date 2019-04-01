# Created by redial at 2019-03-28
# -*- coding: utf-8 -*-
import nginx
import os

def genNginxConfig(rr_name,domain,sPort,rIP,rPort,perfix,nginx_log_path):
    conf_filename = '{}.{}_{}_{}.conf'.format(rr_name, domain, sPort, rPort)

    def genProxy_pass(rIP, rPort=None, perfix=None):
        if rPort:
            if perfix:
                proxy_pass = 'http://{}:{}/{}/'.format(rIP, rPort, perfix)
            else:
                proxy_pass = 'http://{}:{}/'.format(rIP, rPort)
        else:
            if perfix:
                proxy_pass = 'http://{}/{}/'.format(rIP, perfix)
            else:
                proxy_pass = 'http://{}/'.format(rIP)
        return proxy_pass

    proxy_pass = genProxy_pass(rIP,rPort,perfix)

    c = nginx.Conf()
    s = nginx.Server()
    s.add(
        nginx.Key('listen', sPort),
        # nginx.Comment('Yes, python-nginx can read/write comments!'),
        nginx.Key('server_name', '{}.{}'.format(rr_name, domain)),
        nginx.Location('/',
                       nginx.Key('access_log', '{}{}.access.log main'.format(nginx_log_path, rr_name)),
                       nginx.Key('proxy_pass', genProxy_pass(rIP, rPort, perfix)),
                       nginx.Key('tcp_nodelay', 'on'),
                       nginx.Key('proxy_set_header', 'Host            $host'),
                       nginx.Key('proxy_set_header', 'X-Real-IP       $remote_addr'),
                       nginx.Key('proxy_set_header', 'X-Forwarded-For $proxy_add_x_forwarded_for'),
                       # nginx.Key('error_page', '500 502 503 504  /50x.html'),
                       # nginx.Location('= /50x.html',
                       #     nginx.Key('root', '/usr/share/nginx/html'),
                       #                )
                       )
    )
    c.add(s)
    if not os.path.exists('/tmp/opsfile'):
        os.mkdir('/tmp/opsfile')
    nginx.dumpf(c, '/tmp/opsfile/{}'.format(conf_filename))
    return (conf_filename,'/tmp/opsfile/{}'.format(conf_filename))
