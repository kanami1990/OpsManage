# Created by redial at 2019-03-05
# -*- coding: utf-8 -*-
import ConfigParser

class FakeGlobalSectionHead(object):
    def __init__(self,filePath):
        self.filePath = filePath
        self.secHead = '[global]\n'

    def readline(self):
        if self.secHead:
            try: return self.secHead
            finally: self.secHead = None
        else: return self.filePath.readline()

def addSection(base_path,pass_path,rsync_file_path,source_path,host_ip,tenant_name):
    tagname = '{}{}'.format(host_ip, source_path.replace('/', '-'))
    b = {
        'path': '{}/{}/{}'.format(base_path,tenant_name, tagname),
        'auth user': tenant_name,
        'secrets file': pass_path,
        'ignore errors': 'yes'
    }

    config = ConfigParser.ConfigParser()
    config.readfp(FakeGlobalSectionHead(open(rsync_file_path)))
    if tagname in config.sections() and tagname != 'global':
        # config.remove_section(tagname)
        # with open(rsync_file_path, 'w+') as configfile:
        #     config.write(configfile)
        # with open(rsync_file_path, 'r') as fin:
        #     data = fin.read().splitlines(True)
        # with open(rsync_file_path, 'w') as fout:
        #     fout.writelines(data[1:])
        return (0,tagname,b['path'])
    else:
        config = ConfigParser.RawConfigParser()
        config.add_section(tagname)
        for k, v in b.items():
            config.set(tagname, k, v)
        with open(rsync_file_path, 'ab') as configfile:
            config.write(configfile)
        return (1,tagname,b['path'])

def delSection(base_path,rsync_file_path,source_path,host_ip,tenant_name):
    tagname = '{}{}'.format(host_ip, source_path.replace('/', '-'))
    config = ConfigParser.ConfigParser()
    config.readfp(FakeGlobalSectionHead(open(rsync_file_path)))
    if tagname in config.sections() and tagname != 'global':
        config.remove_section(tagname)
        with open(rsync_file_path, 'w+') as configfile:
            config.write(configfile)
        with open(rsync_file_path, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(rsync_file_path, 'w') as fout:
            fout.writelines(data[1:])
        return (0, tagname, '{}/{}/{}'.format(base_path,tenant_name, tagname))
    else:
        return (1, tagname, '{}/{}/{}'.format(base_path,tenant_name, tagname))

def genConfig(base_path,pass_path,rsync_file_path,sectionsMap):
    #remove old sections
    config = ConfigParser.ConfigParser()
    config.readfp(FakeGlobalSectionHead(open(rsync_file_path)))
    sections = config.sections()
    sections.pop(0)
    for section in sections:
        config.remove_section(section)
    #regen all sections
    for _,item in sectionsMap.items():
        tagname = '{}{}'.format(item['host_ip'], item['source_path'].replace('/', '-'))
        b = {
            'path': '{}/{}/{}'.format(base_path,item['tenant_name'], tagname),
            'auth user': item['tenant_name'],
            'secrets file': pass_path,
            'ignore errors': 'yes'
        }
        config.add_section(tagname)
        for k, v in b.items():
            config.set(tagname, k, v)
    # write into  file
    try:
        with open(rsync_file_path, 'w+') as configfile:
            config.write(configfile)
        with open(rsync_file_path, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(rsync_file_path, 'w') as fout:
            fout.writelines(data[1:])
        return 0
    except Exception,e:
        return 1
