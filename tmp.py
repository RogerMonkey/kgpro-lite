import codecs
from Base.Insert import *
import os
import datetime

path = '医疗知识图谱实例'


insert = Base.Insert.Insert('192.168.10.158',27017, 'testkg')
entity = {}
eid = 0
relation = {}
rid = 0
triple = []
for root, dir, filename in os.walk(path):
    for i in filename:
        print(i)
        f = codecs.open(path+"/"+i, encoding='utf8')
        for line in f.readlines():
            item = line.strip().replace('\ufeff' , '').split('\t')
            if len(item) < 3:
                print(item)
                continue
            if item[0] not in entity:
                entity[item[0]] = eid
                eid += 1
            if item[2] not in entity:
                entity[item[2]] = eid
                eid += 1
            if item[1] not in relation:
                relation[item[1]] = rid
                rid += 1

            triple.append([item[0], item[1], item[2]])

begin = datetime.datetime.now()
for i in range(1000):
    begin1 = datetime.datetime.now()
    for e in entity:
        result , id = insert.insert_one_node({'name': e, 'category':'', 'des': e, 'concept' : ''})
        # if result == True:
        entity[e] = id
        # else:
        #     print(e, result)

    for r in relation:
        result, id = insert.insert_one_relation({'name':r, 'des':'', 'range': '', 'domain':'', 'type': 'relation'})
        # if result == True:
        relation[r] = id
        # else:
        #     print(r, result)
    # print(triple)
    for t in triple:
        # print(entity[t[0]])
        insert.insert_one_attribute_or_triple_by_id({'hid': entity[t[0]], 'rid': relation[t[1]], 'tid': entity[t[2]]}, type='triple')
    end1 = datetime.datetime.now()
    print(end1 - begin1)
end = datetime.datetime.now()
print(end-begin)

print(len(entity))
print(entity)
print(len(relation))
print(len(triple))