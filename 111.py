# tm1 = {}
# with open('history_smart_audit_result.data') as f:
#     for line in f.readlines():
#         it = line.strip().split('\t')
#         tm1[it[3]] = 1
#
# tm2 = {}
# with open('history_ad_shop_ctr_info.data.2018-07-30') as f:
#     for line in f.readlines():
#         it = line.strip().split('\001')
#         if it[0] not in tm2:
#             tm2[it[0]] = []
#         tm2[it[0]].append(it[3])
#
#
# cnt = 0
# cnt2 = 0
# nm1 = 0
# nm2 = 0
#
# print len(tm1), len(tm2)
# for key in tm2:
#     t = 0
#     for pic in tm2[key]:
#         if pic in tm1:
#             t += 1
#     if t > 0:
#         cnt += 1
#         nm1 += t
#         nm2 += len(tm2[key])
#         if t != len(tm2[key]):
#             cnt2 += 1
#
#
# print cnt, cnt2
# print nm1, nm2
