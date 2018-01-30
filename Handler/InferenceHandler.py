import tornado.web
import json
from Service import *
import re
from Service.CommonService import *

__author__ = 'roger'

class InferenceHandler(tornado.web.RequestHandler):
    def get(self):
        q = re.findall("/api/([a-z]*)/inference/([a-z]*)", self.request.uri)[0]
        print(q)
        server = CommonService(q[0])
        param = {}
        try:
            param['key'] = int(q[1])
            param['class'] = 'id'
        except:
            param['key'] = q[1]
            param['class'] = 'name'
        print(param)
        response = server.inferenceService(param)
        self.write(json.dumps(response))