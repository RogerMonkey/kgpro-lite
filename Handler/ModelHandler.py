import tornado.web
import json

from Base.Insert import Insert
from Base.Query import Query
from model.Clean import *
import Base.ModelOperator as mop
from Service.CommonService import *

def getlog(path):
    text = ''
    # try:
    print('model/' + path + '/model.log')
    f = open('model/' + path + '/model.log')
    print(f)
    for line in f.readlines():
        text += line
    return text


class ModelHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        if self.get_argument('token') == '222':
            query = Query('192.168.10.158', 27017, 'testkg')
            result = [x for x in query.db['model'].find(projection={'_id': False})]
            for x in result:
                x['log'] = getlog(x['path'])
            count = query.db['model'].count()

            self.write(json.dumps({'code': 0, 'count': count, 'data': result}))

    def post(self, *args, **kwargs):
        name = self.get_argument('name')
        model = self.get_argument('model')
        # TODO
        pars = self.get_argument('pars')
        path = model + '/' + name

        store = {'name': name, 'model': model, 'pars': pars,
                 'path': path, 'status': False}
        mop.preprocess('testkg', path)
        insert = Insert('192.168.10.158', 27017, 'testkg')

        if insert.db['model'].insert(store) == True:
            self.write(json.dumps({'code': 200, 'msg': '模型开始训练！请耐心等待！'}))
        else:
            self.write(json.dumps({'code': 200, 'msg': '训练失败！'}))


class CleanHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        if self.get_argument('token') == '222':
            query = Query('192.168.10.158', 27017, 'testkg')
            result = [x for x in query.db['clean'].find(projection={'_id': False})]
            count = query.db['clean'].count()

            self.write(json.dumps({'code': 0, 'count': count, 'data': result}))

    def post(self, *args, **kwargs):
        name = self.get_argument('name')
        query = Query('192.168.10.158', 27017, 'testkg')
        path = query.db['model'].find({'name':name})[0]['path']
        # TODO
        pars = float(self.get_argument('pars'))

        log = clean(query, 'model/' + path, pars)
        store = {'name': name, 'pars': pars,
                 'path': path, 'log' : log}

        insert = Insert('192.168.10.158', 27017, 'testkg')

        if insert.db['clean'].insert(store) == True:
            self.write(json.dumps({'code': 200, 'msg': '模型开始训练！请耐心等待！'}))
        else:
            self.write(json.dumps({'code': 200, 'msg': '训练失败！'}))

class CompHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        if self.get_argument('token') == '222':
            query = Query('192.168.10.158', 27017, 'testkg')
            limit = int(self.get_argument('limit'))
            page = int(self.get_argument('page'))
            q = query.db['completion'].find(projection={'_id': False}).limit(limit).skip((page-1) * limit)
            count = query.db['completion'].count()
            data = []
            for triple in q:
                hid = triple['head']
                rid = triple['relation']
                tid = triple['tail']
                score = triple['score']
                data.append({'head': hid, 'relation': rid, 'tail': tid, 'score':score})

            self.write(json.dumps({'code': 0, 'count': count, 'data': data}))

    def post(self, *args, **kwargs):
        name = self.get_argument('name')
        head = self.get_argument('head')
        tail = self.get_argument('tail')
        query = Query('192.168.10.158', 27017, 'testkg')
        # TODO
        path = query.db['model'].find({'name': name})[0]['path']
        hid = query.query_node_by_name(head)[0]['id']
        tid = query.query_node_by_name(tail)[0]['id']


        result = completion(hid, tid, 'model/'+ path)
        data = []
        for x in result:
            data.append({
                'head': head,
                'relation': query.query_relation_by_id(x[0])[0]['name'],
                'tail': tail,
                'score':round(x[1],5)
            })

        print(data)
        insert = Insert('192.168.10.158', 27017, 'testkg')
        insert.db['completion'].insert(data)
        self.write(json.dumps({'code': 200, 'msg': '存储成功！'}))

class EntHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        name = self.get_argument('entity')
        # print(name)
        query = Query('192.168.10.158', 27017, 'testkg')
        eid = query.query_node_by_name(name)[0]['id']
        print(eid)
        entity = query.query_entity_by_id(eid)
        txt = ''
        graph = {"nodes":[name], "edges": []}
        for x in entity:
            if x == 'rels':
                for r in entity[x]:
                    txt += '{0}:\n'.format(r)
                    for t in entity[x][r]:
                        graph["nodes"].append(t["name"])
                        graph["edges"].append([name, t["name"]])
                        txt += '\t{0}\n'.format(t["name"])
            elif x == 'attrs':
                pass
            else:
                txt += '{0}: {1}\n'.format(x, entity[x])
        # print(txt, graph)
        same = similar(eid, query, 'model/TransE/test/', 0.85)
        print(same)
        stxt = ''
        for s in same:
            stxt += '{0}\t{1}\n'.format(s[0], s[1])
        self.write(json.dumps({'txt':txt, 'graph':graph, 'same':stxt}))

class TriHandler(tornado.web.RequestHandler):
    def post(self, *args, **kwargs):
        head = self.get_argument('head')
        relation = self.get_argument('relation')
        tail = self.get_argument('tail')
        # print(name)
        query = Query('192.168.10.158', 27017, 'testkg')
        qjson = {}
        if head != '':
            qjson['hid'] = query.query_node_by_name(head)[0]['id']
        if tail != '':
            qjson['tid'] = query.query_node_by_name(tail)[0]['id']
        if relation != '':
            qjson['rid'] = query.query_relation_by_name(relation)[0]['id']

        print(qjson)
        result = query.db['triple'].find(qjson, projection={'_id': False})
        graph = {"nodes": [], "edges": []}
        for x in result:
            print(x)
            h = query.query_node_by_id(x['hid'])[0]['name']
            t = query.query_node_by_id(x['tid'])[0]['name']
            graph['nodes'].append(h)
            graph['nodes'].append(t)
            graph['edges'].append([h,t])

        self.write(json.dumps({'graph':graph}))