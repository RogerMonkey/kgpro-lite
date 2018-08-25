#coding=utf8
import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import re
import tornado.web
import json
import os
from tornado.options import define, options


tp = json.load(open('C:/Users/roger/Documents/KGPro_Lite/static/zz.txt'))

class InferenceHandler(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument('question')
        # q = re.findall("/kgpro-web/inference\?question=(.*)", self.request.uri)[0]
        print(q)
        # server = CommonService(q[0])
        param = tp
        if q in param:
            self.write(json.dumps(param[q]))

define("port", default=6868, help="run on the given port", type=int)

handlers = [
    (r"/kgpro-web/inference", InferenceHandler),
]

template_path = os.path.join(os.path.dirname(__file__), "static")
static_path = os.path.join(os.path.dirname(__file__), "static")

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=handlers, debug= True, template_path= template_path,
                                  static_path= static_path)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()