# coding=utf-8
# Filename dbclt.py, 是对本体数据操作所需要的底层模块

# 对于数字，可以考虑其id号为，i_数字  便于提高数字的处理效率。
from msvcrt import CRT_ASSEMBLY_VERSION
import pymongo
from pymongo.mongo_client import MongoClient
import re
from _overlapped import NULL
from tkinter.constants import RIDGE
import xlrd
import xlwt
import globalinfo
import math
from collections import OrderedDict
from errno import ECONNABORTED
import pymysql
import pymysql.cursors


# read from file


# con=MongoClient('localhost',27017)
# ontodb=con['taskonto']
# idcol=ontodb['idrec']
# rec=idcol.find()[0]
#
# conid=rec['conid']
# resid=rec['resid']
# attid=rec['attid']
# insid=rec['insid']

class Dbc:
    def __init__(self, c):
        self.name = c

    def find_all(self):
        return self.name.find()

    def find_key_value(self, key, val):
        temp = self.name.find({key: val}).count()
        if temp:
            self.data = self.name.find({key: val})
        else:
            self.data = NULL
        # print(self.name)
        return self.data

    def find_keys(self, key, val):
        keys = self.name.find_one({key: val}).keys()
        return keys

    def find_vals(self, key, val):
        vals = self.name.find_one({key: val}).values()
        return vals

    def insert_key_value(self, key, val):  # 插入一个新的键和值
        self.name.insert_one({key: [val]})

    def insert_key_none_of_rec(self, key, val, inkey):
        self.name.update({key: val}, {"$set": {inkey: []}})

    def insert_key_value_of_rec(self, key, val, newkey, newval):  # 插入某一个记录的键和值，如果键不存在，则在记录中增加该键。
        self.name.update({key: val}, {'$addToSet': {newkey: newval}})

    def update_key_value_of_rec(self, key, val, findkey, oldval, newval):
        self.name.update({key: val}, {'$addToSet': {findkey: newval}})
        self.name.update({key: val}, {'$pull': {findkey: oldval}})

    def update_idres(self, idtype, ids):
        self.name.update({'idrec': 'idrec'}, {"$set": {idtype: ids}})

    def delete_key_value_of_rec(self, key, val, findkey, oldval):  ##删除某一个记录的键和值，如果键不存在，则在记录中增加该键。
        self.name.update({key: val}, {'$pull': {findkey: oldval}})

    def delete_key_of_rec(self, key, val, findkey):  # 删除某一个记录的键。
        self.name.update({key: val}, {'$unset': {findkey: 1}})

    def update_key_of_rec(self, key, val, findkey, newkey):  #
        temp1 = self.name.find({key: val})
        temp2 = {}
        temp2[newkey] = temp1[0][findkey]
        self.name.update({key: val}, {'$unset': {findkey: 1}})
        self.name.update({key: val}, {'$set': {newkey: temp2[newkey]}})

    def insert_dict_of_rec(self, dic):
        self.name.insert(dic)

    def delete_doc(self, key, val):
        self.name.remove({key: val})


class OntoLow:
    colct = 0
    colcd = 0
    colrt = 0
    colrd = 0
    colid = 0

    def __init__(self, cct, ccd, crt, crd, cid, idrec):
        self.colct = Dbc(cct)
        self.colcd = Dbc(ccd)
        self.colrt = Dbc(crt)
        self.colrd = Dbc(crd)
        self.colid = Dbc(cid)
        self.colidrec = Dbc(idrec)

    # 		self.conid=self.colid.find_key_value('idtype', 'conid')[0]['idpool']
    # 		self.insid=self.colid.find_key_value('idtype', 'insid')[0]['idpool']
    # 		self.relid=self.colid.find_key_value('idtype', 'relid')[0]['idpool']
    # 		self.attid=self.colid.find_key_value('idtype', 'attid')[0]['idpool']

    def find_method_in_relation_term(self, str):
        methods = self.colrd.find_key_value('rid', re.compile(str))
        return methods

    def insert_new_concept(self, dictct, dictcd):
        self.colct.insert_dict_of_rec(dictct)
        self.colcd.insert_dict_of_rec(dictcd)

    def insert_new_relation(self, dictrt, dictrd):
        self.colrt.insert_dict_of_rec(dictrt)
        self.colrd.insert_dict_of_rec(dictrd)

    def find_concepts_data(self):
        cons = self.colcd.find_all()
        return cons

    def find_concepts_term(self):
        cons = self.colct.find_all()
        return cons

    def fuzzy_find_concepts_term(self, str):
        cons = self.colct.find_key_value('term', re.compile(str))
        return cons

    def fuzzy_find_relations_term(self, str):
        cons = self.colrt.find_key_value('term', re.compile(str))
        return cons

    ##conterm 表中的操作方法
    def update_concept_term(self, term, newterm):
        self.colct.update_key_value_of_rec('term', term, 'term', term, newterm)

    def update_concept_cid(self, term, oldid, newid):
        self.colct.update_key_value_of_rec('term', term, 'cid', oldid, newid)

    def update_idrec(self, idtype, ids):
        self.colidrec.update_idres(idtype, ids)

    def delete_concept_cid(self, term, findid):
        self.colct.delete_key_value_of_rec('term', term, 'cid', findid)
        temp = self.colct.find_key_value('term', term)[0]['cid']
        if not temp:
            self.colct.delete_doc('term', term)
        else:
            return temp

    def insert_concept_cid(self, term, findid):
        self.colct.insert_key_value_of_rec('term', term, 'cid', findid)
        return findid

    def insert_concept_term(self, term):
        self.colct.insert_key_value('term', term)

    def find_concept_term(self, term):
        if self.colct.find_key_value('term', term):
            con = self.colct.find_key_value('term', term)
        else:
            con = NULL
        return con

    def delete_concept_termorid(self, term, cid):  # 如果term所对应的id号只有一个，则全部删除，否则只删除其中一个
        temp = self.colct.find_key_value("term", term)
        if len(temp['cid']) == 1:
            self.delete_concept_term(term)
        else:
            self.colct.delete_key_value_of_rec('term', term, 'cid', cid)

    def delete_concept_term(self, term):
        self.colct.delete_doc('term', term)

    def find_concept_cid_colterm(self, findid):
        con = self.colct.find_key_value('cid', findid)[0]
        return con['term']

    def find_rels_vals_of_concept(self, findid):
        rels = self.colcd.find_keys('cid', findid)
        vals = self.colcd.find_vals('cid', finid)
        return rels, vals

    def find_cid_with_term(self, term):
        id = self.colct.find_key_value('term', term)
        return id[0]['cid']

    ##conterm 表中的操作方法

    ##relterm 表中的操作方法
    def update_relation_term(self, term, newterm):
        self.colrt.update_key_value_of_rec('term', term, 'term', term, newterm)

    def update_relation_cid(self, term, oldid, newid):
        self.colrt.update_key_value_of_rec('term', term, 'rid', oldid, newid)

    def delete_relation_cid(self, term, findid):
        self.colrt.delete_key_value_of_rec('term', term, 'rid', findid)
        temp = self.colrt.find_key_value('term', term)[0]['rid']
        if not temp:
            self.delete_relation_term(term)
        else:
            return temp

    def insert_relation_cid(self, term, findid):
        self.colrt.insert_key_value_of_rec('term', term, 'rid', findid)
        return findid

    def insert_relation_term(self, term):
        self.colrt.insert_key_value('term', term)

    def find_relation_term(self, term):
        if self.colrt.find_key_value('term', term):
            con = self.colrt.find_key_value('term', term)
        else:
            con = NULL
        return con

    def delete_relation_term(self, term):
        self.colrt.delete_doc('term', term)

    def find_relation_rid_colterm(self, findid):
        con = self.colrt.find_key_value('rid', findid)[0]
        return con['term']

    ##relterm 表中的操作方法

    ##condata表中的操作方法
    def find_concept_data(self, findid):
        temp = self.colcd.find_key_value('cid', findid)
        if temp:
            con = temp[0]
        else:
            con = NULL
        return con

    def insert_concept_data(self, newid):
        self.colcd.insert_key_value('cid', newid)

    def delete_concept_data(self, findid):
        self.colcd.delete_doc('cid', findid)

    def update_cid_of_concept(self, oldid, newid):
        self.colcd.update_key_value_of_rec('cid', oldid, 'cid', oldid, newid)

    def find_val_of_rel_concept(self, findid, findrel):
        if findrel in self.colcd.find_key_value('cid', findid)[0].keys():
            temp = self.colcd.find_key_value('cid', findid)[0][findrel]
        else:
            temp = []
        return temp

    def delete_val_rel_of_concept(self, findid, findrel, relval):
        self.colcd.delete_key_value_of_rec('cid', findid, findrel, relval)

    def update_val_of_rel_concept(self, findid, findrel, oldval, newval):
        self.colcd.update_key_value_of_rec('cid', findid, findrel, oldval, newval)

    def insert_val_of_rel_concept(self, findid, findrel, newval):
        self.colcd.insert_key_value_of_rec('cid', findid, findrel, newval)

    def update_rel_of_concept(self, findid, findrel, newrel):
        self.colcd.update_key_of_rec('cid', findid, findrel, newrel)

    def insert_rel_of_concept(self, findid, newrel, relval):
        self.colcd.insert_key_value_of_rec('cid', findid, newrel, relval)
        inv_newrel = self.get_invers_relid(newrel)
        self.colcd.insert_key_value_of_rec('cid', relval, inv_newrel, findid)

    def insert_rels_of_concept(self, findid, rels):
        for k in rels:
            self.colcd.insert_key_none_of_rec('cid', findid, k)

    def delete_rel_of_concept(self, findid, findrel):
        self.colcd.delete_key_of_rec('cid', findid, findrel)

    def find_concepts_with_rel(self, findrel):
        c = set('')
        for cons in self.colcd.find_all():
            if findrel in cons.keys():
                c.add(cons)

        return c

    def find_concepts_with_relval(self, findrel, relval):
        c = []
        for cons in self.colcd.find_key_value(findrel, relval):
            c.append(cons['cid'][0])
        # print(cons['cid'])
        return c

    def get_inverse_rid(self, rid):
        if (int(rid) % 2):
            d = str(int(rid) + 1)
        else:
            d = str(int(rid) - 1)
        return d

    ##condata表中的操作方法
    def generate_id(self):
        # self.colid.insert_key_value('idtype','conid')
        # self.colid.insert_key_value('idtype','insid')
        # self.colid.insert_key_value('idtype','attid')
        # self.colid.insert_key_value('idtype','relid')

        for i in range(734303, 2999999):
            print('ids   ', i)
            self.colid.insert_key_value_of_rec('idtype', 'insid', 'idpool', str(1100000000 + i))
            '''
            if i<999999:
                self.colid.insert_key_value_of_rec('idtype', 'conid', 'idpool', str(1000000000+i))
                self.colid.insert_key_value_of_rec('idtype', 'attid', 'idpool', str(2000000000+2*i+1))
                self.colid.insert_key_value_of_rec('idtype', 'relid', 'idpool', str(2100000000+2*i+1))
            '''
            ##对idpool中的id号进行操作

    def get_id(self, idtype):
        if idtype == 'conid':
            needid = self.conid[0]
            self.conid.remove(needid)
        if idtype == 'insid':
            needid = self.insid[0]
            self.insid.remove(needid)
        if idtype == 'relid':
            needid = self.relid[0]
            self.relid.remove(needid)
        if idtype == 'attid':
            needid = self.attid[0]
            self.attid.remove(needid)
        self.colid.delete_key_value_of_rec('idtype', idtype, 'idpool', needid)

        return needid

    def put_id(self, idtype, newid):
        self.colid.insert_key_value_of_rec('idtype', idtype, 'idpool', newid)

    def get_invers_relid(self, relid):
        t1 = int(relid[-1])
        if (t1 % 2) == 0:
            rel = str(int(relid) - 1)
        else:
            rel = str(int(relid) + 1)

        return rel

    ##对idpool中的id号进行操作

    ##reldata表中的操作方法
    def find_relation_data(self, findid):
        temp = self.colrd.find_key_value('rid', findid)
        if temp:
            con = temp[0]
        else:
            con = NULL
        return con

    def insert_relation_data(self, newid):
        self.colrd.insert_key_value('rid', newid)

    def delete_relation_data(self, findid):
        self.colrd.delete_doc('rid', findid)

    def update_rid_of_relation(self, oldid, newid):
        self.colrd.update_key_value_of_rec('rid', oldid, 'rid', oldid, newid)

    def find_val_of_rel_relation(self, findid, findrel):
        if findrel in self.colrd.find_key_value('rid', findid)[0].keys():
            temp = self.colrd.find_key_value('rid', findid)[0][findrel]
        else:
            temp = []
        return temp

    def delete_val_rel_of_relation(self, findid, findrel, relval):
        self.colrd.delete_key_value_of_rec('rid', findid, findrel, relval)

    def update_val_of_rel_relation(self, findid, findrel, oldval, newval):
        self.colrd.update_key_value_of_rec('rid', findid, findrel, oldval, newval)

    def insert_val_of_rel_relation(self, findid, findrel, newval):
        self.colrd.insert_key_value_of_rec('rid', findid, findrel, newval)

    def update_rel_of_relation(self, findid, findrel, newrel):
        self.colrd.update_key_of_rec('rid', findid, findrel, newrel)

    def insert_rel_of_relation(self, findid, newrel, relval):
        self.colrd.insert_key_value_of_rec('rid', findid, newrel, relval)
        inv_reval = self.get_invers_relid(relval)
        self.colrd.insert_key_value_of_rec('rid', findid, newrel, inv_reval)
        inv_newrel = self.get_invers_relid(newrel)
        self.colrd.insert_key_value_of_rec('rid', relval, inv_newrel, findid)
        self.colrd.insert_key_value_of_rec('rid', inv_reval, inv_newrel, findid)

    def delete_rel_of_relation(self, findid, findrel):
        self.colrd.delete_key_of_rec('rid', findid, findrel)

    def find_relations_with_rel(self, findrel):
        c = set('')
        for cons in self.colrd.find_all():
            if findrel in cons.keys():
                c.add(cons)

        return c

    def remove_str_key(self,strkeylist,rellist):
        for str in strkeylist:
            if str in rellist:
                rellist.remove(str)
        return rellist

##reldata表中的操作方法



class OntoMid:
    is_a = '2100000001'
    superclass_of = '2100000002'
    instace_of = '2100000003'
    has_instance = '2100000004'
    onto_null = '0000000000'
    onto_root = '1000000000'
    ontocols = 0

    def __init__(self, ontodb):

        db = globalinfo.con[ontodb]
        colct = db['ConTerm']
        colcd = db['ConData']
        colrt = db['RelTerm']
        colrd = db['RelData']
        colid = db['idPool']
        colidrec = db['idrec']
        self.ontocols = OntoLow(colct, colcd, colrt, colrd, colid, colidrec)

    def judge_ontoid(self,idval):
        if idval[0] in globalinfo.idtype and idval[1:].isdigit():
            return True
        else:
            return False

    def find_into_for_searchbox(self, mat, keystr):
        # globalinfo.trifirst=[]# 三元组第一元
        # globalinfo.trisecond=[]# 三元组第二元
        # globalinfo.trithird=[]# 三元组第三元
        retinfo = []  # 返回的信息
        # globalinfo.rettemp=[]#临时信息存储
        if not mat:  # 如果前台来的列表为空
            if keystr:  # 如果前台传来的字符串不为空
                retinfo = self.fuzzy_find_in_contermtable(keystr) + self.fuzzy_find_in_reltermtable(
                    keystr)  # 在数据库中模糊查询keystr中的内容

        else:  # 如果前台传来的列表不为空
            if (len(mat) - 1) % 2 == 0:  # 检查最后一个列表最后一个元素的位置，如果位置为偶数
                if not globalinfo.trifirst:  # 如果trifirst中为空，说明这是第一次赋值
                    globalinfo.trifirst = mat[len(mat) - 1]  # 这时把最后一个值给trifirst
                else:  # 如果trifirst不为空，说明这不是第一次赋值，则把这个值赋给trithird
                    globalinfo.trithird = mat[len(mat) - 1]  # 给trithird赋值
            elif (len(mat) - 1) % 2 == 1:  # 如果为奇数，则肯定是关系数据
                globalinfo.trisecond = mat[len(mat) - 1]  # 因此赋值给trisecond

            if keystr == ' ':  # 如果前台传来空格
                # if (len(mat) - 1) % 2 == 0:#检查列表最后一个数的位置，如果是偶数
                #     globalinfo.trifirst = mat[len(mat) - 1]#则把该值放到三元组中的第一个。
                #     globalinfo.trisecond = []# 把第二个和第三个清空
                #     globalinfo.trithird = []
                # elif (len(mat) - 1) % 2 == 1:#如果最后一个数的位置是奇数
                #     globalinfo.trisecond = mat[len(mat) - 1]#则把最后一个数赋值给第二个


                globalinfo.rettemp = self.find_info_of_csyn_id(globalinfo.trifirst,
                                                               globalinfo.trisecond)  # 获取csyn,如果第二项为空，则返回第一项的关系的csyn，如果第二项不为空，则返回第一项的某关系的值的csyn

                # globalinfo.rettemp = []

                tl = []
                for g in globalinfo.rettemp:
                    if 'second' in g:
                        for t in g['second']:
                            if t not in tl:
                                tl.append(t)
                    else:
                        tl = []

                # print(globalinfo.rettemp)
                retinfo = tl
                # retinfo=globalinfo.rettemp

            elif keystr != '?' and keystr != '^':  # 如果不是？，即为其它的汉字或符号的情况下，是在上面的cysn中进行模糊查询。

                retinfo = self.fuzzy_find_info_in_csyn(keystr, globalinfo.rettemp)  # 模糊查询

            if keystr == '^':  # 相当于点击了搜索按钮
                retinfo = self.get_all_info_of_search(globalinfo.trifirst, globalinfo.trisecond,
                                                      globalinfo.trithird)  # 返回全部信息，分别提供给图和表

        return retinfo

    #
    # 			if keystr=='^':
    #
    #
    #  		return retinfo

    def fuzzy_find_rel_info_in_csyn(self, clist, keystr):
        infolist = []
        globalinfo.rettemp = self.find_info_of_csyn_id(clist,
                                                       [])  # 获取csyn,如果第二项为空，则返回第一项的关系的csyn，如果第二项不为空，则返回第一项的某关系的值的csyn
        infolist = self.fuzzy_find_info_in_csyn(keystr, globalinfo.rettemp)
        return infolist

    def fuzzy_find_info_in_csyn(self, keystr, slist):  # 在cysn中进行模糊查询
        infolist = []
        for sl in slist:
            if keystr in sl['name']:
                infolist.append(sl)
        return infolist

    # def find_info_of_csyn_id(self, cid1, rid):  # 这部分内容是用来返回输入空格后的信息 #cid1 = <type:list>
    #     infolist = []
    #
    #     if cid1 and not rid:#如果rid为空，则返回该cid的关系的csyn
    #         for c in cid1:
    #
    #             rel = list(self.ontocols.find_concept_data(c).keys())#把cid对应的所有关系都列出来
    #             rel.remove('cid')#去掉三个关系
    #             rel.remove('_id')
    #             rel.remove('csyn')
    #             for r in rel: #rel中是所需关系
    #                 tempdict = {}
    #                 csyn = self.ontocols.find_val_of_rel_relation(r, 'csyn')[0]#得到关系的
    #                 tempdict['name'] = csyn
    #                 tempdict['value'] = r#返回
    #                 if tempdict not in infolist:
    #                     infolist.append(tempdict)
    #                 # print(infolist)
    #
    #     if cid1 and rid and rid != '?':
    #         for c in cid1:
    #             for r in rid:
    #                 val = self.ontocols.find_val_of_rel_concept(c, r)
    #                 for v in val:
    #                     csyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
    #                     tempdict = {}
    #                     tempdict['name'] = csyn
    #                     tempdict['value'] = v
    #                     # if tempdict not in infolist:
    #                     infolist.append(tempdict)
    #                 # print(infolist)
    #                 #
    #     if cid1 and rid and rid == '?':
    #         for c in cid1:
    #             rel = list(self.ontocols.find_concept_data(c).keys())
    #             rel.remove('cid')
    #             rel.remove('_id')
    #             rel.remove('csyn')
    #             for r in rel:
    #                 tempdict = {}
    #                 val = self.ontocols.find_val_of_rel_concept(c, r)
    #                 for v in val:
    #                     csyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
    #                     tempdict['name'] = csyn
    #                     tempdict['value'] = v
    #                     # if tempdict not in infolist:
    #                     infolist.append(tempdict)
    #                 # print(infolist)
    #     return
    def find_info_of_csyn_id(self, cid1, rid):  # 这部分内容是用来返回输入空格后的信息
        infolist = []
        templist = []
        if cid1 and not rid:  # 如果rid为空，则返回该cid的关系的csyn
            infolist = []
            for c in cid1:
                infodict = {}
                tempd = {}
                templist = []
                concsyn = self.ontocols.find_val_of_rel_concept(c, 'csyn')[0]
                tempd['name'] = concsyn
                tempd['value'] = c
                infodict['first'] = tempd
                rel = list(self.ontocols.find_concept_data(c).keys())  # 把cid对应的所有关系都列出来
                rel.remove('cid')  # 去掉三个关系
                rel.remove('_id')
                rel.remove('csyn')
                for r in rel:  # rel中是所需关系

                    tempdict = {}
                    csyn = self.ontocols.find_val_of_rel_relation(r, 'csyn')[0]  # 得到关系的
                    tempdict['name'] = csyn
                    tempdict['value'] = r  # 返回
                    templist.append(tempdict)
                if self.find_method_in_relation():
                    templist = templist + self.find_method_in_relation()
                infodict['second'] = templist

                if infodict not in infolist:
                    infolist.append(infodict)


                    # print(infolist)

        if cid1 and rid and rid != '?':  # [a][b]
            infolist = []
            for c in cid1:
                infodict = {}
                tempd = {}
                concsyn = self.ontocols.find_val_of_rel_concept(c, 'csyn')[0]
                tempd['name'] = concsyn
                tempd['value'] = c
                infodict['first'] = tempd
                templist = []
                for r in rid:
                    val = self.ontocols.find_val_of_rel_concept(c, r)
                    for v in val:
                        tempdict = {}
                        csyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
                        tempdict['name'] = csyn
                        tempdict['value'] = v
                        # if tempdict not in infolist:
                        templist.append(tempdict)
                        infodict['second'] = templist
                if infodict not in infolist:
                    infolist.append(infodict)
                    # print(infolist)
                    #
        if cid1 and rid and rid[0] == '?':  # [a][?]
            infolist = []
            for c in cid1:
                infodict = {}
                tempd = {}
                concsyn = self.ontocols.find_val_of_rel_concept(c, 'csyn')
                tempd['name'] = concsyn
                tempd['value'] = c
                infodict['first'] = tempd
                rel = list(self.ontocols.find_concept_data(c).keys())
                rel.remove('cid')
                rel.remove('_id')
                rel.remove('csyn')
                for r in rel:

                    val = self.ontocols.find_val_of_rel_concept(c, r)
                    for v in val:
                        tempdict = {}
                        csyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
                        tempdict['name'] = csyn
                        tempdict['value'] = v
                        templist.append(tempdict)
                        # if tempdict not in infolist:

                infodict['second'] = templist
                infolist.append(infodict)
                # print(infolist)
        return infolist

    def result_info_of_method_for_webfront(self, frontlist):
        # [['i306', 'i334', 'i254', 'i312'], ['r39','r41'], ['i7', 'i14'], ['m3','m1']]
        infolist = []
        mlist = []
        corrlist = []  # 第一和第三的对应关系，格式为：[[[{'name','value},{'name','value'}]...],[[{'name','value},{'name','value'}]...]]
        templistc = []
        templistr = []
        if len(frontlist) >= 4:
            for m in frontlist[-1]:
                if 'm' == m[0]:
                    mlist.append(m)
        if mlist:
            for r in frontlist[-3]:
                for c in frontlist[-4]:
                    tempd = {}
                    templ = []
                    ccsyn = self.ontocols.find_val_of_rel_concept(c, 'csyn')[0]
                    tempd['name'] = ccsyn
                    tempd['value'] = c
                    templ.append(tempd)
                    tempd = {}
                    vid = self.ontocols.find_val_of_rel_concept(c, r)
                    for v in vid:
                        ccsyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
                        tempd['name'] = ccsyn
                        tempd['value'] = v
                    templ.append(tempd)
                    templistc.append(templ)

                templistr.append(templistc)
                templistc = []


                #             print(templistr[1])
        for m in mlist:
            if m == 'm3':
                infolist = self.scoredist_for_helplist(templistr[0])  # 这里只给出一类成绩的成绩分布
                # print('infolist is ',infolist)
            if m == 'm1':
                infolist = self.max_value_for_helplist(templistr[0])  # 这里只给出一类成绩的最大值最小值。
            if m == 'm5':
                infolist = self.min_value_for_helplist(templistr[0])  # 这里只给出一类成绩的最大值最小值。
            if m == 'm7':
                infolist = self.average_value_for_helplist(templistr[0])

        return infolist

    def scoredist_for_helplist(self, helplist):
        # 这里的frontlist是[[{'name': '李健康', 'value': 'i306'}, {'name': 19, 'value': 'i7'}]]

        infolist = []

        templist = []

        templist5 = []
        templist6 = []
        templist7 = []
        templist8 = []
        templist9 = []
        num5 = 0
        num6 = 0
        num7 = 0
        num8 = 0
        num9 = 0
        for i in helplist:
            st = i[0]
            # print(st)
            s = i[1]['name']
            if s < 60:
                num5 = num5 + 1
                templist5.append(st)
            elif s >= 60 and s < 70:
                num6 = num6 + 1
                templist6.append(st)
            elif s >= 70 and s < 80:
                num7 = num7 + 1
                templist7.append(st)
            elif s >= 80 and s < 90:
                num8 = num8 + 1
                templist8.append(st)
            elif s >= 90 and s < 100:
                num9 = num9 + 1
                templist9.append(st)
        tempdict = {}
        tempdict['name'] = '<60'
        tempdict['value'] = num5
        infolist.append(tempdict)
        tempdict = {}
        tempdict['name'] = '>=60 <70'
        tempdict['value'] = num6
        infolist.append(tempdict)
        tempdict = {}
        tempdict['name'] = '>=70 <80'
        tempdict['value'] = num7
        infolist.append(tempdict)
        tempdict = {}
        tempdict['name'] = '>=80 <790'
        tempdict['value'] = num8
        infolist.append(tempdict)
        tempdict = {}
        tempdict['name'] = '>=90'
        tempdict['value'] = num9
        infolist.append(tempdict)
        # print(infolist)

        return infolist

    def max_value_for_helplist(self, helplist):
        numlist = []
        tempdict = {}
        maxid = []
        maxtemp = 0
        minid = []
        mintemp = 0
        max = 0
        min = helplist[0][1]['name']
        for i in helplist:
            st = i[0]
            s = i[1]['name']
            sid = i[1]['value']
            tempdict = {}
            if max <= s:
                if max == s:
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    maxid.append(tempdict)
                else:
                    max = s
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    maxid = []
                    maxid.append(tempdict)

            if min >= s:
                if min == s:
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    minid.append(tempdict)
                else:
                    min = s
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    minid = []
                    minid.append(tempdict)

        return maxid

    def min_value_for_helplist(self, helplist):
        numlist = []
        tempdict = {}
        maxid = []
        maxtemp = 0
        minid = []
        mintemp = 0
        max = 0
        min = helplist[0][1]['name']
        for i in helplist:
            st = i[0]
            s = i[1]['name']
            sid = i[1]['value']
            tempdict = {}
            if max <= s:
                if max == s:
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    maxid.append(tempdict)
                else:
                    max = s
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    maxid = []
                    maxid.append(tempdict)

            if min >= s:
                if min == s:
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    minid.append(tempdict)
                else:
                    min = s
                    tempdict['value'] = s
                    tempdict['name'] = st['name']
                    minid = []
                    minid.append(tempdict)

        return minid

    def average_value_for_helplist(self, helplist):
        numlist = []
        tempdict = {}
        maxid = []
        maxtemp = 0
        minid = []
        mintemp = 0
        max = 0
        sum = 0
        min = helplist[0][1]['name']
        for i in helplist:
            st = i[0]
            s = i[1]['name']
            sid = i[1]['value']
            tempdict = {}
            sum = sum + s
        tempdict['name'] = '平均成绩'
        tempdict['value'] = sum / float(len(helplist))
        maxid.append(tempdict)

        return maxid

    def find_method_in_relation(self):
        methodlist = []
        tempdict = {}
        methods = self.ontocols.find_method_in_relation_term('m')
        if methods:
            for m in methods:
                tempdict = {}
                tempdict['name'] = m['csyn'][0]
                tempdict['value'] = m['rid'][0]
                methodlist.append(tempdict)
        return methodlist

    def get_all_info_of_search(self, cid1, rid, cid2):
        infolist = []
        infotemp = []
        if rid == '?':
            rid = []
        if cid2 == '?':
            cid2 = []
        if cid1:
            for c1 in cid1:
                tempdict = {}
                csyn = self.ontocols.find_val_of_rel_concept(c1, 'csyn')[0]
                tempdict['name'] = csyn
                tempdict['value'] = c1
                infotemp.append(tempdict)
                if not rid:  # 如果关系为空    [a][]
                    if not cid2:  # 如果关系值为空，则直接显示cid1的所有信息  [a][][]
                        rel = list(self.ontocols.find_concept_data(c1).keys())
                        rel.remove('cid')
                        rel.remove('_id')
                        rel.remove('csyn')
                        for r in rel:

                            val = self.ontocols.find_val_of_rel_concept(c1, r)
                            for v in val:
                                tempdict = {}
                                csyn = self.ontocols.find_val_of_rel_relation(r, 'csyn')[0]
                                tempdict['name'] = csyn
                                tempdict['value'] = r
                                infotemp.append(tempdict)
                                csyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
                                tempdict = {}
                                tempdict['name'] = csyn
                                tempdict['value'] = v
                                # if tempdict not in infolist:
                                infotemp.append(tempdict)
                    else:  # 如果cid2不为空，则显示它们之间的关系 [a][][c]
                        rel1 = list(self.ontocols.find_concept_data(c1).keys())
                        rel1.remove('cid')
                        rel1.remove('_id')
                        rel1.remove('csyn')
                        for c2 in cid2:
                            rel2 = list(self.ontocols.find_concept_data(c2).keys())
                            rel2.remove('cid')
                            rel2.remove('_id')
                            rel2.remove('csyn')
                            for r in rel2:
                                invr = self.get_reverse_id(r)

                                if invr in rel1:
                                    cysn = self.ontocols.find_val_of_rel_relation(invr, 'csyn')
                                    tempdict = {}
                                    tempdict['name'] = cysn
                                    tempdict['value'] = invr
                                    infotemp.append(tempdict)
                                    tempdict = {}
                                    csyn = self.ontocols.find_val_of_rel_concept(c2, 'csyn')[0]
                                    tempdict['name'] = csyn
                                    tempdict['value'] = c2
                                    infotemp.append(tempdict)
                                    #                                 else:
                                    #                                     infotemp=[]
                else:  # 如果关系不为空 [a][b]
                    if not cid2:  # 如果cid2,即关系值为空，则显示关系的关系值内容[a][b][]
                        for r in rid:

                            val = self.ontocols.find_val_of_rel_concept(c1, r)
                            for v in val:
                                tempdict = {}

                                csyn = self.ontocols.find_val_of_rel_relation(r, 'csyn')[0]
                                tempdict['name'] = csyn
                                tempdict['value'] = r
                                infotemp.append(tempdict)
                                csyn = self.ontocols.find_val_of_rel_concept(v, 'csyn')[0]
                                tempdict = {}
                                tempdict['name'] = csyn
                                tempdict['value'] = v
                                # if tempdict not in infolist:
                                infotemp.append(tempdict)

                    else:  # 如果cid2不为空，则给出是真还是假。
                        for r in rid:
                            val = self.ontocols.find_val_of_rel_concept(c1, r)
                            for c2 in cid2:
                                if c2 in val:
                                    tempdict = {}

                                    csyn = self.ontocols.find_val_of_rel_relation(r, 'csyn')[0]
                                    tempdict['name'] = csyn
                                    tempdict['value'] = r
                                    infotemp.append(tempdict)
                                    csyn = self.ontocols.find_val_of_rel_concept(c2, 'csyn')[0]
                                    tempdict = {}
                                    tempdict['name'] = csyn
                                    tempdict['value'] = c2
                                    # if tempdict not in infolist:
                                    infotemp.append(tempdict)
                                    res = 'true'

                                else:
                                    res = 'false'

                infolist.append(infotemp)
                # print(c1,infotemp)
                infotemp = []
        return infolist

    def format_for_web_front(self, typ):
        infolist = []
        if typ == '':
            print()
        if typ == '':
            print()
        if typ == '':
            print()
        if typ == '':
            print()

        return infolist

    def fuzzy_find_in_contermtable(self, keystr):  # 对数据库conterm表中的term进行模糊查询，有多个cid的term则返回多次
        infolist = []
        tempdict = {}
        rec = self.ontocols.fuzzy_find_concepts_term(keystr)  # 对数据库中的内容进行模糊查询
        if rec:

            for r in rec:

                for cid in r['cid']:
                    tempdict = {}
                    tempdict['name'] = r['term'][0]
                    tempdict['value'] = cid
                    infolist.append(tempdict)

        return infolist

    def fuzzy_find_in_reltermtable(self, keystr):  # 对数据库conterm表中的term进行模糊查询，有多个cid的term则返回多次
        infolist = []
        tempdict = {}
        rec = self.ontocols.fuzzy_find_relations_term(keystr)  # 对数据库中的内容进行模糊查询
        if rec:

            for r in rec:

                for cid in r['rid']:
                    tempdict = {}
                    tempdict['name'] = r['term'][0]
                    tempdict['value'] = cid
                    infolist.append(tempdict)

        return infolist

    def insert_method_term_data(self, termp, termn):  # 插入一个关系
        rids = []
        temp = self.ontocols.find_relation_term(termp)  # 查一下知识库中有没有该关系的术语
        if temp:  # 如果有，返回这个术语对应的id列表
            rids = temp[0]['rid']
        else:  # 如果没有，则进行下面的操作，
            globalinfo.metid = globalinfo.metid + 1  # 记录关系数

            rids.append('m' + str(globalinfo.metid))
            self.ontocols.insert_relation_term(termp)  # 增加一个关系术语
            self.ontocols.insert_relation_cid(termp, 'm' + str(globalinfo.metid))  # 在术语表中对应的术语，增加一个id

            globalinfo.metid = globalinfo.metid + 1  # 记录关系数，这里的关系是两个的，
            self.ontocols.colidrec.update_idres('metid', globalinfo.metid)
            self.ontocols.insert_relation_term(termn)  # 逆关系后面加了个逆字
            self.ontocols.insert_relation_cid(termn, 'm' + str(globalinfo.metid))
            self.insert_relation_data(rids[0], termp, termn)

        return rids

    def find_multi(self, ques):  # 用于多种情况的查询，+ #

        subq = ques.split('#')
        ids = []
        infos = self.find_concept(subq[0])
        ids.append(self.find_concept_term_id(subq[0]))
        for q in range(1, len(subq)):
            temp = self.find_relation_term_id(subq[q])
            ids.append(temp)
        valtemp = self.find_relval_of_concept(ids[0], ids[1])
        for vid in valtemp:
            valinfo = self.find_info_for_concept_id(vid)
            infos.append(valinfo)
        return infos

    def find_val_of_rel_concept(self, cid, rid):
        self.ontocols.find_val_of_rel_concept(cid, rid)

    def find_val_of_rel_relation(self, rid, relid):
        self.ontocols.find_val_of_rel_relation(rid, relid)

    def find_allrel_and_allval_of_entity(self, eid):
        rellist = self.ontocols.find_rels_vals_of_concept(eid)[0]
        vallist = self.ontocols.find_rels_vals_of_concept(eid)[1]
        return rellist, vallist

    def find_relval_of_concept(self, cids, rids):  # 查询概念的所有关系的关系值

        if cids:
            for d in cids:
                tempinfo = self.ontocols.find_concept_data(d)
                if tempinfo:
                    temp = tempinfo.keys()
                    s = list(set(temp).intersection(set(rids)))
        return tempinfo[s[0]]

    def find_concept_term_id(self, term):  # 查找术语所对应用id,输入为术语
        temp = self.ontocols.find_concept_term(term)
        if temp:
            return temp[0]['cid']
        else:
            return []

    def find_relation_term_id(self, term):  # 查找关系术语所对应用id,输入为术语
        temp = self.ontocols.find_relation_term(term)
        if temp:
            return temp[0]['rid']
        else:
            return []

    def find_concept(self, term):  # 查找概念或实例，输入为术语
        infos = []
        ids = self.find_concept_term_id(term)
        for i in ids:
            infos.append(self.find_info_for_concept_id(i))
        return infos

    def find_concept_for_echarts(self, term):  # 查找概念或实例，输入为术语
        infos = []
        ids = self.find_concept_term_id(term)
        for i in ids:
            infos.append(self.info_for_echart2_force(i))
        return infos

    def get_info_of_relatt_of_conins(self, coninsterm, relattterm):
        idlist = []
        result = {}
        idc = self.find_concept_term_id(coninsterm)
        for i in idc:
            keys = self.ontocols.find_concept_data(i).keys()
            for k in keys:
                if k[1:].isdigit():
                    kcsyn = self.ontocols.find_val_of_rel_relation(k, 'csyn')
                    for c in kcsyn:
                        if relattterm in c:
                            idlist.append(k)

            for idl in idlist:
                val = self.ontocols.find_val_of_rel_concept(i, idl)
                ridcsyn = self.ontocols.find_val_of_rel_relation(idl, 'csyn')[0]
                valcsyn = []
                for v in val:
                    valcsyn.append(self.ontocols.find_val_of_rel_concept(v, 'csyn')[0])
                    result[ridcsyn] = valcsyn
        return result

    def node_format(self, cate, name, label):  # 用于打包成前端需要数据包，该包是按照echarts2 force的格式。
        node = {}
        node['category'] = cate
        node['name'] = name
        node['label'] = label
        node['value'] = 20
        return node

    def link_format(self, sour, targ, name):  # 用于打包成前端需要数据包，该包是按照echarts2 force的格式。
        link = {}
        link['source'] = sour
        link['target'] = targ
        link['name'] = name
        return link

    def judge_conid_or_inid(self, findid):
        if findid[0] == 'c' or findid[1] == '0':
            return 2
        elif findid[0] == 'i' or findid[1] == '1':
            return 3

    def info_for_echart2_force(self, findid):  # 这里的信息输出是用于echarts2中的force所需要的数据
        returninfo = {}
        nodesinfo = {}
        linksinfo = {}
        nodesinfolist = []
        linksinfolist = []
        info = self.ontocols.find_concept_data(findid)  # 找到该id所在的记录
        if info:  # 如果有记录，则执行下面的操作
            nodesinfo = self.node_format(0, findid, info['csyn'][0])
            nodesinfolist.append(nodesinfo)
            info.pop('_id')  # 去掉mongod自己带的_id
            info.pop('cid')
            # info.pop('gloss')
            # info.pop('esyn')
            for k in info.keys():  # 对每个info中的关系进行遍历
                temp = self.ontocols.find_relation_data(k)  # 找关系的id号
                if temp:  # 如果有这个关系
                    tkey = temp['csyn']  # 那么，将这个id对应的术语名放到tkey里面
                else:
                    tkey = [k]  # 如果没有，则将k值放到里面

                vals = info[k]  # 取关系所对应的值，即具体的节点
                for v in vals:  # 遍历该值，目的是取其中术语名称。
                    nodesinfo = {}
                    linksinfo = {}
                    vtemp = self.ontocols.find_concept_data(v)  # 查询一下是否有该值的记录
                    if vtemp:
                        nodesinfo = self.node_format(self.judge_conid_or_inid(v), v,
                                                     vtemp['csyn'][0])  # 这里的0指的是同义词表中的第1个元素，以后可以写成变量的形式
                        nodesinfolist.append(nodesinfo)
                        linksinfo = self.link_format(findid, v, tkey[0])  # 取关系同义词中的第1个元素
                        linksinfolist.append(linksinfo)
                    else:
                        nodesinfo = self.node_format(3, v, v)  # 这里的0指的是同义词表中的第1个元素，以后可以写成变量的形式
                        nodesinfolist.append(nodesinfo)
                        linksinfo = self.link_format(findid, v, tkey[0])  # 取关系同义词中的第1个元素
                        linksinfolist.append(linksinfo)

        returninfo['nodes'] = nodesinfolist
        returninfo['links'] = linksinfolist
        return returninfo

    def find_info_for_concept_id(self, findid):  # 查找cid所对应的信息
        returninfo = {}
        terminfo = {}
        corinfo = {}
        info = self.ontocols.find_concept_data(findid)  # 找到该id所在的记录
        if info:  # 如果有记录，则执行下面的操作
            info.pop('_id')  # 去掉mongod自己带的_id
            corinfo[info['csyn'][0]] = findid  # 记录下术语和id的对应关系
            # info.pop('cid')
            # info.pop('csyn')
            for k in info.keys():  # 对每个info中的关系进行遍历
                temp = self.ontocols.find_relation_data(k)  # 找关系的id号
                if temp:  # 如果有这个关系
                    tkey = temp['csyn']  # 那么，将这个id对应的术语名放到tkey里面
                else:
                    tkey = [k]  # 如果没有，则将k值放到里面
                vals = info[k]  # 取关系所对应的值，即具体的节点
                tval = []
                for v in vals:  # 遍历该值，目的是取其中术语名称。
                    vtemp = self.ontocols.find_concept_data(v)  # 查询一下是否有该值的记录
                    if vtemp:
                        tval.append(vtemp['csyn'][0])  # 增加到列表中，其中的0，表示取同义词列列表中的第一个值
                        corinfo[vtemp['csyn'][0]] = v  # 得到术语及其与id的对应关系写到cor当局者迷
                    else:
                        tval.append(v)

                terminfo[tkey[0]] = tval  # 得到term的信息
        returninfo['term'] = terminfo
        returninfo['cor'] = corinfo
        return returninfo

    # 9月5日改
    # ===========================================================================
    #
    # ===========================================================================
    def insert_instance_term_in_kn(self, term):
        cids = []
        globalinfo.insid = globalinfo.insid + 1  # 生成id号，即自动加1，这个是用来记录库中有多少个概念。
        cids.append('i' + str(globalinfo.insid))  # 对于概念来说前面加一个字母‘c’来表示
        self.ontocols.colidrec.update_idres('insid', globalinfo.insid)  # 在表idrec里面记录当前的概念数

        self.ontocols.insert_concept_cid(term, cids[0])  # 在术语表中为该术语增加一个对应的id号
        self.insert_concept_data(cids[0], term)  # 在数据表中增加一个记录，并且增加一个csyn
        return cids

    def insert_instance_term_data(self, term):  # 插入一个概念，这个可以用于前台的一个概念的插入请求。
        cids = []
        temp = self.ontocols.find_concept_term(term)  # 查找是否有相同的概念术语
        if temp:
            cids = temp[0]['cid']  # 如果有相同的术语，则返回目前该术语所对应的语义
            print('exist a concept with same term', term)
        else:  # 如果库中没有这个术语，那么执行下面的操作
            globalinfo.insid = globalinfo.insid + 1  # 生成id号，即自动加1，这个是用来记录库中有多少个概念。
            cids.append('i' + str(globalinfo.insid))  # 对于概念来说前面加一个字母‘c’来表示
            self.ontocols.colidrec.update_idres('insid', globalinfo.insid)  # 在表idrec里面记录当前的概念数
            self.ontocols.insert_concept_term(term)  # 在术语表中增加一个术语
            self.ontocols.insert_concept_cid(term, cids[0])  # 在术语表中为该术语增加一个对应的id号
            self.insert_concept_data(cids[0], term)  # 在数据表中增加一个记录，并且增加一个csyn
        return cids  # 返回插入概念术语的id号

    def insert_concept_term_in_kn(self, term):
        cids = []
        globalinfo.conid = globalinfo.conid + 1  # 生成id号，即自动加1，这个是用来记录库中有多少个概念。
        cids.append('c' + str(globalinfo.conid))  # 对于概念来说前面加一个字母‘c’来表示
        self.ontocols.colidrec.update_idres('conid', globalinfo.conid)  # 在表idrec里面记录当前的概念数

        self.ontocols.insert_concept_cid(term, cids[0])  # 在术语表中为该术语增加一个对应的id号
        self.insert_concept_data(cids[0], term)  # 在数据表中增加一个记录，并且增加一个csyn
        return cids

    def insert_concept_term_data(self, term):  # 插入一个概念，这个可以用于前台的一个概念的插入请求。
        cids = []
        temp = self.ontocols.find_concept_term(term)  # 查找是否有相同的概念术语
        if temp:
            cids = temp[0]['cid']  # 如果有相同的术语，则返回目前该术语所对应的id
            print('exist a concept with same term')
        else:  # 如果库中没有这个术语，那么执行下面的操作
            globalinfo.conid = globalinfo.conid + 1  # 生成id号，即自动加1，这个是用来记录库中有多少个概念。
            cids.append('c' + str(globalinfo.conid))  # 对于概念来说前面加一个字母‘c’来表示
            self.ontocols.colidrec.update_idres('conid', globalinfo.conid)  # 在表idrec里面记录当前的概念数
            self.ontocols.insert_concept_term(term)  # 在术语表中增加一个术语
            self.ontocols.insert_concept_cid(term, cids[0])  # 在术语表中为该术语增加一个对应的id号
            self.insert_concept_data(cids[0], term)  # 在数据表中增加一个记录，并且增加一个csyn
        return cids  # 返回插入概念术语的id号

    def delete_concept_term_data(self, term,
                                 cid):  # 删除一个概念，其实是删一个具有一个id号的术语，在术语表中，删掉该id号对应的术语（该术语只有一个id号），数据表中删掉该id号，还有对应的关系。
        info = self.ontocols.find_concept_data(cid)  # 找到cid所对应的记录，即是一个记录所对应的键值对信息
        for csyn in info['csyn']:
            self.ontocols.delete_concept_cid(csyn, cid)  # 在术语表中删除对应的术语及id，如果术语中还对应其它id，则保留该术语，否则将整个术语记录删掉。
        if info:  # 如果信息不为空，则执行下面的操作
            info.pop('_id')
            for k in info.keys():
                if k[1:].isdigit():  # 这里的目的是检查一下是否符合生成的id，以便于去掉不是自动生成id号的关系，如csyn,gloss等
                    invers = self.get_reverse_id(k)  # 得到关系的逆关系的
                    for v in info[k]:  # 获取关系所对应的值
                        self.ontocols.delete_val_rel_of_concept(v, invers, cid)  # 在所对应的值端删除该节点的信息。
        self.ontocols.delete_concept_data(cid)  # 在数据表中

    def update_concept_instance_term_data(self, term, newterm, cid):  # 更新术语名，注意，有可能会出现库中已有该术语，因此要先找一下有没有
        info = self.ontocols.find_concept_term(newterm)  # 查询一下库中是否有相同的术语
        if info:  # 如果有该术语，执行插入存大的术语当中，即找到这个术语名，把cid插入到cid表，并把原来的术语对应的号删除
            self.ontocols.insert_concept_cid(newterm, cid)
            self.ontocols.delete_concept_cid(term, cid)
        else:  # 如果没有该术语，则重新建立
            self.ontocols.insert_concept_term(newterm)  # 在术语表中，增加一个新的术语名
            self.ontocols.insert_concept_cid(newterm, cid)  # 在术语表中的对应的术语增加一个id号
            self.ontocols.delete_concept_cid(term, cid)  # 删除原来的术语表中的id号。
        self.ontocols.update_val_of_rel_concept(cid, 'csyn', term, newterm)  # 在数据表中修改csyn

    # 9月5日改

    def insert_concept_data(self, cid, term):  # 与实例共用
        self.ontocols.insert_concept_data(cid)
        self.ontocols.insert_val_of_rel_concept(cid, 'csyn', term)

    def insert_solorel_of_concept_data(self, cid, rel, val):  # 这里的rel参数，可以是关系名，也可是关系的id
        self.ontocols.insert_val_of_rel_concept(cid, rel, val)

    def get_reverse_id(self, rid):
        headid = rid[0]
        temp = int(rid[1:])
        if temp % 2:
            tempid = headid + str(temp + 1)
        else:
            tempid = headid + str(temp - 1)
        return tempid

    def insert_binrel_of_concept_data(self, cid, rid, valid):
        self.ontocols.insert_val_of_rel_concept(cid, rid, valid)
        revrid = self.get_reverse_id(rid)
        self.ontocols.insert_val_of_rel_concept(valid, revrid, cid)

    def update_solorel_of_concept_data(self, cid, rel, oldval, newval):
        self.ontocols.update_val_of_rel_concept(cid, rel, oldval, newval)

    def update_binrel_of_concept_data(self, cid, relid, oldvalid, newvalid):
        self.ontocols.update_val_of_rel_concept(cid, relid, oldvalid, newvalid)
        revrelid = self.get_reverse_id(relid)
        self.ontocols.delete_val_rel_of_concept(oldvalid, revrelid, cid)
        self.ontocols.insert_val_of_rel_concept(newvalid, revrelid, cid)

    def insert_concept_tri(self, term, relterm, valterm):  # 插入概念三元组
        cid = self.insert_concept_term_data(term)[0]
        rid = self.insert_relation_term_data(relterm)[0]
        valid = self.insert_concept_term_data(valterm)[0]
        self.insert_binrel_of_concept_data(cid, rid, valid)

    def insert_instance_tri(self, term, relterm, valterm):  # insert instance 三元组
        cid = self.insert_instance_term_data(term)[0]
        rid = self.insert_relation_term_data(relterm)[0]
        valid = self.insert_instance_term_data(valterm)[0]
        self.insert_binrel_of_concept_data(cid, rid, valid)

    def insert_relation_term_data(self, termp, termn):  # 插入一个关系
        rids = []
        temp = self.ontocols.find_relation_term(termp)  # 查一下知识库中有没有该关系的术语
        if temp:  # 如果有，返回这个术语对应的id列表
            rids = temp[0]['rid']
        else:  # 如果没有，则进行下面的操作，
            globalinfo.resid = globalinfo.resid + 1  # 记录关系数

            rids.append('r' + str(globalinfo.resid))
            self.ontocols.insert_relation_term(termp)  # 增加一个关系术语
            self.ontocols.insert_relation_cid(termp, 'r' + str(globalinfo.resid))  # 在术语表中对应的术语，增加一个id

            globalinfo.resid = globalinfo.resid + 1  # 记录关系数，这里的关系是两个的，
            self.ontocols.colidrec.update_idres('resid', globalinfo.resid)
            self.ontocols.insert_relation_term(termn)  # 逆关系后面加了个逆字
            self.ontocols.insert_relation_cid(termn, 'r' + str(globalinfo.resid))
            self.insert_relation_data(rids[0], termp, termn)

        return rids

    def delete_relation_term_data(self, term,
                                  cid):  # 删除一个关系，其实是删一个具有一个id号的术语，在术语表中，删掉该id号对应的术语（该术语只有一个id号），数据表中删掉该id号，还有对应的关系。
        info = self.ontocols.find_relation_data(cid)  # 找到cid所对应的记录，即是一个记录所对应的键值对信息
        for csyn in info['csyn']:
            self.ontocols.delete_relation_cid(csyn, cid)  # 在术语表中删除对应的术语及id，如果术语中还对应其它id，则保留该术语，否则将整个术语记录删掉。
        if info:  # 如果信息不为空，则执行下面的操作
            info.pop('_id')
            for k in info.keys():
                if k[1:].isdigit():  # 这里的目的是检查一下是否符合生成的id，以便于去掉不是自动生成id号的关系，如csyn,gloss等
                    invers = self.get_reverse_id(k)  # 得到关系的逆关系的
                    for v in info[k]:  # 获取关系所对应的值
                        self.ontocols.delete_val_rel_of_concept(v, invers, cid)  # 在所对应的值端删除该节点的信息。
        self.ontocols.delete_relation_data(cid)  # 在数据表中

        invid = self.get_reverse_id(cid)
        info = self.ontocols.find_relation_data(invid)  # 找到cid所对应的记录，即是一个记录所对应的键值对信息
        for csyn in info['csyn']:
            self.ontocols.delete_relation_cid(csyn, invid)
        self.ontocols.delete_relation_data(invid)

    def update_relation_attribute_term_data(self, term, newterm, cid):  # 更新术语名，注意，有可能会出现库中已有该术语，因此要先找一下有没有
        info = self.ontocols.find_relation_term(newterm)  # 查询一下库中是否有相同的术语
        if info:  # 如果有该术语，执行插入存大的术语当中，即找到这个术语名，把cid插入到cid表，并把原来的术语对应的号删除
            self.ontocols.insert_relation_cid(newterm, cid)
            self.ontocols.delete_relation_cid(term, cid)
        else:  # 如果没有该术语，则重新建立
            self.ontocols.insert_relation_term(newterm)  # 在术语表中，增加一个新的术语名
            self.ontocols.insert_relation_cid(newterm, cid)  # 在术语表中的对应的术语增加一个id号
            self.ontocols.delete_relation_cid(term, cid)  # 删除原来的术语表中的id号。
        self.ontocols.update_val_of_rel_relation(cid, 'csyn', term, newterm)  # 在数据表中修改csyn

    def insert_relation_data(self, rid, termp, termn):
        self.ontocols.insert_relation_data(rid)
        self.ontocols.insert_val_of_rel_relation(rid, 'csyn', termp)
        invrid = self.get_reverse_id(rid)
        self.ontocols.insert_relation_data(invrid)
        self.ontocols.insert_val_of_rel_relation(invrid, 'csyn', termn)

    def insert_attribute_term_data(self, termp, termn):  # 插入一个属性
        rids = []
        temp = self.ontocols.find_relation_term(termp)  # 查一下知识库中有没有该属性的术语
        if temp:  # 如果有，返回这个术语对应的id列表
            rids = temp[0]['rid']
        else:  # 如果没有，则进行下面的操作，
            globalinfo.attid = globalinfo.attid + 1  # 记录属性数

            rids.append('a' + str(globalinfo.attid))
            self.ontocols.insert_relation_term(termp + termn)  # 增加一个属性术语
            self.ontocols.insert_relation_cid(termp + termn, 'a' + str(globalinfo.attid))  # 在术语表中对应的术语，增加一个id

            globalinfo.attid = globalinfo.attid + 1  # 记录属性数，这里的属性是两个的，
            self.ontocols.colidrec.update_idres('attid', globalinfo.attid)
            self.ontocols.insert_relation_term(termn + termp)  # 逆关系后面加了个逆字
            self.ontocols.insert_relation_cid(termn + termp, 'a' + str(globalinfo.attid))
            self.insert_relation_data(rids[0], termp + termn, termn + termp)

        return rids

    def delete_attribute_term_data(self, term,
                                   cid):  # 删除一个关系，其实是删一个具有一个id号的术语，在术语表中，删掉该id号对应的术语（该术语只有一个id号），数据表中删掉该id号，还有对应的关系。
        info = self.ontocols.find_relation_data(cid)  # 找到cid所对应的记录，即是一个记录所对应的键值对信息
        for csyn in info['csyn']:
            self.ontocols.delete_relation_cid(csyn, cid)  # 在术语表中删除对应的术语及id，如果术语中还对应其它id，则保留该术语，否则将整个术语记录删掉。
        if info:  # 如果信息不为空，则执行下面的操作
            info.pop('_id')
            for k in info.keys():
                if k[1:].isdigit():  # 这里的目的是检查一下是否符合生成的id，以便于去掉不是自动生成id号的关系，如csyn,gloss等
                    invers = self.get_reverse_id()  # 得到关系的逆关系的
                    for v in info[k]:  # 获取关系所对应的值
                        self.ontocols.delete_val_rel_of_concept(v, invers, cid)  # 在所对应的值端删除该节点的信息。
        self.ontocols.delete_relation_data(cid)  # 在数据表中

        invid = self.get_reverse_id(cid)
        info = self.ontocols.find_relation_data(invid)  # 找到cid所对应的记录，即是一个记录所对应的键值对信息
        for csyn in info['csyn']:
            self.ontocols.delete_relation_cid(csyn, invid)
        self.ontocols.delete_relation_data(invid)

    def update_attribute_term_data(self, term, newterm, cid):  # 更新术语名，注意，有可能会出现库中已有该术语，因此要先找一下有没有
        info = self.ontocols.find_relation_term(newterm)  # 查询一下库中是否有相同的术语
        if info:  # 如果有该术语，执行插入存大的术语当中，即找到这个术语名，把cid插入到cid表，并把原来的术语对应的号删除
            self.ontocols.insert_relation_cid(newterm, cid)
            self.ontocols.delete_relation_cid(term, cid)
        else:  # 如果没有该术语，则重新建立
            self.ontocols.insert_relation_term(newterm)  # 在术语表中，增加一个新的术语名
            self.ontocols.insert_relation_cid(newterm, cid)  # 在术语表中的对应的术语增加一个id号
            self.ontocols.delete_relation_cid(term, cid)  # 删除原来的术语表中的id号。
        self.ontocols.update_val_of_rel_relation(cid, 'csyn', term, newterm)  # 在数据表中修改csyn

    def insert_attribute_term(self, term):
        rids = []
        temp = self.ontocols.find_relation_term(term)
        if temp:
            rids = temp[0]['rid']
        else:
            globalinfo.attid = globalinfo.attid + 1
            rids.append('a' + str(globalinfo.attid))
            self.ontocols.colidrec.update_idres('attid', globalinfo.attid)
            self.ontocols.insert_relation_term(term)
            self.ontocols.insert_relation_cid(term, 'a' + str(globalinfo.attid))
            globalinfo.attid = globalinfo.attid + 1
            self.ontocols.colidrec.update_idres('attid', globalinfo.attid)
            self.ontocols.insert_relation_term(term + '逆')
            self.ontocols.insert_relation_cid(term + '逆', 'a' + str(globalinfo.attid))
        return rids

    def insert_concept_sta(self, term, idtype, flag):  # 插入一个概念
        num = 0;
        if flag is True:  # 如果flag为真，则为新的术语
            num = num + 1
            findid = self.ontocols.get_id(idtype)
            self.ontocols.insert_concept_term(term)
            self.ontocols.insert_concept_cid(term, findid)
            self.ontocols.insert_concept_data(findid)
            self.ontocols.insert_val_of_rel_concept(findid, 'csyn', term)
        # else:#如果flag为假，则说明这个术语有新的
        #	findid=self.ontocols.find_concept_term(term)
        # self.ontocols.insert_concept_cid(term, findid)
        # self.ontocols.insert_val_of_rel_concept(findid, 'csyn',term)
        return findid

    def insert_relation_sta(self, term, idtype, flag):  # 插入一个概念

        if flag is True:  # 如果flag为真，则为新的术语
            findid = self.ontocols.get_id(idtype)
            self.ontocols.insert_relation_term(term)
            self.ontocols.insert_relation_cid(term, findid)
            self.ontocols.insert_relation_data(findid)
            self.ontocols.insert_val_of_rel_relation(findid, 'csyn', term)

            inverid = self.get_inverse_rid(findid)
            inverterm = term + '逆'
            self.ontocols.insert_relation_term(inverterm)
            self.ontocols.insert_relation_cid(inverterm, inverid)
            self.ontocols.insert_relation_data(inverid)
            self.ontocols.insert_val_of_rel_relation(inverid, 'csyn', inverterm)

        else:  # 如果flag为假，则说明这个术语有新的
            findid = self.ontocols.find_relation_term(term)
            inverid = self.get_inverse_rid(findid)
        # self.ontocols.insert_concept_cid(term, findid)
        # self.ontocols.insert_val_of_rel_concept(findid, 'csyn',term)
        return findid, inverid

    def insert_relation_sta_(self, term, idtype, flag):  # 插入一个概念

        if flag is True:  # 如果flag为真，则为新的术语
            findid = self.ontocols.get_id(idtype)
            self.ontocols.insert_relation_term(term)
            self.ontocols.insert_relation_cid(term, findid)
            self.ontocols.insert_relation_data(findid)
            self.ontocols.insert_val_of_rel_relation(findid, 'csyn', term)

            inverid = self.get_inverse_rid(findid)
            inverterm = term + '逆'
            self.ontocols.insert_relation_term(inverterm)
            self.ontocols.insert_relation_cid(inverterm, inverid)
            self.ontocols.insert_relation_data(inverid)
            self.ontocols.insert_val_of_rel_relation(inverid, 'csyn', inverterm)

        else:  # 如果flag为假，则说明这个术语有新的
            findid = self.ontocols.find_relation_term(term)
            inverid = self.get_inverse_rid(findid)
        # self.ontocols.insert_concept_cid(term, findid)
        # self.ontocols.insert_val_of_rel_concept(findid, 'csyn',term)
        return findid, inverid

    def get_inverse_rid(self, rid):
        if (int(rid) % 2):
            d = str(int(rid) + 1)
        else:
            d = str(int(rid) - 1)
        return d

    def check_pro_of_rel(self, findid, pro):
        if pro in self.ontocols.find_relation_data(findid)['pro']:
            return True
        else:
            return False

    def get_rels_with_pro_of_concept(self, pro, findid):
        r = set()
        for rels in self.ontocols.find_concept_data(findid).keys():
            if pro in self.ontocols.find_relation_data(rels)['pro']:
                r.add(rels)
        return r

    def add_rel_between_concepts(self, id1, id2, relid):
        self.ontocols.insert_rel_of_concept(id1, relid, id2)
        rel = self.ontocols.get_invers_relid(relid)
        self.ontocols.insert_rel_of_concept(id2, rel, id1)

    def insert_subcon_of_concept(self, fatherid, insertid):
        self.ontocols.insert_concept_data(insertid)
        self.add_rel_between_concepts(fatherid, insertid, self.superclass_of)
        rels = self.get_rels_with_pro_of_concept('inh', fatherid)
        self.ontocols.insert_rels_of_concept(insertid, rels)


class OntoHigh:
    ontomid = 0

    def __init__(self, ontodb):
        self.ontomid = OntoMid(ontodb)

    def get_id_of_concept(self, conterm):
        cid = self.ontomid.find_concept_term_id(conterm)
        return cid

    def add_concept(self, conterm):  # 增加一个概念，只是增加概念，即在conterm表里面增加术语，在condata里面增加id号
        cid = self.ontomid.insert_concept_term_data(conterm)
        return cid

    def add_concept_in_kn(self, conterm):
        cid = self.ontomid.insert_concept_term_in_kn(conterm)
        return cid

    def add_instance(self, insterm):  # 增加一个实例，只是增加实例，即在conterm表里面增加术语，在condata里面增加id号
        iid = self.ontomid.insert_instance_term_data(insterm)
        return iid

    def add_instance_in_kn(self, insterm):
        iid = self.ontomid.insert_instance_term_in_kn(insterm)
        return iid

    def add_concept_batch(self, termlist):  # 批量增加概念
        for t in termlist:
            self.ontomid.insert_concept_term_data(t)

    def add_instance_batch(self, termlist):  # 批量增加实例
        for t in termlist:
            self.ontomid.insert_instance_term_data(t)

    def add_isa_between_concepts(self, conterm1, conterm2):  # 为两个概念建立上下位关系
        cid1 = self.ontomid.find_concept_term_id(conterm1)[0]
        cid2 = self.ontomid.find_concept_term_id(conterm2)[0]
        rid = self.ontomid.find_relation_term_id('is_a')[0]
        self.ontomid.insert_binrel_of_concept_data(cid1, rid, cid2)

    def add_hasinstance_between_concept_instance(self, conterm, insterm):  # 为概念增加一个实例
        cid = self.ontomid.find_concept_term_id(conterm)[0]
        iid = self.ontomid.find_concept_term_id(insterm)[0]
        rid = self.ontomid.find_relation_term_id('has_instance')[0]
        self.ontomid.insert_binrel_of_concept_data(cid, rid, iid)

    def add_hasinstance_between_concept_instance_batch(self, conterm, instermlist):  # 为一个概念批量增加实例
        cid = self.ontomid.find_concept_term_id(conterm)[0]
        rid = self.ontomid.find_relation_term_id('has_instance')[0]
        for ins in instermlist:
            iid = self.ontomid.find_concept_term_id(ins)[0]
            self.ontomid.insert_binrel_of_concept_data(cid, rid, iid)

    def generate_concept_from_instance(self, conoflist,
                                       attributeval):  # 根据一组实例中共同的属性，自动生成一个概念，然后将该组实例的父节点做为新生成的概念的父节点，这组实例作为该概念的实例。
        cid = self.ontomid.insert_concept_term_data(attributeval + '_' + conoflist)[0]
        concid = self.ontomid.find_concept_term_id(conoflist)
        rid = rid = self.ontomid.find_relation_term_id('is_a')[0]
        self.ontomid.insert_binrel_of_concept_data(cid, rid, concid)
        hasinsrid = self.ontomid.find_relation_term_id('has_instance')[0]
        inslist = self.ontomid.find_val_of_rel_concept(concid, hasinsrid)
        attvalid = self.ontomid.find_concept_term_id(attributeval)[0]
        for ins in inslist:
            vallist = self.ontomid.find_allrel_and_allval_of_entity(ins)[1]
            if attvalid in vallist:
                self.ontomid.insert_binrel_of_concept_data(ins, hasinsrid, cid)

    def add_attval_of_concept(self, conterm, attval):  # 为概念增加一个属性，是增加一个属性关系及属性值。
        cid = self.ontomid.find_concept_term_id(conterm)[0]
        aid = self.ontomid.find_concept_term_id(attval)[0]
        attid = self.ontomid.insert_attribute_term_data(conterm, attval)
        self.ontomid.insert_binrel_of_concept_data(cid, attid[0], aid)

    def add_rel_between_concepts(self):
        pass

        # def auto_classification_of_concept(self, conterm, classterm):  #
        #     cid = self.ontomid.find_concept_term_id(conterm)[0]
        #     claid = self.ontomid.find_concept_term_id(classterm)[0]
        #     insid = self.ontomid.find_val_of_rel_concept(claid, 'has_instance')
        #     for ins in insid:
        #         insterm = self.ontomid.find_val_of_rel_concept(ins, 'csyn')[0]
        #         newterm = insterm + '_' + conterm
        #         self.add_concept(newterm)
        #         self.add_isa_between_concepts(newterm, conterm)


class OntoReason:
    is_a = '2100000001'
    superclass_of = '2100000002'
    instace_of = '2100000003'
    has_instance = '2100000004'
    onto_null = '0000000000'
    onto_root = '1000000000'
    ontocols = 0
    ontomid = 0

    def __init__(self, ontodb):

        db = globalinfo.con[ontodb]
        colct = db['ConTerm']
        colcd = db['ConData']
        colrt = db['RelTerm']
        colrd = db['RelData']
        colid = db['idPool']
        colidrec = db['idrec']
        self.ontocols = OntoLow(colct, colcd, colrt, colrd, colid, colidrec)
        self.ontomid = OntoMid(ontodb)

    def direct_relation(self,id1,id2): #给出两个概念得其关系，给一个概念一个关系得关系值，如果给两个关系得到关系的关系值。
        retinfo=[]
        templist=[]

        if self.ontomid.judge_ontoid(id1) and self.ontomid.judge_ontoid(id2) :
            val1 = list(self.ontocols.find_concept_data(id1).values())
            for v in val1:
                if type(v)==type([]):
                    templist=templist+v
            templist.remove(id1)
            for t in templist:
                if not self.ontomid.judge_ontoid(t):
                    templist.remove(t)
            if id2 in templist:
                tri=self.reason_tri_in_kn([id1,'X',id2])
                retinfo.append(id1)
                retinfo.append(tri[1])
                retinfo.append(id2)
        return retinfo
            # else:
            #     for t in templist:
            #         retinfo=self.direct_relation(t,id2,level+1)
            #     return retinfo

    def minus(self,id1,id2):#如果id1是概念（id2如果是概念则只减去这个节点，如果id2是关系，则减去这个关系枝），如果id1是关系（则目前只考虑id2是关系的情况）
        pass


    def inter(self,id1,id2): # 两个概念的交，这里指的是关系和关系值交，即不只是关系相交，对应的关系值也相交

        ret=[]
        rel1 = list(self.ontocols.find_concept_data(id1).keys())
        rel2 = list(self.ontocols.find_concept_data(id2).keys())
        rel1=self.ontocols.remove_str_key(globalinfo.strkeylist,rel1)
        rel2=self.ontocols.remove_str_key(globalinfo.strkeylist,rel2)
        for r in rel1:
            if r in rel2:
                val1=self.ontocols.find_val_of_rel_concept(id1,r)
                val2=self.ontocols.find_val_of_rel_concept(id2,r)
                if val1==val2:
                    templist=[]
                    templist.append(r)
                    templist.append(val1)
                    ret.append(templist)
        return ret

    def vinter(self,id1,id2): # 这里的交，指的是两个概念的关系值的交
        ret=[]
        templist1=[]
        templist2=[]
        val1 = list(self.ontocols.find_concept_data(id1).values())
        for v1 in val1:
            if type(v1)==type([]):
                templist1=templist1+v1
        val2 = list(self.ontocols.find_concept_data(id2).values())
        for v2 in val2:
            if type(v2)==type([]):
                templist2=templist1+v2
        for v in templist1:
            if v  in templist2:
                ret.append(v)
        return ret

    def kinter(self,id1,id2): # 这里的交，指的两个概念的关系的交
        rel1 = list(self.ontocols.find_concept_data(id1).keys())
        rel2 = list(self.ontocols.find_concept_data(id2).keys())
        rel1=self.ontocols.remove_str_key(globalinfo.strkeylist,rel1)
        rel2=self.ontocols.remove_str_key(globalinfo.strkeylist,rel2)
        ret=list(set(rel1).intersection(set(rel2)))
        return ret


    def uni(self,id1,id2):# 两个概念的并，这里指的是关系和关系值并，即不只是关系相并，对应的关系值也相并

        ret=[]
        rel1 = list(self.ontocols.find_concept_data(id1).keys())
        rel2 = list(self.ontocols.find_concept_data(id2).keys())
        rel1=self.ontocols.remove_str_key(globalinfo.strkeylist,rel1)
        rel2=self.ontocols.remove_str_key(globalinfo.strkeylist,rel2)
        for r in rel1:
            val1=self.ontocols.find_val_of_rel_concept(id1,r)
            templist1=[]
            templist1.append(r)
            templist1.append(val1)
            ret.append(templist1)
        for r in rel2:
            val2=self.ontocols.find_val_of_rel_concept(id2,r)
            templist2=[]
            templist2.append(r)
            templist2.append(val2)
            ret.append(templist2)

        return ret


    def vuni(self,id1,id2): ## 这里的并，指的是两个概念的关系值的并
        ret=[]
        templist1=[]
        templist2=[]
        val1 = list(self.ontocols.find_concept_data(id1).values())
        for v1 in val1:
            if type(v1)==type([]):
                templist1=templist1+v1
        val2 = list(self.ontocols.find_concept_data(id2).values())
        for v2 in val2:
            if type(v2)==type([]):
                templist2=templist2+v2
        ret=templist1+templist2
        return ret

    def kuni(self,id1,id2): #这里的并，指的两个概念的关系的并
        rel1 = list(self.ontocols.find_concept_data(id1).keys())
        rel2 = list(self.ontocols.find_concept_data(id2).keys())
        rel1=self.ontocols.remove_str_key(globalinfo.strkeylist,rel1)
        rel2=self.ontocols.remove_str_key(globalinfo.strkeylist,rel2)

        ret=list(set(rel1).union(set(rel2)))
        return ret

    def dif(self,id1,id2):# 两个概念的差，这里指的是关系和关系值差，即不只是关系相差，对应的关系值也相差
        t1=[]
        t2=[]
        ret=[]
        rel1 = list(self.ontocols.find_concept_data(id1).keys())
        rel2 = list(self.ontocols.find_concept_data(id2).keys())
        rel1=self.ontocols.remove_str_key(globalinfo.strkeylist,rel1)
        rel2=self.ontocols.remove_str_key(globalinfo.strkeylist,rel2)
        for r in rel1:
            val1=self.ontocols.find_val_of_rel_concept(id1,r)
            templist1=[]
            templist1.append(r)
            templist1.append(val1)
            t1.append(templist1)
        for r in rel2:
            val2=self.ontocols.find_val_of_rel_concept(id2,r)
            templist2=[]
            templist2.append(r)
            templist2.append(val2)
            t2.append(templist2)
        print(t1)
        print(t2)
        for l in t1:
            if l not in t2:
                ret.append(l)
        return ret
        pass
    def vdif(self,id1,id2): #这里的差，指的是两个概念的关系值的差
        ret=[]
        templist1=[]
        templist2=[]
        val1 = list(self.ontocols.find_concept_data(id1).values())
        for v1 in val1:
            if type(v1)==type([]):
                templist1=templist1+v1
        val2 = list(self.ontocols.find_concept_data(id2).values())
        for v2 in val2:
            if type(v2)==type([]):
                templist2=templist2+v2

        ret=list(set(templist1).difference(set(templist2)))

        return ret



        pass
    def kdif(self,id1,id2): #这里的差，指的是两个概念的关系的差
        rel1 = list(self.ontocols.find_concept_data(id1).keys())
        rel2 = list(self.ontocols.find_concept_data(id2).keys())
        rel1=self.ontocols.remove_str_key(globalinfo.strkeylist,rel1)
        rel2=self.ontocols.remove_str_key(globalinfo.strkeylist,rel2)

        ret=list(set(rel1).difference(set(rel2)))
        return ret

    def equ(self,id1,id2):
        pass


    def mul(self,id1,id2):
        pass
    def div(self,id1,id2):
        pass
    def ata(self,id1,id2):
        pass
    def doll(self,id1,id2):
        pass
    def pow(self,id1,id2):
        pass
    def ontoand(self,id1,id2):
        pass
    def ontoor(self,id1,id2):
        pass


    def question_parser(self, rule):
        temp = []
        vtemp = {}
        metarules = []
        patt = re.compile(r"(\w*[(|（]*((\w+[,|，]*){1,}|(\w+[<>!@#$%^&*]*))\w+[)|）]*)")
        vals = patt.findall(rule)
        for v in vals:
            temp.append(v[0])
        for t in temp:
            pt = self.clause_parser(t)
            metarules.append(pt)
            # print(metarules)
            for metarule in pt:
                if metarule.istitle():
                    vtemp[metarule] = []
                    # print(vtemp)
        print(metarules)
        return metarules, vtemp

    def reason_tri_in_kn(self, queslist):  # queslist 是一个三元组，主谓宾的形式。
        v1 = []
        vr = []
        v2 = []
        c1 = queslist[0]  # 主
        r = queslist[1]  # 谓
        c2 = queslist[2]  # 宾
        rule = False  # self.ontomid.find_val_of_rel_relation(r,'rule')[0] #看一下该关系是否有规则描述，如果有则对规则进行分析，规则的形式是：X r Y@X r1 Z,Y r1 Z
        if not rule:
            if not c1.istitle():  # 如果第一个参数不是未知数
                v1.append(c1)
                if r.istitle() and c2.istitle():  # 如果第二个和第三个参数都是未知数，则给出第一个参数的所有信息。 a X Y
                    rel = list(self.ontocols.find_concept_data(c1).keys())
                    rel.remove('cid')
                    rel.remove('_id')
                    rel.remove('csyn')
                    vr = rel
                    for ir in vr:
                        val = self.ontocols.find_val_of_rel_concept(c1, ir)
                        v2 += val

                if not r.istitle() and c2.istitle():  # 如果第二个参数不是未知数，第三个参数是未知数，则给出第一参数的第二参数下面的值 a b Y
                    vr.append(r)
                    val = self.ontocols.find_val_of_rel_concept(c1, r)
                    v2 += val

                if not r.istitle() and not c2.istitle():  # 如果第二个和第三个参数都不是未知数，则给出True 或者 False a b c
                    vr.append(r)
                    val = self.ontocols.find_val_of_rel_concept(c1, r)
                    if c2 in val:
                        v2.append(c2)

                if r.istitle() and not c2.istitle():  # 如果第二个参数是未知数，第三个参加不是未知数，则给出第一个参数和第三个参数的关系，即第二个参数的值。a R c
                    v2.append(c2)
                    rel = list(self.ontocols.find_concept_data(c1).keys())
                    rel.remove('cid')
                    rel.remove('_id')
                    rel.remove('csyn')

                    for ir in rel:
                        val = self.ontocols.find_val_of_rel_concept(c1, ir)
                        if c2 in val:
                            vr.append(ir)

            else:  # 如果第一个参数是未知数
                if r.istitle() and not c2.istitle():  # 如果第二个参数是未知数，第三个参数不是未知数，则给出第三个参数的所有信息。X, Z, c
                    v2.append(c2)
                    rel = list(self.ontocols.find_concept_data(c2).keys())
                    rel.remove('cid')
                    rel.remove('_id')
                    rel.remove('csyn')

                    for ir in rel:
                        invr = self.ontomid.get_reverse_id(ir)
                        vr.append(invr)
                        val = self.ontocols.find_val_of_rel_concept(c2, ir)
                        v1 += val
                        v2.append(c2)

                if not r.istitle() and not c2.istitle():  # 如果第二个参数和第三个参数都不是未知数，则给出第三个参数和第二个参数的反关系的值。 X b c
                    invr = self.ontomid.get_reverse_id(r)
                    vr.append(invr)
                    val = self.ontocols.find_val_of_rel_concept(c2, invr)
                    v1 += val
                    v2.append(c2)

        return v1, vr, v2

    def reason_tri_in_kn_batch(self, batlist):  # 这里的列表中的元素为list 如[[]，[]，[]]
        battemp = []
        if type(batlist[0]) != type([]):
            battemp.append([batlist[0]])
        else:
            battemp.append(batlist[0])

        if type(batlist[1]) != type([]):
            battemp.append([batlist[1]])
        else:
            battemp.append(batlist[1])

        if type(batlist[2]) != type([]):
            battemp.append([batlist[2]])
        else:
            battemp.append(batlist[2])
            # 以上是字符和列表的转换
        ret = []
        v1list = []
        vrlist = []
        v2list = []
        c1list = battemp[0]
        rlist = battemp[1]
        c2list = battemp[2]
        for c1 in c1list:
            if not c1.istitle():  # 如果c1不是变量，则把c1放到列表中   第一个元素是常数 a
                tempc1list = []
                v1list.append(c1)
                tempc1list.append(c1)
                for vr in rlist:  # 检查一下vr是否是变量，
                    if not vr.istitle():  # 如果不是变量，则首先把vr放到列表中  第二个元素是常数  r
                        temprlist = []
                        vrlist.append(vr)
                        temprlist.append(vr)
                        for c2 in c2list:  # 检查一下c2是否是变量，
                            if not c2.istitle():  # 如果不是变量，则放到列表中    第三个元素是常数  b
                                tempc2list = []
                                v2list.append(c2)
                                tempc2list.append(c2)
                                ret = self.reason_tri_in_kn(tempc1list + temprlist + tempc2list)
                            else:  # 如果是变量               第三个元素是变量 Z
                                tempc2list = []
                                tempc2list.append(c2)
                                ret = self.reason_tri_in_kn(tempc1list + temprlist + tempc2list)
                                v2list = ret[2]
                    else:
                        temprlist = []
                        temprlist.append(vr)
                        for c2 in c2list:
                            if not c2.istitle():
                                tempc2list = []
                                v2list.append(c2)
                                tempc2list.append(c2)
                                ret = self.reason_tri_in_kn(tempc1list + temprlist + tempc2list)
                                vrlist = ret[1]
                            else:
                                tempc2list = []
                                tempc2list.append(c2)
                                ret = self.reason_tri_in_kn(tempc1list + temprlist + tempc2list)
                                vrlist = ret[1]
                                v2list = ret[2]



            else:
                tempc1list = []
                tempc1list.append(c1)
                for vr in rlist:  # 检查一下vr是否是变量，
                    if not vr.istitle():  # 如果不是变量，则首先把vr放到列表中 X r
                        temprlist = []
                        vrlist.append(vr)
                        temprlist.append(vr)
                        for c2 in c2list:  # 检查一下c2是否是变量，
                            if not c2.istitle():  # 如果不是变量，则放到列表中 X r b
                                tempc2list = []
                                v2list.append(c2)
                                tempc2list.append(c2)
                                ret = self.reason_tri_in_kn(tempc1list + temprlist + tempc2list)

                    else:
                        temprlist = []
                        temprlist.append(vr)
                        for c2 in c2list:  # 检查一下c2是否是变量，
                            if not c2.istitle():  # 如果不是变量，则放到列表中 X Y b
                                tempc2list = []
                                v2list.append(c2)
                                tempc2list.append(c2)
                                ret = self.reason_tri_in_kn(tempc1list + temprlist + tempc2list)

        # v1list += ret[0]
        # vrlist += ret[1]

        return ret

    # def reason_by_rule(self, headlist,rulelist):  # 从关系的rule中取出规则，规则在数据库中的格式是三元组的集合，第一个三元组是规则头，后面的三元组是规则体。[['i5','X','Y'],['X','r8','Z'],['Y','r8','Z']]
    #
    #     vardict = {}  # 用于存储变量及值的字典类型数据，如{'X':'i11','Y':'c4}
    #     for rule in rulelist:  # 将所有变量放到一个字典里面。
    #         for e in rule:
    #             if e.istitle():
    #                 vardict[e] = []
    #     for h in range(0, len(headlist)):  # 把前端传来的值传到规则头中，并给对应的变量赋值。
    #         if rulelist[0][h].istitle() and not headlist[h].istitle():
    #             vardict[rulelist[0][h]] = headlist[h]
    #         if rulelist[0][h].istitle() and headlist[h].istitle():
    #             retval = rulelist[0][h]  # 找到要返回的变量
    #     epoch = 0
    #     while (epoch <= 12):  # 这里是求出需要返回的值
    #         for i in range(1, len(rulelist)):
    #             num = 0
    #             place = 0
    #             for j in range(0, len(rulelist[i])):
    #
    #                 if type(rulelist[i][j]) != type([]):
    #                     if rulelist[i][j].istitle():
    #                         if vardict[rulelist[i][j]]:
    #                             rulelist[i][j] = vardict[rulelist[i][j]]
    #                         else:
    #                             num += 1
    #                             place = j
    #             if num == 1:
    #                 print(epoch, vardict)
    #                 vardict[rulelist[i][place]] = self.reason_tri_in_kn_batch(rulelist[i])[place]
    #         epoch += 1
    #
    #     return retval, vardict[retval]
    #
    def pre_process_ruleist(self,rulelist,assign={}):
        vardict = {}  # 用于存储变量及值的字典类型数据，如{'X':'i11','Y':'c4}
        rulechecklist=[]
        solveorder=[]
        a=0
        if  assign:
            a=list(assign.keys())[0]
            vardict[a]=assign[a]
        for rule in rulelist:  # 将所有变量放到一个字典里面。并且对于非变量的内容改为yes,目的是如果dict里面所有的键值为yes，说明这个查询是可解的。
            templist=[]
            for e in rule:
                if e.istitle() and e!=a:
                    vardict[e] = []
                    templist.append(e)
                else:
                    templist.append('yes')
            rulechecklist.append(templist)

        vartemp=vardict.copy()
        for times in range(0,len(vartemp)):
            for rule in rulechecklist: # 根据一个三元组里面有两个确定，第三个值就能确定的原理，来得到是否可以求出所有的变量。
                for e in rule:
                    if e.istitle():
                        if vartemp[e]=='yes':
                            rule[rule.index(e)]='yes' #查询一下字典里面是否有值求解出来，一开始都是空的，然而通过两个确定第三的原理，可以求得第三个存储到字典里面，所以每次都要看一遍字典，是否有可求出的值。

                num=0
                for e in rule: #这里是两个确定第三个值的原理的实现。并且记录下来求解的
                    if not e.istitle():
                        num=num+1
                    else:
                        v=e
                if num==2:
                    vartemp[v]='yes'
                    solveorder.append(rulechecklist.index(rule))
        vnum=0
        for (k,v) in vartemp.items():#这里是检查 字典里面是否还有空值，如果有，说明所给的条件不能求出所有答案
            if v  :
                vnum=vnum+1
        if vnum==len(vartemp):
            solve=True
        else:
            solve=False
        return solve,vardict,solveorder





    def reason_by_rule(self,findtri,rule):
        tempdict={}
        qv=None
        headlist=rule[0]
        rulelist=rule[1]
        for f in findtri:
            if not f.istitle():
                p=findtri.index(f)
                if headlist[p].istitle():
                    tempdict[headlist[p]]=f
            else:
                p=findtri.index(f)
                qv=headlist[p]

        pre=self.pre_process_ruleist(rulelist,tempdict)
        print(pre)
        vardict=pre[1]
        solveorder=pre[2]
        if pre[0]:
            for order in range(0,len(solveorder)):
                for e in rulelist[solveorder[order]]:
                    if e.istitle():
                        if vardict[e]:

                            rulelist[solveorder[order]][rulelist[solveorder[order]].index(e)]=vardict[e]
                        else:
                            var=e
                            place=rulelist[solveorder[order]].index(e)
                vardict[var]=self.reason_tri_in_kn_batch(rulelist[solveorder[order]])[place]

        else:
            print('cannot give answers of the question because of lack of conditions')
        if qv:
            qinfo=vardict[qv]
        return qinfo,vardict




    def find_by_rule(self,rulelist):  # 规则列表如。[['i5','X','Y'],['X','r8','Z'],['Y','r8','Z']]，

        pre=self.pre_process_ruleist(rulelist)
        print(pre)
        vardict=pre[1]
        solveorder=pre[2]
        if pre[0]:

            for order in range(0,len(solveorder)):
                for e in rulelist[solveorder[order]]:
                    if e.istitle():
                        if vardict[e]:

                            rulelist[solveorder[order]][rulelist[solveorder[order]].index(e)]=vardict[e]
                        else:
                            var=e
                            place=rulelist[solveorder[order]].index(e)
                vardict[var]=self.reason_tri_in_kn_batch(rulelist[solveorder[order]])[place]

        else:
            print('cannot give answers of the question because of lack of conditions')

        return vardict

        # vardict = {}  # 用于存储变量及值的字典类型数据，如{'X':'i11','Y':'c4}
        # rulechecklist=[]
        # for rule in rulelist:  # 将所有变量放到一个字典里面。
        #     templist=[]
        #     for e in rule:
        #         if e.istitle():
        #             vardict[e] = []
        #             templist.append(e)
        #         else:
        #             templist.append(1)
        #     rulechecklist.append(templist)
        # print(vardict,rulechecklist)
        #
        # # 用于检测
        # vartemp=vardict

        # for h in range(0, len(headlist)):  # 把前端传来的值传到规则头中，并给对应的变量赋值。
        #     if rulelist[0][h].istitle() and not headlist[h].istitle():
        #         vardict[rulelist[0][h]] = headlist[h]
        #     if rulelist[0][h].istitle() and headlist[h].istitle():
        #         retval = rulelist[0][h]  # 找到要返回的变量
        # epoch = 0
        # while (epoch <= 12):  # 这里是求出需要返回的值
        #     for i in range(0, len(rulelist)):
        #         num = 0
        #         place = 0
        #         for j in range(0, len(rulelist[i])):
        #
        #             if type(rulelist[i][j]) != type([]):
        #                 if rulelist[i][j].istitle():
        #                     if vardict[rulelist[i][j]]:
        #                         rulelist[i][j] = vardict[rulelist[i][j]]
        #                     else:
        #                         num += 1
        #                         place = j
        #         if num == 1:
        #             print(epoch, vardict)
        #             vardict[rulelist[i][place]] = self.reason_tri_in_kn_batch(rulelist[i])[place]
        #     epoch += 1
        #
        # return vardict




        # def reason_by_rule(self, queslist):  # 这里的推理只针对二元关系，先不考虑大于，运算等  ['2100000001', '1000000052', 'Y']
        #     # 这里要加上检查传进来的参数有没有值，不能全是变量，如果全是变量，返回空值,这里只针对二元关系 在第一位就找该概念的正关系，如果在第2就找该关系的逆关系？？？？
        #     done1 = False
        #     done2 = False
        #     """for count in range(1,len(queslist)):
        #         if not queslist[count].istitle():
        #             done=True
        #             v1=queslist[count]"""
        #     v1 = []
        #     v2 = []
        #
        #     if not queslist[1].istitle():
        #         done1 = True
        #         v1.append(queslist[1])
        #
        #     if not queslist[2].istitle():
        #         done2 = True
        #         v2.append(queslist[2])
        #     print('v1', v1)
        #     print('v2', v2)
        #     if (done1 or done2):
        #         if done1:
        #             v2 = list(set(v2).union(set(self.find_of_reason(queslist[0], queslist[1], True))))
        #             print('v2', v2)
        #             rule = self.ontocols.find_val_of_rel_relation(queslist[0], 'rule')  # 找关系的data表中是否有rule的值
        #             print(rule)
        #             if rule:
        #                 rulevars = {}  # 参数词典
        #                 parl = self.question_parser(rule[0])
        #                 rulevars = parl[1]  # 将变量做一个表，以后推理时对隔开的数据进行增加
        #                 ###以下是将问句当中的数值增加到变量表中
        #                 for count in range(1, len(queslist)):
        #                     if not queslist[count].istitle():
        #                         rulevars[parl[0][0][count]].append(queslist[count])
        #                         print(rulevars)
        #                 for rnum in range(1, len(parl[0])):
        #                     qlist = []
        #                     qlist.append(parl[0][rnum][0])
        #
        #                     for vnum in range(1, len(parl[0][rnum])):
        #                         if len(rulevars[parl[0][rnum][vnum]]) != 0:
        #                             for vals in rulevars[parl[0][rnum][vnum]]:
        #                                 qlist.append(vals)
        #
        #                         else:
        #                             qlist.append(parl[0][rnum][vnum])
        #
        #                     temp = self.reason_by_rule(qlist)
        #
        #                     v2 = list(set(v2).union(temp[1]))
        #                     print(temp)
        #             print('v11111', v1)
        #             print('v22222', v2)
        #             return v1, v2
        #
        #         if done2:
        #             v1 = list(set(v1).union(set(self.find_of_reason(queslist[0], queslist[2], False))))
        #             print('v1', v1)
        #             rule = self.ontocols.find_val_of_rel_relation(queslist[0], 'rule')  # 找关系的data表中是否有rule的值
        #             print(rule)
        #             if rule:
        #                 rulevars = {}  # 参数词典
        #                 parl = self.question_parser(rule[0])
        #                 rulevars = parl[1]  # 将变量做一个表，以后推理时对隔开的数据进行增加
        #                 ###以下是将问句当中的数值增加到变量表中
        #                 for count in range(1, len(queslist)):
        #                     if not queslist[count].istitle():
        #                         rulevars[parl[0][0][count]].append(queslist[count])
        #                         print(rulevars)
        #                 for rnum in range(1, len(parl[0])):
        #                     qlist = []
        #                     qlist.append(parl[0][rnum][0])
        #
        #                     for vnum in range(1, len(parl[0][rnum])):
        #                         if len(rulevars[parl[0][rnum][vnum]]) != 0:
        #                             for vals in rulevars[parl[0][rnum][vnum]]:
        #                                 qlist.append(vals)
        #
        #                         else:
        #                             qlist.append(parl[0][rnum][vnum])
        #
        #                     temp = self.reason_by_rule(qlist)
        #
        #                     v1 = list(set(v1).union(temp[0]))
        #                     print(temp)
        #
        #             print('v11111', v1)
        #             print('v22222', v2)
        #             return v1, v2
        #     else:
        #
        #         return v1, v2

        ###以下内容是对规则中的子句进行推理

    # def find_of_reason(self, rid, val, place):
    #     if place:
    #         results = self.ontocols.find_val_of_rel_concept(val, rid)
    #     # print(results)
    #     else:
    #         results = self.ontocols.find_concepts_with_relval(rid, val)
    #     return results

    def clause_parser(self, clause):
        patt = re.compile(r"\w+")
        vs = patt.findall(clause)
        return vs


class ImportFilmActorData:
    is_a = '2100000001'
    superclass_of = '2100000002'
    instace_of = '2100000003'
    has_instance = '2100000004'
    onto_null = '0000000000'
    onto_root = '1000000000'
    actatt = {'aurl': '演员网址', 'apic': '演员图片', 'fans': '演员粉丝', 'high': '身高', 'weight': '体重', 'country': '国籍',
              'mingzu': '民族', 'xingzuo': '星座', 'xiexing': '血型', 'birthday': '出生日期', 'sex': '性别', 'birthplace': '出生地',
              'biyexuexiao': '毕业学校', 'jingjigongsi': '经纪公司'}
    m = {'murl': '电影网址', 'mpic': '电影海报', 'director': '电影导演', 'time': '电影时长', 'year': '电影年份', 'area': '电影地区',
         'language': '电影语言'}

    def __init__(self, ontodb, sourcedb, actordb):
        db = globalinfo.con[ontodb]
        sdb = globalinfo.con[sourcedb]
        adb = globalinfo.con[actordb]
        colct = db['ConTerm']
        colcd = db['ConData']
        colrt = db['RelTerm']
        colrd = db['RelData']
        colid = db['idPool']
        self.scol = sdb['fcol']
        self.acol = adb['acol']
        self.ontocols = OntoLow(colct, colcd, colrt, colrd, colid)
        self.onto = OntoMid(ontodb)

    def insert_relations_first(self, reltype):  # 在运行程序前一定要重新看一下程序。
        num = 0
        for (a, b) in reltype.items():
            ids = self.onto.insert_relation_sta(b, 'attid', True)
            self.ontocols.insert_rel_of_relation('2000000000', self.superclass_of, ids[0])
            self.ontocols.insert_rel_of_relation('2000000000', self.superclass_of, ids[1])
            bid = self.ontocols.find_cid_with_term(b)[0]
            cid = self.ontocols.find_cid_with_term('演员')[0]
            self.ontocols.insert_rel_of_concept(cid, ids[0], bid)
            subid = self.ontocols.find_val_of_rel_concept(cid, self.superclass_of)
            if subid:
                for d in subid:
                    self.ontocols.insert_rel_of_concept(d, ids[0], bid)

            num = num + 1
            print('att  ', num)

    def import_mon_data(self):
        recs = self.scol.find()
        num = 0
        url_id = {}
        for rn in range(1, 25733):
            r = recs[rn]
            cid = self.ontocols.find_cid_with_term(r['mname'])
            if 'gloss' in r.keys():
                self.insert_gloss_of_data(cid, r['gloss'])
            else:
                self.insert_gloss_of_data(cid, '')
            # for l in r['leix']:
            #	leid=self.ontocols.find_cid_with_term(l)[0]
            #	print(l+'  '+leid+'  '+cid+'  '+r['mname'])
            #	self.ontocols.insert_rel_of_concept(leid, self.has_instance, cid)

            # if 'mid' in r.keys():
            #	r.pop('mid')
            # if 'gloss' in r.keys():
            #	r.pop('gloss')

            # if 'actor' in r.keys():
            #	r.pop('actor')
            # if 'othername' in r.keys():
            #	r.pop('othername')

            print(rn)

    def classify_for_data(self, fid, leix):
        for l in leix:
            lid = self.ontocols.find_cid_with_term(l + '片')
            self.ontocols.insert_rel_of_concept(lid, self.has_instance, fid)

    def insert_gloss_of_data(self, fid, gloss):

        self.ontocols.insert_val_of_rel_concept(fid, 'gloss', gloss)

    def insert_csyn_of_data(self, fid, csyn):
        for c in csyn:
            self.ontocols.insert_concept_term(c)
            self.ontocols.insert_concept_cid(c, fid)
            self.ontocols.insert_val_of_rel_concept(fid, 'csyn', c)

    def insert_actor_data(self):
        recs = self.acol.find()
        num = 0
        url_id = {}
        career = 0
        self.insert_relations_first(self.actatt)
        for a in recs:
            '''
            #根据职业分类，统计所有职业，如果没有则为其它
            if 'career' in a.keys():
                for c in a['career']:
                    career.append(c)

            '''
            num = num + 1
            print(num, '  ', career)

    def generate_id(self):
        self.ontocols.generate_id()

    def insert_main_term(self, term, mainkey, idtype):  # mainkey 是一个主键，用于区别其它概念的。
        termrec = self.ontocols.find_concepts_term()
        tcid = 0
        for trec in termrec:
            if not self.find_dup_rec(term, self.ontocols.colct):  # 如果term表里面没有这个术语
                if not self.find_dup_rec(mainkey, self.ontocols.colct):  # 如果用来识别这个术语是否是同一概念的主键不在术语表中
                    tcid = self.onto.insert_concept_sta(term, idtype, True)  # 插入一个新的概念，包括术语和概念表中的数据
                    self.onto.insert_concept_sta(mainkey, idtype, True)

                else:  # 如果主键存在，说明这个术语和其中一个术语虽然不同名，但是是指的同一个事，即是同义词集。
                    self.ontocols.insert_concept_term(term)  # 术语表中增加这个术语，
                    tcid = self.ontocols.find_cid_with_term(mainkey)[0]  # 找到这个主键对应的id号
                    cid = self.ontocols.find_concepts_with_relval('2100000043', tcid)
                    if cid:  # 找到这个主键对应的这个值的概念的id号
                        self.ontocols.insert_concept_cid(term, cid)  # 把id号添加到术语的cid表中
            else:  # 如果term表中有这个term
                if not self.find_dup_rec(mainkey, self.ontocols.colct):  # 看一下对应的主键是不是存在于term中，如果不存在，说明这个term对应多个意思。
                    tcid = self.ontocols.get_id(idtype)
                    self.ontocols.insert_concept_cid(term, tcid)
                    self.ontocols.insert_concept_data(tcid)
                    self.ontocols.insert_val_of_rel_concept(tcid, 'csyn', term)
                    self.onto.insert_concept_sta(mainkey, idtype, True)
        return tcid

    def find_dup_rec(self, dup, col):  # 查找有没有相同的术语，因为术语保证只有一个
        recs = col.find_all()
        ret = False
        for r in recs:
            if r['term'][0] == dup:
                ret = True
                break
        return ret

    def insert_actor_atts(self, fid, key, val):
        print(key)
        rid = self.ontocols.find_relation_term('有' + self.actatt[key])['rid'][0]
        if isinstance(val, list):
            vid = self.onto.insert_concept_sta(val[0], 'insid', True)
        else:
            vid = self.onto.insert_concept_sta(val, 'insid', True)
        keyid = self.ontocols.find_cid_with_term(self.actatt[key])[0]
        self.ontocols.insert_rel_of_concept(fid, rid, vid)
        self.ontocols.insert_rel_of_concept(keyid, self.has_instance, vid)

    def insert_film_atts(self, fid, key, val):
        print(key)
        rid = self.ontocols.find_relation_term('有' + self.m[key])['rid'][0]
        if isinstance(val, list):
            vid = self.onto.insert_concept_sta(val[0], 'insid', True)
        else:
            vid = self.onto.insert_concept_sta(val, 'insid', True)
        keyid = self.ontocols.find_cid_with_term(self.m[key])[0]
        self.ontocols.insert_rel_of_concept(fid, rid, vid)
        self.ontocols.insert_rel_of_concept(keyid, self.has_instance, vid)

    def conbine_film_actor(self):
        recs = self.scol.find()
        for r in recs:
            for a in a['actor']:
                print()


class OntoXls:
    is_a = '2100000001'
    superclass_of = '2100000002'
    instace_of = '2100000003'
    has_instance = '2100000004'
    onto_null = '0000000000'
    onto_root = '1000000000'
    ontocols = 0
    ontomid = 0
    ontohigh = 0

    def __init__(self, ontodb):

        db = globalinfo.con[ontodb]
        colct = db['ConTerm']
        colcd = db['ConData']
        colrt = db['RelTerm']
        colrd = db['RelData']
        colid = db['idPool']
        colrec = db['idrec']
        self.ontocols = OntoLow(colct, colcd, colrt, colrd, colid, colrec)
        self.ontomid = OntoMid(ontodb)
        self.ontohigh = OntoHigh(ontodb)

    def xlsRead_con(self, fname):
        xls = xlrd.open_workbook(fname)
        sheetcon = xls.sheet_by_name('con')  # read concept table
        # sheetins=xls.sheet_by_name('ins') #read instance table
        crows = sheetcon.nrows  # concept rows
        ncols = sheetcon.ncols
        for i in range(crows):
            t1 = sheetcon.cell_value(i, 0)  # concept first row
            t2 = sheetcon.cell_value(i, 1)  # concept second row
            t3 = sheetcon.cell_value(i, 2)  # concept third row
            t4 = sheetcon.cell_value(i, 3)  # concept third row

            id1 = self.ontomid.insert_concept_term_data(t1)
            id3 = self.ontomid.insert_concept_term_data(t4)
            id2 = self.ontomid.insert_relation_term_data(t2 + t3, t3 + t2)
            self.ontomid.insert_binrel_of_concept_data(id1[0], id2[0], id3[0])

    # def xlsRead_ins(self, fname):
    #     xls = xlrd.open_workbook(fname)
    #     sheetcon = xls.sheet_by_name('ins')  # read concept table
    #     crows = sheetcon.nrows
    #     firstrow = sheetcon.row_values(0)  # 读取excel中的第1行，
    #     fid = []
    #     for fir in range(0, len(firstrow)):
    #         fid.append(self.ontomid.insert_concept_term_data(firstrow[fir])[0])  # 插入并获取表格第一行的概念的id,放到列表里面
    #
    #     for i in range(1, crows):
    #         ids = []  # 用来存放
    #         row = sheetcon.row_values(i)  # 读取excel行数据
    #         for j in range(0, len(row)):
    #             if j == 1:  # 这个地方是单独处理学生的信息，尤其是重名学生的信息。
    #                 if self.ontocols.find_concept_term(row[j]):  # 如果有重名，则给出新的id,术语表中增加id,不增加术语。
    #                     ids.append(self.ontomid.insert_instance_term_in_kn(row[j])[0])
    #                 else:
    #                     ids.append(self.ontomid.insert_instance_term_data(row[j])[0])
    #             elif j in (5, 6, 7, 8, 9):  # 对于数据的列的处理，用了round 四舍五入
    #                 ids.append(self.ontomid.insert_instance_term_data(round(row[j]))[0])
    #             else:
    #                 ids.append(self.ontomid.insert_instance_term_data(row[j])[0])
    #             self.ontomid.insert_binrel_of_concept_data(ids[j], '2100000003', fid[j])  # 所有都是实例
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '学号')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '年级')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '班级')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '课程')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '作业成绩')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '平时成绩')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '期中成绩')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '期末成绩')
    #         self.Make_realtion_in_xls(firstrow, ids, '姓名', '总成绩')
    #         self.Make_realtion_in_xls(firstrow, ids, '作业成绩', '课程')
    #         self.Make_realtion_in_xls(firstrow, ids, '平时成绩', '课程')
    #         self.Make_realtion_in_xls(firstrow, ids, '期中成绩', '课程')
    #         self.Make_realtion_in_xls(firstrow, ids, '期末成绩', '课程')
    #         self.Make_realtion_in_xls(firstrow, ids, '总成绩', '课程')

    def xlsRead_ins(self, fname, unique=0, keycol=1, prestr=''):
        xls = xlrd.open_workbook(fname)
        sheetcon = xls.sheet_by_name('ins')  # read concept table
        crows = sheetcon.nrows
        firstrow = sheetcon.row_values(0)  # 读取excel中的第1行，
        relid = []
        fid = []
        cidkeycol = self.ontohigh.add_concept(firstrow[keycol])[0]  # 得到关键列的第一行的标题的id
        cidunique = self.ontohigh.add_concept(firstrow[unique])[0]  # 得到唯一号索引列的标题的id
        for fir in range(0, len(firstrow)):  # 这里是建关系，把第一行中的关系先建好，并且得到关系的id, 放到数组中
            if fir != keycol and fir != unique:
                fid.append(self.ontohigh.add_concept(firstrow[fir])[0])  # 插入并获取表格第一行的概念的id,放到列表里面
                relid.append(self.ontomid.insert_relation_term_data(firstrow[keycol] + firstrow[fir],
                                                                    firstrow[fir] + firstrow[keycol])[0])

        for i in range(1, crows):
            ids = []
            row = sheetcon.row_values(i)  # 读取excel行数据

            if not self.ontomid.find_concept(row[unique]):
                if self.ontomid.find_concept(row[keycol]):
                    cidkeycoldata = self.ontomid.insert_instance_term_in_kn(row[keycol])[0]
                else:
                    cidkeycoldata = self.ontomid.insert_instance_term_data(row[keycol])[0]
            ciduniquedata = self.ontohigh.add_concept(row[unique])[0]  # 插入并获取关键列的概念的id,放到列表里面
            self.ontomid.insert_binrel_of_concept_data(cidkeycoldata, '2100000003', cidkeycol)
            self.ontomid.insert_binrel_of_concept_data(ciduniquedata, '2100000003', cidunique)
            num = 0;
            for j in range(0, len(row)):
                if j == unique or j == keycol:
                    pass
                else:
                    insid = self.ontomid.insert_instance_term_data(row[j])[0]
                    ids.append(insid)
                    self.ontomid.insert_binrel_of_concept_data(insid, '2100000003', fid[num])  # 所有都是实例
                    num = num + 1
            for n in range(0, len(ids)):
                self.ontomid.insert_binrel_of_concept_data(cidkeycoldata, relid[n], ids[n])

    def Make_realtion_in_xls(self, frlist, otherlist, col1, col2):
        index1 = frlist.index(col2)
        index2 = frlist.index(col1)
        relid = self.ontomid.insert_relation_term_data(col1 + col2, col2 + col1)[0]
        self.ontomid.insert_binrel_of_concept_data(otherlist[index2], relid, otherlist[index1])

    def dupTerm(self, term):
        if self.ontocols.find_concept_term(term):
            flag = False
        else:
            flag = True
        return flag

class OntoWnt:
    is_a = '2100000001'
    superclass_of = '2100000002'
    instace_of = '2100000003'
    has_instance = '2100000004'
    onto_null = '0000000000'
    onto_root = '1000000000'
    ontocols = 0
    ontomid = 0
    ontohigh = 0


    def __init__(self, ontodb):

        db = globalinfo.con[ontodb]
        colct = db['ConTerm']
        colcd = db['ConData']
        colrt = db['RelTerm']
        colrd = db['RelData']
        colid = db['idPool']
        colrec = db['idrec']
        self.ontocols = OntoLow(colct, colcd, colrt, colrd, colid, colrec)
        self.ontomid = OntoMid(ontodb)
        self.ontohigh = OntoHigh(ontodb)


        # print(self.sqlcur)
    def opensql(self):
        try:
            wntsql = pymysql.connect(host='127.0.0.1',port=3306, user='root',passwd='111111',db='wnt',charset='utf8')
            sqlcur=wntsql.cursor()
            print('mysql conn success')
        except:
            print('mysql conn error')

        return wntsql,sqlcur

    def exeQuery(self,cur,sql):
        cur.execute(sql)
        return (cur)
        # print(info)

    def closesql(self,db):
        db[1].close()
        db[0].close()


if __name__ == '__main__':
    # o=OntoXls('b11002')
    # a=o.dupTerm('丹麦')
    # print(a)
    # 	db=con['taskonto']
    # db1=con['t']
    wnt=OntoWnt(globalinfo.dbname)
    db=wnt.opensql()
    info=wnt.exeQuery(db[1],'select name from check_entity')

    print(info.fetchall())
    # a[1].execute('select * from wnt')
    wnt.closesql(db)
    # wnt.opensql()[1].execute('select * from wnt')
    # print(cur)
    # wnt.exeQuery(cur,'select * from wnt')


    # ore = OntoReason(globalinfo.dbname)
    # info1=ore.reason_tri_in_kn(['i12','Y','i3'])
    # info=ore.reason_tri_in_kn(['i150','r45','X'])
    # info=ore.ontomid.ontocols.find_concept_data('i3')
    # info=ore.reason_tri_in_kn_batch([['i16','i12'],['A'],['C']])
    # info = ore.reason_by_rule(['A', 'r11', 'i100'], [['X', 'r100', 'Y'], ['X', 'r3', 'Z'], ['Y', 'r3', 'Z']])
    # info = ore.find_by_rule( [["c60", "r60", "A"],['A','r45','X'],['A','r33','Y']])
    # info=ore.reason_by_rule(["i340", "r35", "B"],[["C", "r35", "B"],[["C", "A", "i3"],['i334','A','B'],['B','2100000003','Y']]])
    # info=ore.pre_process_ruleist([["V", "r35", "X"],['i334','A','X'],['X','r32','Y']],{'V':'i9'})
    # info = ore.direct_relation('i331','i329')
    # info=ore.dif('i105','i100')
    # print(info)
    # print(info2)
    #     ontom = OntoMid(globalinfo.dbname)
    # info=ontom.fuzzy_find_in_termtable('玉')
    # info=ontom.get_info_of_csyn_id(['i77','i303'], '?')
    # info=ontom.get_all_info_of_search(['i303'], [], [])
    # info = ontom.find_into_for_searchbox([['i303', 'i306'], ['r67']], ' ')
    # info=ontom.find_concept('作业成绩')
    # info=ontom.insert_method_term_data('平均成绩', '平均成绩逆')
    # 	info=ontom.get_info_of_relatt_of_conins('信息论与编码','成绩')
    #     print(info)
    # oh=OntoHigh(globalinfo.dbname)
    # oh.add_concept_batch(['学生','学号','年级','班级','学院','课程','爱好'])
    # ox=OntoXls(globalinfo.dbname)
    # ox.xlsRead_ins('f:/excel/edutest.xls')
    # oh.generate_concept_from_instance('12通信','星座')
    # oh.add_concept('星座')
    # oh.add_instance_batch(['白羊座','金牛座','双子座','巨蟹座','狮子座','处女座','天秤座','天蝎座','射手座','摩羯座','水瓶座','双鱼座'])
    # oh.add_hasinstance_between_concept_instance_batch('星座',['白羊座','金牛座','双子座','巨蟹座','狮子座','处女座','天秤座','天蝎座','射手座','摩羯座','水瓶座','双鱼座'])
    # info=ontom.info_for_echart2_force('1000000033')
    # info=ontom.find_concept_for_echarts('张学友')
    # info=ontom.insert_concept_term_in_kn('测试')
    # info=ontom.insert_concept_term_data('学院')
    # info=ontom.delete_concept_term_data('测试', 'c4')
    # info=ontom.delete_concept_term_data('test', 'c7')
    # info=ontom.update_concept_term_data('测试', 'test', 'c7')
    # info=ontom.insert_relation_term_data('rel')
    # ontom.update_relation_attribute_term_data('att', 'rrrr', 'a5')
    # info=ontom.delete_relation_term_data('rrrr','r11')
    # info=ontom.delete_attribute_term_data('rrrr','a5')
    # info=ontom.insert_attribute_term_data('att')
    # ontom.insert_binrel_of_concept_data(info[0], '2100000001', '1000000000')
    # info=ontom.ontocols.delete_relation_data('r2')
    # ontom.update_relation_term_data('rel', 'reltest', 'r5')
    # print(info)
    # 	colct=db['ConTerm']
    # 	colcd=db['ConData']
    # 	colrt=db['RelTerm']
    # 	colrd=db['RelData']
    # 	colid=db['idPool']

    # t=Dbc(colcd)
    # t1=Dbc(col1)
    #     xls=OntoXls(globalinfo.dbname)
    #     xls.xlsRead_con('f:/excel/edu.xls')
    #  	xls.xlsRead_ins('e:/excel/edutest.xls')
    # 	xls.xlsRead_con('e:/excel/edu.xls')

    # xls.task_three('e:/excel/task3.xls')
    # onto=OntoXls(globalinfo.dbname)
    # onto.task_three('e:/excel/task3.xls')
    # info=onto.task3_prob_of_att('e:/excel/task30808.xls', 5)
    # info=onto.task3_find_cor('e:/excel/task30808.xls', 1)
    # info=onto.task3_mutaul('e:/excel/e_pro.xls', 'e:/excel/all_cor.xls')
    # info=onto.task3_result('3109965344','C16','D056','OR034',5.17)
    # 	info=onto.task3_final('e:/excel/sample.xls', 'e:/excel/result_test3.xls')
    # info=onto.task3_method1('3105915023','D063',3.12, 'OR092','C16')
    # info=onto.knowledge_result('e:/excel/test3.xls', 'e:/excel/result_kn.xls')
    # print(info)
    # 	ids=onto.get_reverse_id('c121')
    # 	print(ids)
    # info=onto.find_info_for_concept_id('0000000000')
    # info=onto.find_multi('王菲#出生日期')
    # print(info)

    #     onto.insert_concept('概念3', '关系3', '概念4')
    # onto.insert_concept_sta('test', 'conid', False)
    # 	o=OntoLow(colct,colcd,colrt,colrd,colid)
    # 	o.generate_id()
    # ore=OntoReason('jbl')
    # a=ore.reason_by_rule("a10001(X,Ya):-a10002(X，Z,A),210003(Y,Z),A<B")
    # a=ore.reason_by_rule(["2100000001",'Z','1000000000'])
    # a=ore.find_of_reason("2100000002", "1000000013", False)
    # a=ImportFilmActorData('filmonto','filmdb','actordb')
    # a.import_mon_data()
    # a.insert_actor_data()
    # a.insert_relations_first(a.actatt)
    # a.generate_id()
    # b=a.find_dup_rec('概念', a.ontocols.colct)
    # a.import_mon_data()
    # a.insert_term('概念')
    # print(a)
    # dd=o.insert_rels_of_concept('1000000093', ['a','b'])
    # o.insert_val_of_rel_concept('1000000093', 'a', 'add')
    # colct.update({'cid':'1000000002'},{'$addToSet':{'term':'三星用户'}})
    # t1.find_all()
    # t1.delete_doc('d1', 2)
    # t1.find_all()
    # s=o.find_concept_data('1100000111')
    # print(s)
    # print('\n')


    # o.delete_concept_data('1100000113')
    # s=o.find_concept_data('1100000111')
    # print(s)

    # s=o.find_concept_term('三星用户')
    # print(s)
    # print(dd)

    # dd=o.find_concepts_with_rel('21000000003')
    # o.delete_concept_data('1100000113')

    # o.insert_rel_of_concept("1000000028", 'newrel', 'relval')
    # o.delete_rel_of_concept("1000000028", 'newrel')
    # o.delete_rel_val_of_concept("1000000028", 'newrel', 'relval')
    # o.update_rel_of_concept("1000000028", 'relval', 'newrel')
    # o.update_val_of_rel_concept("1000000028", 'newrel', 'relval', 'val')
    # o.update_cid_of_concept('newid',"1000000012")
    # s=o.find_concept_data('1000000012')
    # dd=o.get_id('relid')

    # print(dd)

    # o.put_id('relid', '2100000033')
    # s=o.find_concept_data('1100000111')
    # print(s)
    # d={'d1':[2],'d2':[3]}
    # t.find_all()
    # t.insert_key_value('cid','1001')
    # print(t.find_key_value('cid','1001')[0])
    # t.insert_key_value_of_rec('cid', '1001', 'test',4)
    # t.update_key_of_rec('cid','1001', 't', 'e')
    # t.insert_dict_of_rec(d)
    # print(t.find_key_value('cid','1001')[0])

    print('ok')
