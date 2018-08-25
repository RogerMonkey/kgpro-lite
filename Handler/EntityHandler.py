import tornado.web
import json
from Base import Query
import re
from Service.CommonService import *

__author__ = 'roger'

class EntityHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        query = Query('192.168.10.158', 27017, 'testkg')
        page = int(self.get_argument('page'))
        limit = int(self.get_argument('limit'))
        if 'searchKey' in self.request.arguments:
            key = self.get_argument('searchKey')
            value = self.get_argument('searchValue')
        else:
            key = None
            value = None

        if key is None:
            count = query.db['node'].count()
            result = query.db['node'].find(projection={'_id':False}).limit(limit).skip(limit * (page - 1))
        else:
            count = query.db['node'].find({'name':value}).count()
            result = query.db['node'].find({'name':value},projection={'_id': False}).limit(limit).skip(limit * (page - 1))
        resp = {'code':0, 'count':count, 'data':[x for x in result]}

        self.write(json.dumps(resp))

    def delete(self, *args, **kwargs):
        id = int(self.request.uri.split('/')[-1])
        excutor = Delete('192.168.10.158', 27017, 'testkg')
        if excutor.delete_entity_by_id(id) is True:
            self.write(json.dumps({"code":200, "msg":"删除成功！"}))
        else:
            self.write(json.dumps({"code": 0, "msg": "删除失败！"}))

    def post(self, *args, **kwargs):
        jsonnode = {}
        jsonnode['name'] = self.get_argument('entityname')
        jsonnode['concept'] = self.get_argument('concept')
        jsonnode['des'] = self.get_argument('entitydes')
        jsonnode['category'] = self.get_argument('category')
        insert = Insert('192.168.10.158', 27017, 'testkg')
        tag, id = insert.insert_one_node(jsonnode)
        if tag == True:
            self.write(json.dumps({"code":200, "msg":"插入成功！"}))
        else:
            self.write(json.dumps({"code":200, "msg":"插入失败！"}))
        print(jsonnode)

    # 更新
    def put(self, *args, **kwargs):
        self.write(json.dumps({"code":200, "msg":"更新失败！"}))


class TripleHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        query = Query('192.168.10.158', 27017, 'testkg')
        page = int(self.get_argument('page'))
        limit = int(self.get_argument('limit'))
        if 'searchKey' in self.request.arguments:
            key = self.get_argument('searchKey')
            value = self.get_argument('searchValue')
        else:
            key = None
            value = None

        # if key is None:
        count = query.db['triple'].count()
        result = query.db['triple'].find(projection={'_id':False}).limit(limit).skip(limit * (page - 1))
        data = []
        for triple in result:
            hid = query.query_node_by_id(triple['hid'])[0]['name']
            rid = query.query_relation_by_id(triple['rid'])[0]['name']
            tid = query.query_node_by_id(triple['tid'])[0]['name']
            data.append({'hid':hid, 'rid':rid, 'tid':tid})

        # else:
        #
        #     count = query.db['node'].find({'name':value}).count()
        #     result = query.db['node'].find({'name':value},projection={'_id': False}).limit(limit).skip(limit * (page - 1))
        resp = {'code':0, 'count':count, 'data':data}

        self.write(json.dumps(resp))

    def delete(self, *args, **kwargs):
        id = int(self.request.uri.split('/')[-1])
        excutor = Delete('192.168.10.158', 27017, 'testkg')
        if excutor.delete_entity_by_id(id) is True:
            self.write(json.dumps({"code":200, "msg":"删除成功！"}))
        else:
            self.write(json.dumps({"code": 0, "msg": "删除失败！"}))

    def post(self, *args, **kwargs):
        jsonnode = {}
        jsonnode['name'] = self.get_argument('entityname')
        jsonnode['concept'] = self.get_argument('concept')
        jsonnode['des'] = self.get_argument('entitydes')
        jsonnode['category'] = self.get_argument('category')
        insert = Insert('192.168.10.158', 27017, 'testkg')
        tag, id = insert.insert_one_node(jsonnode)
        if tag == True:
            self.write(json.dumps({"code":200, "msg":"插入成功！"}))
        else:
            self.write(json.dumps({"code":200, "msg":"插入失败！"}))
        print(jsonnode)

    def put(self, *args, **kwargs):
        self.write(json.dumps({"code":200, "msg":"更新失败！"}))