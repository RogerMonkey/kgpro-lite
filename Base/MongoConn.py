__author__ = 'roger'

from pymongo import MongoClient

class Conn(object):

    conn = None
    def __init__(self):
        pass

    def connect(self, user, port):
        if self.conn is None:
            self.conn = MongoClient(user, port)
        else:
            ## todo
            print('already')

    def get_db(self, dbname):
        if self.conn is not None:
            return self.conn[dbname]
        else:
            ## todo
            return None

    def unconnect(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def drop_database(self, param):
        self.conn.drop_database(param)


if __name__ == '__main__':
    con = Conn()
    con.connect('localhost', 27017)
    print(con.get_db('test'))
