#!/usr/bin/python
# -*- coding: utf-8

import os, sys
import urllib2, ssl
from hashlib import md5
from xml.etree.ElementTree import fromstring, ElementTree as ET, dump as ETdump
import json

#PROG = os.path.basename(sys.argv[0]).rstrip('.py')
#PROG_DESC = 'hp-msa client'
#USAGE = """Usage: hp-msa.py <HOSTNAME> <USERNAME> <PASSWORD> [lld|stats|data]"""

class msa_storage(object):
    username = None
    password = None
    hostname = None
    sessionKey = None
#    zbxData = {'data': []}

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password
    
    def _request_url(self, api):
        url = 'https://%s/api/%s' % (self.hostname, api)
        print(url)
        #return 'https://%s/api/%s' % (self.hostname, api)
        return url
    
    def _request(self, api):
        # print(self._request_url(api))
        if self.sessionKey:
            req = urllib2.Request(url=self._request_url(api))
            req.add_header('dataType', 'api-brief')
            req.add_header('sessionKey', self.sessionKey)
            xml=urllib2.urlopen(req, context=ssl._create_unverified_context()).read()
            #if len(xml)>10:
            #    return ET(fromstring(xml)).getroot()
        return xml
    
    def _request_show(self, api):
        return self._request('show/' + api)
    
    def dados(self, api):
        return self._request_show(api)
     
    def login(self):
        return_code = 0
        req = urllib2.Request(url=self._login_url())
        req.add_header('dataType', 'api-brief')
        xml = urllib2.urlopen(req, context=ssl._create_unverified_context()).read()
        tree = ET(fromstring(xml))
        for obj in tree.getroot():
            for prop in obj:
                if prop.get('name') == 'response-type':
                    response_type = prop.text
                    print(prop.text)
                if prop.get('name') == 'return-code':
                    return_code = int(prop.text)
                    print(prop.text)
                if prop.get('name') == 'response':
                    self.sessionKey = prop.text
                    print(prop.text)
        return return_code
    
    def _login_url(self):
        login = md5('%s_%s' % (self.username, self.password)).hexdigest()
        print(login)
        url = f'https://{self.hostname}/api/login/{login}'
        print(url)
        return url

    def logout(self):
        self._request('exit')

if __name__ == "__main__":

    msa = msa_storage(sys.argv[1], sys.argv[2], sys.argv[3])
    msa.login()
    api = "controllers"
    print(msa.dados)
    msa.logout()