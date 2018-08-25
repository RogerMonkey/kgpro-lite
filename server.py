import os.path

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import json
import os
from tornado.options import define, options

from Handler.InsertHandler import InsertHandler
from Handler.QueryHandler import QueryHandler
from Handler.InferenceHandler import InferenceHandler
from Handler.DeleteHandler import DeleteHandler
from Handler.UpdateHandler import UpdateHandler
from Handler.IndexHandler import *
from Handler.EntityHandler import *
from tornado.web import StaticFileHandler
from Handler.ModelHandler import *

define("port", default=8848, help="run on the given port", type=int)

handlers = [
    (r"/assets/(.*)", StaticFileHandler, {"path": "assets"}),
    (r"/views/(.*)", StaticFileHandler, {"path": "template/views"}),
    # (r"/index.html", StaticFileHandler, {"path": "template/index.html"}),
    (r"/api/entity(.*)", EntityHandler),
    (r"/api/triple(.*)", TripleHandler),
    (r"/api/model(.*)", ModelHandler),
    (r"/api/clean(.*)", CleanHandler),
    (r"/api/completion(.*)", CompHandler),
    (r"/api/equery", EntHandler),
    (r"/api/tquery", TriHandler),
    (r"/index.html", IndexHandler),
    (r"/login.html", LoginHandler),
    (r"/api/login", Login2Handler),
    (r"/api/menu(.*)", MenuHandler),
    (r"/api/[a-z]*/insert", InsertHandler),
    (r"/api/[a-z]*/query/[a-z]*/.*|/api/[a-z]*/query", QueryHandler),
    (r"/api/[a-z]*/inference/[a-z1-9]*", InferenceHandler),
    (r"/api/[a-z]*/delete", DeleteHandler),
    (r"/api/[a-z]*/update", UpdateHandler)
]

template_path = os.path.join(os.path.dirname(__file__), "template")
static_path = os.path.join(os.path.dirname(__file__), "assets")

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=handlers, debug=True, template_path=template_path,
                                  static_path= static_path)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()