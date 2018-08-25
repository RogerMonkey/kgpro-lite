# structure test for row storage or column storage in mongodb
__author__ = 'roger'

from pymongo import MongoClient
import random

conn = MongoClient('localhost', 27017)

testkg = conn['testkg']

size = 5000000

values = ['apple','sansum','sony','xiaomi','roger']
test1 = []
test2 = []
for i in range(1,size+1):
    if i % 10000 == 0:
        print(i)
        testkg['test2'].insert_many(test2)
        testkg['test1'].insert_many(test1)
        test1 = []
        test2 = []
    testtmp = {'id':i}
    for x in range(64):
        key = 'key{0}'.format(x)
        rd = random.randint(1,100)
        value = '{0}_{1}'.format(values[rd%5],rd)
        testtmp[key] = value
        test2.append({'id': i, 'key': key, 'value': value})
    test1.append(testtmp)
    # testkg['test2'].insert_many(test2)
    # testkg['test1'].insert_one(test1)