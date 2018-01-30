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

define("port", default=8848, help="run on the given port", type=int)

handlers = [
    (r"/api/[a-z]*/insert", InsertHandler),
    (r"/api/[a-z]*/query/[a-z]*/.*|/api/[a-z]*/query", QueryHandler),
    (r"/api/[a-z]*/inference/[a-z1-9]*", InferenceHandler),
    (r"/api/[a-z]*/delete", DeleteHandler),
    (r"/api/[a-z]*/update", UpdateHandler)
]

template_path = os.path.join(os.path.dirname(__file__), "templates")
static_path = os.path.join(os.path.dirname(__file__), "static")

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=handlers, debug= True, template_path= template_path,
                                  static_path= static_path)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()