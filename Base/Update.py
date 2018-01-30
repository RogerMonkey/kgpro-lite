__author__ = 'roger'

# base insert function

import json
import pymongo
import Base.MongoConn

class Update(object):
    db = None

    def __init__(self, user, port, dbname):
        conn = Base.MongoConn.Conn()
        conn.connect(user, port)
        self.db = conn.get_db(dbname)

    def update_node_by_base_id(self, id, json, isForce):
        return self.db['node'].update_one({'id' : id}, {'$set' : json}, isForce)

    def update_rel_by_base_id(self, id, json, isForce):
        return self.db['relation'].update_one({'id' : id}, {'$set' : json}, isForce)

    def update_attrs_by_entity_id(self, id, json, isForce):
        return self.db['attribute'].update_one({'id' : id}, {'$set' : json}, isForce)

    def update_triple_by_id(self, ojson, njson):
        return self.db['triple'].update_one(ojson, {'$set':njson})