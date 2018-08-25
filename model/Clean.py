## TransE

from Base.Query import *
import numpy as np


def distance(v1, v2):
    dist = np.linalg.norm(v1 - v2)
    sim = 1.0 / (1.0 + dist)
    return sim


def energe(h, r, t):
    return np.mean(np.abs(h + r - t), axis=1)


def clean(query, path, pars):
    entity2id = {}
    with open(path + '/entity2id.txt') as f:
        for line in f.readlines():
            line = line.split('\t')
            entity2id[int(line[1])] = int(line[0])
    print(entity2id)
    entity2vec = np.loadtxt(path + '/entity.bern', delimiter='\t')
    print(entity2vec.shape)

    simt = []
    for i in range(entity2vec.shape[0]):
        for j in range(i + 1, entity2vec.shape[0]):
            if distance(entity2vec[i, :], entity2vec[j, :]) > pars:
                simt.append([i, j, distance(entity2vec[i, :], entity2vec[j, :])])

    print(len(simt))
    log = ''
    with open('clean.txt', 'w') as f:
        log += '如下实体相似度高，可能存在同义实体！\n'
        for x in simt:
            e1 = query.query_node_by_id(entity2id[x[0]])[0]['name']
            e2 = query.query_node_by_id(entity2id[x[1]])[0]['name']
            log += '{0}\t{1} 相似度：{2}\n'.format(e1, e2, x[2])

    return log


def completion(hid, tid, path):
    entity2id = {}
    relation2id = {}
    id2relation = {}
    id2entity = {}
    with open(path + '/entity2id.txt') as f:
        for line in f.readlines():
            line = line.split('\t')
            entity2id[int(line[1])] = int(line[0])
            id2entity[int(line[0])] = int(line[1])
    with open(path + '/relation2id.txt') as f:
        for line in f.readlines():
            line = line.split('\t')
            relation2id[int(line[1])] = int(line[0])
            id2relation[int(line[0])] = int(line[1])

    entity2vec = np.loadtxt(path + '/entity.bern', delimiter='\t')
    relation2vec = np.loadtxt(path + '/relation.bern', delimiter='\t')
    hvec = entity2vec[id2entity[hid]]
    tvec = entity2vec[id2entity[tid]]

    score = energe(hvec, relation2vec, tvec)
    sidx = np.argsort(score)
    print(sidx[:10])
    return [[relation2id[x], score[x]] for x in sidx[:10]]


def similar(eid, query, path, pars):
    entity2id = {}
    id2entity = {}
    with open(path + '/entity2id.txt') as f:
        for line in f.readlines():
            line = line.split('\t')
            id2entity[int(line[1])] = int(line[0])
            entity2id[int(line[0])] = int(line[1])
    # print(entity2id)
    eid = entity2id[eid]
    entity2vec = np.loadtxt(path + '/entity.bern', delimiter='\t')
    print(entity2vec.shape)

    simt = {}
    for i in range(entity2vec.shape[0]):
        if i == eid:
            continue
        # for j in range(i + 1, entity2vec.shape[0]):
        if distance(entity2vec[eid, :], entity2vec[i, :]) > pars:
            simt[i] = distance(entity2vec[eid, :], entity2vec[i, :])

    print(len(simt))
    if len(simt) == 0:
        return None
    simt = sorted(simt.items(), key=lambda item:item[1], reverse=True)
    # print(simt)
    lenth = 4
    ett = []
    print(simt)
    for i in simt:
        if lenth == 0:
            break
        lenth -= 1
        # print(simt)
        # print(query.query_node_by_id(id2entity[i[0]])[0]['name'])
        ett.append([query.query_node_by_id(id2entity[i[0]])[0]['name'], i[1]])
    # print(ett)
    return ett
    # with open('clean.txt', 'w') as f:
        # log += '如下实体相似度高，可能存在同义实体！\n'
        # for x in simt:
        #     e1 = query.query_node_by_id(entity2id[x[0]])[0]['name']
            # e2 = query.query_node_by_id(entity2id[x[1]])[0]['name']

    # return log
