#!/usr/bin/python
# -*- coding: utf-8

import os
import sys
import ssl
import urllib2
from hashlib import md5
from xml.etree.ElementTree import fromstring, ElementTree as ET, dump as ETdump
import xmltodict
import json
import jmespath

attributes = """durable-id
architecture
interface
usage
size-numeric
disk-group
led-status
smart
owner
transfer-rate
status
temperature-numeric
temperature-status
health-numeric""".split('\n')

class msa_storage(object):
    username = None
    password = None
    hostname = None
    sessionKey = None

    def __init__(self, hostname, username, password):
        self.hostname = hostname
        self.username = username
        self.password = password

    def login(self):
        req = urllib2.Request(url=self._login_url())
        req.add_header('dataType', 'api-brief')
        xml = urllib2.urlopen(req, context=ssl._create_unverified_context()).read()
        tree = ET(fromstring(xml))
        for obj in tree.getroot():
            for prop in obj:
                if prop.get('name') == 'response':
                    self.sessionKey = prop.text

    def logout(self):
        self._request('exit')

    def _login_url(self):
        login = md5( '{}_{}'.format(self.username, self.password)).hexdigest()
        url = 'https://{}/api/login/{}'.format( self.hostname, login)
        return url

    def _request_url(self, api):
        return 'https://%s/api/%s' % (self.hostname, api)

    def _request(self, api):
        if self.sessionKey:
            req = urllib2.Request(url=self._request_url(api))
            req.add_header('dataType', 'api-brief')
            req.add_header('sessionKey', self.sessionKey)
            xml=urllib2.urlopen(req, context=ssl._create_unverified_context()).read()
            return xml
        return None

    def request_show(self, api):
        return self._request('show/' + api)

if __name__ == "__main__":
    msa = msa_storage(sys.argv[1], sys.argv[2], sys.argv[3])
    msa.login()
    if sys.argv[4] != 'disks':
        print(msa.request_show(sys.argv[4]))
    else:
        disks = msa.request_show(sys.argv[4])
        expression = jmespath.compile('RESPONSE.OBJECT[?"@name"==`drive`]')
        drives = expression.search(xmltodict.parse(disks))
        for drive in drives:
            property = []
            for propy in drive['PROPERTY']:
                if propy['@name'] in attributes:
                    propy.pop('@type')
                    property.append(propy)
            drive.pop('PROPERTY')
            drive['PROPERTY'] = property

        print(json.dumps(drives))
    msa.logout()