__author__ = 'roger'

# base operator of mongo database

import json
import pymongo
import Base.MongoConn

class DBOperator(object):
    conn =None

    def __init__(self, user, port):
        self.conn = Base.MongoConn.Conn()
        self.conn.connect(user, port)

    # create kg with kgname
    # init the ip_pool
    def create_KG(self, kgname):
        db = self.conn.get_db(kgname)
        id_pool = {}
        id_pool['_id'] = 0
        id_pool['rid'] = 1000000
        id_pool['nid'] = 2000000
        # id_pool['ruleid'] = 3000000
        try:
            db['id_pool'].insert_one(id_pool)
        except:
            return False
        return True

    def delete_KG(self, kgname):
        db = self.conn.drop_database('testkg')
    # def drop_KG(self, kgname):
    #     db = self.conn.get_db(kgname)
    #     db.drop()

if __name__ == '__main__':
    db = DBOperator('192.168.10.158',27017)
    db.delete_KG('testkg')
    db.create_KG('testkg')