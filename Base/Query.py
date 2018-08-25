__author__ = 'roger'

# base insert function

import json
import pymongo
import Base.MongoConn

class Query(object):
    db = None

    def __init__(self, user, port, dbname):
        conn = Base.MongoConn.Conn()
        conn.connect(user, port)
        self.db = conn.get_db(dbname)

    def query_node_by_id(self, id):
        return self.db['node'].find({'id': id}, projection={'_id': False})

    def query_node_by_name(self, name):
        return self.db['node'].find({'name': name}, projection={'_id': False})

    def query_relation_by_id(self, id):
        return self.db['relation'].find({'id': id}, projection={'_id': False})

    def query_relation_by_name(self, name):
        return self.db['relation'].find({'name' : name}, projection={'_id': False})

    def query_node_by_basic_attr(self, attr):
        return self.db['node'].find(attr, projection={'_id': False})

    def query_attribute_by_node_id(self, id):
        return self.db['attribute'].find({'id':id}, projection={'_id': False})

    def query_attribute_by_multi_rules(self, json):
        return self.db['attribute'].find(json, projection={'_id': False})

    def query_triple_by_json(self, json):
        return self.db['triple'].find(json, projection={'_id': False})

    def query_entity_by_id(self, eid):
        e_base = self.query_node_by_id(eid)
        e_attribute = self.query_attribute_by_node_id(eid)
        e_triple = self.query_triple_by_json({'hid':eid})
        #
        if e_base.count() == 0:
            return None
        else:
            e_base = e_base[0]
        att = {}
        for e in e_attribute:
            # print(e)
            att[e['key']] = e['value']
        e_base['attrs'] = att
        tri = {}
        #
        # print(e_triple.count())
        for e in e_triple:
            # print(e)
            rel = self.query_relation_by_id(e['rid'])[0]['name']
            tname = self.query_node_by_id(e['tid'])[0]
            tail = {'id': tname['id'], 'name': tname['name']}
            if rel not in tri:
                tri[rel] = [tail]
            else:
                if len(tri[rel]) < 3:
                    tri[rel].append(tail)
        e_base['rels'] = tri
        # print(tri)
        return e_base

if __name__ == '__main__':
    # q = Query('192.168.10.158', 27017, 'testkg')
    pass
    # for c in cur:
    #     print(c)