__author__ = 'roger'

from Base.Insert import Insert
from Base.Delete import Delete
from Base.Query import Query
from Base.Update import Update
from Base.BaseOperator import *


class CommonService(object):
    insert = None
    update = None
    delete = None
    query = None

    def __init__(self, dbname='test'):
        self.insert = Insert('localhost', 27017, dbname)
        self.update = Update('localhost', 27017, dbname)
        self.delete = Delete('localhost', 27017, dbname)
        self.query = Query('localhost', 27017, dbname)

    def insertService(self, json):
        if json['operate'] != 'insert':
            return build_respond(0, '错误的操作类型')
        else:
            isForce = json['isForce']
            type = json['type']
            if isForce == 1:
                if type == 'concept' or type == 'entity':
                    success_list = self.insert.insert_many_node(json['body'])
                    print('success', success_list)
                    # TODO
                    if None in success_list:
                        return build_respond(0, '插入失败！', 1, [json['body'][i] for i in range(len(success_list)) if
                                                             success_list[i] is None])
                    else:
                        return build_respond(1, '插入全部成功！')
                elif type == 'relation' or type == 'rule':
                    success_list = self.insert.insert_many_relation(json['body'])
                    if None in success_list:
                        return build_respond(0, '插入失败！', 1, [json['body'][i] for i in range(len(success_list)) if
                                                             success_list[i] is None])
                    else:
                        return build_respond(1, '插入全部成功！')
                else:
                    return build_respond(0, '非法请求！')
            elif isForce == 0:
                if type == 'concept' or type == 'entity':
                    error_list = []
                    for term in json['body']:
                        res = self.query.query_node_by_name(term['name'])
                        if res.count() != 0:
                            el = []
                            for x in res:
                                x['_id'] = str(x['_id'])
                                el.append(x)
                            error_list.append(el)
                        else:
                            ins_suc, ins_id = self.insert.insert_one_node(term)
                            print(ins_suc, ins_id)
                            if ins_suc == False:
                                error_list.append(term)
                    if len(error_list) != 0:
                        return build_respond(0, '插入失败！', 1, error_list)
                    return build_respond(1, '插入全部成功！')
                elif type == 'rule' or type == 'relation':
                    error_list = []
                    for term in json['body']:
                        res = self.query.query_relation_by_name(term['name'])
                        if res.count() != 0:
                            el = []
                            for x in res:
                                x['_id'] = str(x['_id'])
                                el.append(x)
                            error_list.append(el)
                        else:
                            ins_suc, ins_id = self.insert.insert_one_relation(term)
                            print(ins_suc, ins_id)
                            if ins_suc == False:
                                error_list.append(term)
                    if len(error_list) != 0:
                        return build_respond(0, '插入失败！', 1, error_list)
                    return build_respond(1, '插入全部成功！')
            else:
                return build_respond(0, '非法isForce请求！')

    def deleteService(self, json):
        if json['operate'] != 'delete':
            return build_respond(0, '错误的操作类型')
        else:
            if 'body' not in json or 'type' not in json:
                return build_respond(0, '错误的参数结构')
            delete_type = json['type']
            delete_body = json['body']
            result = []
            if delete_type == 'triple':
                for e in delete_body:
                    if 'head' not in e or 'rel' not in e or 'tail' not in e:
                        return build_respond(0, '三元组结构错误！')
                    for x in e:
                        if x == 'head' or x == 'tail':
                            e[x] = [cur['id'] for cur in self.query.query_node_by_name(e[x])]
                        else:
                            e[x] = [cur['id'] for cur in self.query.query_relation_by_name(e[x])]
                        if json['isForce'] == False and len(e[x]) > 1:
                            return build_respond(0, '当前删除有冲突！', 1, e)
                        if len(e[x]) == 0:
                            return build_respond(0, '查询失败！', 1, e)
                for e in delete_body:
                    q = {
                        'hid': {'$in': e['head']},
                        'rid': {'$in': e['rel']},
                        'tid': {'$in': e['tail']},
                    }
                    print(q)
                    result.append(self.delete.delte_triple_by_json(q))
                return build_respond(1, '删除成功！', 0, result)
            else:
                flag = 1
                if delete_type == 'entity' or 'concept':
                    delid = self.delete.delete_entity_by_id
                    queryid = self.query.query_node_by_name
                else:
                    delid = self.delete.delete_triple_by_relation_id
                    queryid = self.query.query_relation_by_name
                for e in delete_body:
                    if 'id' in e:
                        r = delid(e['id'])
                        if r == True:
                            result.append(r)
                        else:
                            flag = 0
                            result.append(e['id'])
                    elif 'name' in e:
                        id_cur = queryid(e['name'])
                        if id_cur.count() == 0:
                            return build_respond(0, '无该实体！')
                        if json['isForce'] == False and id_cur.count() > 1:
                            flag = 0
                            result.append([i for i in id_cur])
                        else:
                            tmp = []
                            for x in id_cur:
                                r = delid(x['id'])
                                if r == True:
                                    tmp.append(r)
                                else:
                                    flag = 0
                                    tmp.append(x['id'])
                            result.append(tmp)
                return build_respond(flag, '删除成功', 1, result)

    def updateService(self, json):
        if json['operate'] != 'update':
            return build_respond(0, '错误的操作类型')
        else:
            if 'body' not in json or 'type' not in json:
                return build_respond(0, '错误的参数结构')
            if len(json['body']) > 1:
                return build_respond(0, '参数数量错误！')
            update_triple = json['body'][0]

            if json['isForce'] == 0:
                isForce = False
            else:
                isForce = True

            if json['type'] == 'ntity' or json['type'] == 'concept':
                target_id = json['id']
                att_udt = []
                node_udt = {}
                for x in update_triple:
                    if x != 'atts':
                        node_udt[x] = update_triple[x]

                self.update.update_node_by_base_id(target_id, node_udt, isForce)
                print(self.delete.delete_attribute_by_entity_id(target_id))
                print(get_insert_attribute_list(target_id, update_triple['atts']))
                print(self.insert.insert_many_attribute_or_triple(get_insert_attribute_list(target_id, update_triple['atts']), 'attribute'))
                return build_respond(1, '更新成功！')
            elif json['type'] == 'relation' or json['type'] == 'rule':
                target_id = json['id']
                self.update.update_rel_by_base_id(target_id, update_triple, isForce)
                return build_respond(1, '更新成功！')

            elif json['type'] == 'triple':
                body = json['body']
                old = {
                    'hid' : update_triple['old']['head'],
                    'rid' : update_triple['old']['rel'],
                    'tid' : update_triple['old']['tail']
                }

                new = {
                    'hid': update_triple['new']['head'],
                    'rid': update_triple['new']['rel'],
                    'tid': update_triple['new']['tail']
                }

                return build_respond(1,'更新成功！')

    def queryTripleService(self, json):
        if json['operate'] != 'query':
            return build_respond(0, '错误的操作类型')
        else:
            if 'body' not in json:
                return build_respond(0, '错误的参数结构，缺少body')

            query_triples = json['body']

            for triple in query_triples:
                if 'head' not in triple or 'rel' not in triple or 'tail' not in triple:
                    return build_respond(0, 'body内三元组查询结构错误')

            if len(query_triples) == 1:
                triple = query_triples[0]
                triple = bulid_triple_query(triple)['q']
                query = {}
                print(triple)
                if 'head' in triple:
                    try:
                        query['hid'] = {'$in': [int(triple['head'])]}
                    except:
                        query['hid'] = {'$in': [e['id'] for e in self.query.query_node_by_name(triple['head'])]}
                if 'rel' in triple:
                    try:
                        query['rid'] = {'$in': [int(triple['rel'])]}
                    except:
                        query['rid'] = {'$in': [e['id'] for e in self.query.query_relation_by_name(triple['rel'])]}
                if 'tail' in triple:
                    try:
                        query['tid'] = {'$in': [int(triple['rel'])]}
                    except:
                        query['tid'] = {'$in': [e['id'] for e in self.query.query_node_by_name(triple['tail'])]}

                result = self.query.query_triple_by_json(query)
                return build_respond(1, '查询三元组成功！', 1, [r for r in result])

            else:
                result = {}
                query = {}
                for triple in query_triples:
                    if 'var' not in triple['head']:
                        try:
                            query['hid'] = {'$in': [int(triple['head'])]}
                        except:
                            query['hid'] = {'$in': [e['id'] for e in self.query.query_node_by_name(triple['head'])]}
                    else:
                        if triple['head'] not in result:
                            result[triple['head']] = {'loc': 'head', 'r': []}
                        else:
                            result[triple['head']]['loc'] = 'head'
                            query['hid'] = {'$in': result[triple['head']]['r']}

                    if 'var' not in triple['rel']:
                        try:
                            query['rid'] = {'$in': [int(triple['rel'])]}
                        except:
                            query['rid'] = {'$in': [e['id'] for e in self.query.query_relation_by_name(triple['rel'])]}
                    else:
                        if triple['rel'] not in result:
                            result[triple['rel']] = {'loc': 'rel', 'r': []}
                        else:
                            result[triple['rel']]['loc'] = 'rel'
                            query['rid'] = {'$in': result[triple['rel']]['r']}

                    if 'var' not in triple['tail']:
                        try:
                            query['tid'] = {'$in': [int(triple['tail'])]}
                        except:
                            query['tid'] = {'$in': [e['id'] for e in self.query.query_node_by_name(triple['tail'])]}
                    else:
                        if triple['tail'] not in result:
                            result[triple['tail']] = {'loc': 'tail', 'r': []}
                        else:
                            result[triple['tail']]['loc'] = 'tail'
                            query['tid'] = {'$in': result[triple['tail']]['r']}

                    print('query', query)
                    print(result)
                    result_tmp = self.query.query_triple_by_json(query)
                    h_tmp = []
                    r_tmp = []
                    t_tmp = []
                    for x in result_tmp:
                        h_tmp.append(x['hid'])
                        r_tmp.append(x['rid'])
                        t_tmp.append(x['tid'])

                    print(h_tmp, r_tmp, t_tmp)
                    for x in result:
                        if result[x]['loc'] == 'head':
                            if len(result[x]['r']) == 0:
                                result[x]['r'] = list(set(h_tmp))
                            else:
                                result[x]['r'] = list(set(result[x]['r']) & set(h_tmp))
                        if result[x]['loc'] == 'rel':
                            if len(result[x]['r']) == 0:
                                result[x]['r'] = list(set(r_tmp))
                            else:
                                result[x]['r'] = list(set(result[x]['r']) & set(r_tmp))
                        if result[x]['loc'] == 'tail':
                            if len(result[x]['r']) == 0:
                                result[x]['r'] = list(set(t_tmp))
                            else:
                                result[x]['r'] = list(set(result[x]['r']) & set(t_tmp))

                return build_respond(1, '查询成功，返回结果如下', 1, result)

    def querySingleService(self, json):
        if json['type'] == 'entity' or json['type'] == 'concept' and json['class'] == 'id':
            try:
                return build_respond(1, '查询成功', 1, [self.query.query_entity_by_id(json['key'])])
            except:
                return build_respond(0, '未找到指定目标！')

        if json['type'] == 'entity' or json['type'] == 'concept' and json['class'] == 'name':
            entites = self.query.query_node_by_name(json['key'])
            result = []
            for entity in entites:
                try:
                    result.append(self.query.query_entity_by_id(entity['id']))
                except:
                    result.append({'name': entity['name'], 'result': False})

            return build_respond(1, '查询成功', 1, result)

        if json['type'] == 'relation' or json['type'] == 'rule' and json['class'] == 'id':
            try:
                return build_respond(1, '查询成功', 1, [e for e in self.query.query_relation_by_id(json['key'])])
            except:
                return build_respond(0, '未找到指定目标！')

        if json['type'] == 'relation' or json['type'] == 'rule' and json['class'] == 'name':
            try:
                return build_respond(1, '查询成功', 1, [e for e in self.query.query_relation_by_name(json['key'])])
            except:
                return build_respond(0, '未找到指定目标！')

    def inferenceService(self, json):
        if json['class'] == 'name':
            rule = self.query.query_relation_by_name(json['key'])
            if rule.count() > 1:
                return build_respond(0, '多个规则推理冲突')

        else:
            rule = self.query.query_relation_by_id(json['key'])

        if rule.count() == 0:
            return build_respond(0, '查无规则')
        rule = rule[0]

        # TODO:判断是否是规则
        if 'range' in rule:
            return build_respond(0, '非规则不能推理')

        rule = rule['des']
        rule = rule_parse(rule)
        rule['operate'] = 'query'
        if rule == None:
            return build_respond(0, '规则解析失败！')
        result_raw = self.queryTripleService(rule)
        if result_raw['ret_code'] == 1 and 'rsp_body' in result_raw and result_raw['rsp_body'] != None and len(
                result_raw['rsp_body']) > 0:
            for x in rule['target']:
                if rule['target'][x] in result_raw['rsp_body']:
                    rule['target'][x] = result_raw['rsp_body'][rule['target'][x]]['r']
            print(rule['target'])
            return build_respond(1, '推理成功！', 1, rule['target'])
        else:
            return build_respond(0, '规则推理失败！')