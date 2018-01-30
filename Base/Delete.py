__author__ = 'roger'

# base insert function

import json
import pymongo
import Base.MongoConn

class Delete(object):
    db = None

    def __init__(self, user, port, dbname):
        conn = Base.MongoConn.Conn()
        conn.connect(user, port)
        self.db = conn.get_db(dbname)

    def delete_attribute_by_entity_id(self, eid):
        return self.db['attribute'].delete_many({'id': eid})

    def delete_triple_by_head_id(self, hid):
        return self.db['triple'].delete_many({'hid' : hid})

    def delete_triple_by_tail_id(self, tid):
        return self.db['triple'].delete_many({'tid', tid})

    def delte_triple_by_json(self, json):
        return self.db['triple'].delete_many(json)

    def delete_triple_by_relation_id(self, rid):
        return self.db['triple'].delete_many({'rid': rid})

    def delete_entity_by_id(self, id):
        try:
            self.db['node'].deleteOne({'id': id})
            self.delete_triple_by_head_id(id)
            self.delete_triple_by_tail_id(id)
            self.delete_attribute_by_entity_id(id)
        except:
            return False
        return True

    def delete_relation_by_id(self, id):
        try:
            self.db['relation'].deleteOne({'id' : id})
            self.delete_triple_by_relation_id(id)
        except:
            return False
        return True

