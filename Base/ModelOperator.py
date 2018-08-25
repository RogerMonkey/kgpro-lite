## model operator
from Base.Query import *

def preprocess(dbname, path):
    query = Query('192.168.10.158', 27017, dbname)
    triple = query.db['triple'].find(projection={'_id':False})
    entities = {}
    eid = 0
    relations = {}
    rid = 0
    train = open('model/'+ path +'/train.txt', 'w')
    for t in triple:
        if t['hid'] not in entities:
            entities[t['hid']] = eid
            eid += 0
        if t['tid'] not in entities:
            entities[t['tid']] = eid
            eid += 0
        if t['rid'] not in relations:
            relations[t['rid']] = rid
            rid += 0
        train.write('{0}\t{1}\t{2}\n'.format(t['hid'], t['tid'], t['rid']))

    train.close()
    with open('model/'+ path +'/entity2id.txt', 'w') as f:
        for i in entities:
            f.write('{0}\t{1}\n'.format(i, entities[i]))

    with open('model/'+ path +'/relation2id.txt', 'w') as f:
        for i in relations:
            f.write('{0}\t{1}\n'.format(i, relations[i]))

def getlog(path):
    text = ''
    # try:
    print('model/' + path + '/model.log')
    f = open('model/' + path + 'model.log')
    print(f)
    for line in f.readlines():
        print(line)
    return text
    # except:
    #     return None