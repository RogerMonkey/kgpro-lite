import tornado.web
import json


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', script='''{{#  layui.each(d, function(index, item){ }}
		<li class="layui-nav-item">
			<a class="" href="javascript:openNavItem();"><i class="layui-icon">{{ item.permissionIcon }}</i>&emsp;<span>{{ item.permissionName }}</span></a>
			<dl class="layui-nav-child">
				{{#  layui.each(item.subMenus, function(index, subItem){ }}
				<dd>
					<a href="#!{{ subItem.permissionValue }}">{{ subItem.permissionName }}</a>
				</dd>
				{{#  }); }}
			</dl>
		</li>
		{{#  }); }}''')


class LoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")


class Login2Handler(tornado.web.RequestHandler):
    def post(self):
        self.write('{"msg":"登录成功","code":200,"user":{"userId":"11","userAccount":"test",'
                   '"userPassword":null,"userNickname":"test","mobilePhone":"11111111111","sex":"男",'
                   '"userStatus":0,"createTime":1518529355000,"updateTime":1519482665000,"roleId":"user",'
                   '"token":"111","roleName":"普通"},'
                   '"token":"testkg"}')


class MenuHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write(
            json.dumps(
                {"msg": "操作成功！", "code": 200,
                 "menus": [
                     {"permissionId": "1", "parentId": "0", "permissionName": "知识图谱管理", "permissionValue": None,
                      "createTime": 1491630166000, "updateTime": 1519349730000, "isDelete": 0,
                      "permissionIcon": "&#xe716;",
                      "orderNumber": 0, "permissionType": 0, "parentName": None, "subMenus": [
                         {"permissionId": "11", "parentId": "1", "permissionName": "实体管理",
                          "permissionValue": "system/qentity", "createTime": 1491630863000, "updateTime": 1518608238000,
                          "isDelete": 0,
                          "permissionIcon": None, "orderNumber": 1, "permissionType": 0, "parentName": None,
                          "subMenus": None},
                         {"permissionId": "12", "parentId": "1", "permissionName": "三元组管理",
                          "permissionValue": "system/qtriple", "createTime": 1492231672000, "updateTime": 1519349737000,
                          "isDelete": 0,
                          "permissionIcon": None, "orderNumber": 2, "permissionType": 0, "parentName": None,
                          "subMenus": None},
                         {"permissionId": "13", "parentId": "1", "permissionName": "模型管理",
                          "permissionValue": "system/qmodel", "createTime": 1492147082000,
                          "updateTime": 1519349742000,
                          "isDelete": 0, "permissionIcon": None, "orderNumber": 3, "permissionType": 0,
                          "parentName": None,
                          "subMenus": None}
                     ]},

                     {"permissionId": "2", "parentId": "0", "permissionName": "知识图谱应用",
                      "createTime": 1491630166000, "updateTime": 1519349730000, "isDelete": 0,
                      "permissionValue": None,
                      "permissionIcon": "&#xe631;",
                      "orderNumber": 0, "permissionType": 0, "parentName": None, "subMenus": [
                         {"permissionId": "3", "parentId": "2", "permissionName": "知识图谱清洗",
                          "createTime": 1491630166000, "updateTime": 1519349730000, "isDelete": 0,
                          "permissionIcon": None, "permissionValue": "system/clean",
                          "orderNumber": 0, "permissionType": 0, "parentName": None, "subMenus": None},
                         {"permissionId": "22", "parentId": "2", "permissionName": "知识图谱补全",
                          "createTime": 1491630166000, "updateTime": 1519349730000, "isDelete": 0,
                          "permissionIcon": None, "permissionValue": "system/completion",
                          "orderNumber": 0, "permissionType": 0, "parentName": None, "subMenus": None}
                     ]},

                     {"permissionId": "3", "parentId": "0", "permissionName": "知识图谱查询",
                      "createTime": 1491630166000, "updateTime": 1519349730000, "isDelete": 0,
                      "permissionValue": None,
                      "permissionIcon": "&#xe615;",
                      "orderNumber": 0, "permissionType": 0, "parentName": None, "subMenus": [
                         {"permissionId": "31", "parentId": "3", "permissionName": "实体查询",
                          "permissionValue": "system/entity", "createTime": 1491630863000, "updateTime": 1518608238000,
                          "isDelete": 0,
                          "permissionIcon": None, "orderNumber": 3, "permissionType": 0, "parentName": None,
                          "subMenus": None},
                         {"permissionId": "32", "parentId": "3", "permissionName": "三元组查询",
                          "permissionValue": "system/triple", "createTime": 1492231672000, "updateTime": 1519349737000,
                          "isDelete": 0,
                          "permissionIcon": None, "orderNumber": 4, "permissionType": 0, "parentName": None,
                          "subMenus": None}
                     ]}
                 ]})
        )
