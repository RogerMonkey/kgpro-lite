import tornado.web
import json
from Service import *
import re
from Service.CommonService import *

__author__ = 'roger'

class DeleteHandler(tornado.web.RequestHandler):
    def post(self):
        server = CommonService(re.findall("/api/([a-z]*)/delete", self.request.uri)[0])
        param = self.request.body.decode('utf-8')
        param = json.loads(param)
        print(param)
        response = server.deleteService(param)
        print(response)
        self.write(json.dumps(response))