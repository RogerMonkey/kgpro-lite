import re

__author__ = 'roger'


def get_value_type(value):
    if type(value) == int:
        return 'int'
    elif type(value) == float:
        return 'float'
    elif type(value) == bool:
        return 'bool'
    else:
        return 'str'


def get_insert_node(id, name, concept, des, type):
    insert_node = {'id': id, 'name': name, 'type': type, 'des': des, 'concept': concept}

    return insert_node


def get_insert_relation(id, name, des, range, domain):
    insert_relation = {'id': id, 'name': name, 'des': des, 'range': range, 'domain': domain}

    return insert_relation


def get_insert_rule(id, name, des):
    insert_rule = {'id': id, 'name': name, 'des': des}

    return insert_rule


def get_insert_attribute_list(id, attributes):
    attribute = []
    for key in attributes:
        if type(attributes[key]) != list:
            attribute.append({'id': id, 'key': key,
                              'value': str(attributes[key]),
                              'type': get_value_type(attributes[key])})
        else:
            for k in attributes[key]:
                attribute.append({'id': id, 'key': key,
                                  'value': str(k),
                                  'type': get_value_type(k)})

    return attribute


def build_respond(ret_code, ret_desc, ret_choose=0, rsp_body=''):
    respond = {'ret_code': ret_code, 'ret_desc': ret_desc, 'ret_choose': ret_choose, 'rsp_body': rsp_body}
    return respond


def bulid_triple_query(json):
    query = {}
    q = {}
    c = {}
    for k in json:
        if json[k] != "":
            q[k] = json[k]
    query['q'] = q

    return query


def rule_parse(rule):
    if ':-' not in rule:
        return None
    result = re.findall(r'(var\(\w\)|\w+)', rule)
    if len(result) % 3 != 0:
        return None
    target = {
        'head': result[0],
        'rel': result[1],
        'tail': result[2]
    }
    body = []
    for x in range(3, len(result), 3):
        body.append({
            'head': result[x],
            'rel': result[x+1],
            'tail': result[x+2]
        })

    return {'target': target, 'body': body}


if __name__ == '__main__':
    print(rule_parse('(var(x),love,var(z)):-(var(x),friend,var(y)),(var(y),friend,var(z))'))
