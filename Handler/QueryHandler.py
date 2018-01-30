import tornado.web
import json
from Service import *
import re
from Service.CommonService import *

__author__ = 'roger'

class QueryHandler(tornado.web.RequestHandler):
    def get(self):
        q = re.findall("/api/([a-z]*)/query/([a-z]*)/(.*)", self.request.uri)[0]
        print(q[0])
        server = CommonService(q[0])
        param = {}
        try:
            param['key'] = int(q[2])
            param['class'] = 'id'
        except:
            param['key'] = q[2]
            param['class'] = 'name'
        param['type'] = q[1]
        print(param)
        response = server.querySingleService(param)
        self.write(json.dumps(response))

    def post(self):
        server = CommonService(re.findall("/api/([a-z]*)/query.*", self.request.uri)[0])
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        response = server.queryTripleService(param)
        print(response)
        self.write(json.dumps(response))