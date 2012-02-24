
import json
import base64
import http.client
import urllib.parse
import functools


class Database (object):

    def __init__(self, user, passwd, server="127.0.0.1:5984"):
        self.uri = urllib.parse.urlparse("http://" + server).netloc
        self.auth = ({'Authorization': "Basic " +
            base64.b64encode(user.encode() + b":" + passwd.encode()).decode()}
            if user and passwd is not None else {})

    def request(self, method, action, headers=None, body=None):
        headers, body = headers or {}, body or {}
        headers.update(self.auth)
        headers.update({'Content-Type': 'application/json'})
        connection = http.client.HTTPConnection(self.uri)
        connection.request(method, action, json.dumps(body), headers)
        return json.loads(connection.getresponse().read().decode())
