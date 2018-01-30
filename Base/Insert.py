__author__ = 'roger'

# base insert function

import json
import Base.MongoConn
from Base.BaseOperator import *


class Insert(object):
    db = None

    def __init__(self, user, port, dbname):
        conn = Base.MongoConn.Conn()
        conn.connect(user, port)
        self.db = conn.get_db(dbname)

    ## insert node
    def insert_one_node(self, jsonnode):

        ## 从id池获取id
        id = self.db['id_pool'].find_one_and_update({'_id': 0}, {'$inc': {'nid': 1}})['nid']

        ## 生成插入节点
        try:
            insert_node = get_insert_node(id, jsonnode['name'],
                                          jsonnode['category'],
                                          jsonnode['des'],
                                          jsonnode['concept'])
        except:
            # TODO：缺少属性提示
            return False, None

        ## 生成其他属性
        attribute = []
        if ('atts' in jsonnode):
            attribute = get_insert_attribute_list(id, jsonnode['atts'])
        try:
            self.db['node'].insert_one(insert_node)
            if len(attribute) != 0:
                self.db['attribute'].insert_many(attribute)
        except:
            # TODO:插入失败提示
            return False, None

        return True, id

    # TODO:批量实现
    def insert_many_node(self, jsonlist):
        success_list = []
        for json in jsonlist:
            res = self.insert_one_node(json)
            success_list.append(res[1])
        return success_list

    def insert_one_relation(self, jsonnode):
        ## 从id池获取id
        id = self.db['id_pool'].find_one_and_update({'_id': 0}, {'$inc': {'rid': 1}})['rid']

        if jsonnode['type'] == 'relation':
            try:
                insert_relation = get_insert_relation(id,
                                                      jsonnode['name'],
                                                      jsonnode['des'],
                                                      jsonnode['range'],
                                                      jsonnode['domain'],
                                                      )
            except:
                # TODO:缺少属性提示
                return False, None
        elif jsonnode['type'] == 'rule':
            try:
                insert_relation = get_insert_rule(id,
                                                  jsonnode['name'],
                                                  jsonnode['des']
                                                  )
            except:
                # TODO:缺少属性提示
                return False, None
        else:
            # TODO：未知类型
            return False, None

        try:
            self.db['relation'].insert_one(insert_relation)
        except:
            # TODO:插入失败提示
            return False, None
        return True, id

    # TODO：批量操作
    def insert_many_relation(self, jsonlist):
        success_list = []
        for json in jsonlist:
            res = self.insert_one_relation(json)
            success_list.append(res[1])
        return success_list

    def insert_one_attribute_or_triple_by_id(self, json, type):
        if type == 'attribute':
            if 'id' not in json or 'key' not in json or 'value' not in json or 'type' not in json:
                # TODO: 缺少属性提示
                return False
            try:
                self.db['attribute'].insert_one(json)
            except:
                return False
            return True
        elif type == 'triple':
            if 'hid' not in json or 'rid' not in json or 'tid' not in json:
                return False
            try:
                self.db['triple'].insert_one(json)
            except:
                return False
            return True
        else:
            return False

    def insert_many_attribute_or_triple(self, jsonlist, type):
        success_list = []
        for json in jsonlist:
            success_list.append(self.insert_one_attribute_or_triple_by_id(json, type))
        return success_list


if __name__ == '__main__':
    insert = Insert('localhost', 27017, 'testkg')
    # print(insert.insert_one_node({
    #     'name': 'lucille',
    #     'des': 'roger love her.',
    #     'category': 'student',
    #     'concept':'woman',
    #     'atts':{
    #         '性别':'女',
    #     }
    # }))
    # print(insert.insert_one_node({
    #     'name': 'roger',
    #     'des': 'roger love cl.',
    #     'category': 'student',
    #     'concept': 'man',
    #     'atts': {
    #         '特征': '讨人厌',
    #     }
    # }))
    # print(insert.insert_one_relation({
    #     'name': 'friend',
    #     'des': 'is it true?',
    #     'type': 'relation',
    #     'domain':'people',
    #     'range':'people'
    # }))
    print(insert.insert_one_attribute_or_triple_by_id({
        'hid': 2000000,
        'rid': 1000000,
        'tid': 2000001,
    }, 'triple'
    ))
    # print(insert.insert_one_relation({
    #     'name': 'danlian',
    #     'des': '(var(x),love,var(z)):-(var(x),friend,var(y)),(var(y),friend,var(z))',
    #     'type': 'rule',
    # }))

