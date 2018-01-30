import tornado.web
import json
from Service import *
from Service.CommonService import *
import re
__author__ = 'roger'

class InsertHandler(tornado.web.RequestHandler):
    def post(self):
        server = CommonService(re.findall("/api/([a-z]*)/insert", self.request.uri)[0])
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        response = server.insertService(param)
        print(response)
        self.write(json.dumps(response))