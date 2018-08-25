$(function() {
	//渲染表格
	layui.table.render({
		elem : '#table',
		url : 'api/entity',
 		where: {
	  		token : getToken()
		},
		page: true,
		cols: [[
			{type:'numbers'},
			{field:'id', sort: true, title: '实体ID'},
			{field:'name', sort: true, title: '实体名'},
			{field:'des', sort: true, title: '实体描述'},
			{field:'concept', sort: true, title: '上位概念'},
			{field:'type', sort: true,title: '类型'},
			{align:'center', toolbar: '#barTpl', minWidth: 180, title: '操作'}
    	]]
	});
	
	//添加按钮点击事件
	$("#addBtn").click(function(){
		showEditModel(null);
	});

	$("#batchBtn").click(function(){
		UploadModel(null);
	});
	
	//表单提交事件
	layui.form.on('submit(btnSubmit)', function(data) {
		data.field.token = getToken();
		data.field._method = $("#editForm").attr("method");
		layer.load(1);
		$.post("api/entity", data.field, function(data){
			layer.closeAll('loading');
			if(data.code==200){
				layer.msg(data.msg,{icon: 1});
				layer.closeAll('page');
				layui.table.reload('table', {});
			}else{
				layer.msg(data.msg,{icon: 2});
			}
		}, "JSON");
		return false;
	});
	
	//工具条点击事件
	layui.table.on('tool(table)', function(obj){
		var data = obj.data;
		var layEvent = obj.event;
 
		if(layEvent === 'edit'){ //修改
			showEditModel(data);
		} else if(layEvent === 'del'){ //删除
			doDelete(obj);
		} else if(layEvent === 'reset'){ //重置密码
			doReSet(obj.data.userId);
		}
	});
	
	//监听状态开关操作
	layui.form.on('switch(statusCB)', function(obj){
		updateStatus(obj);
	});
	
	//搜索按钮点击事件
	$("#searchBtn").click(function(){
		doSearch(table);
	});
});

//显示表单弹窗
function showEditModel(data){
	layer.open({
		type: 1,
		title: data==null?"添加实体":"修改实体",
		area: '450px',
		offset: '120px',
		content: $("#addModel").html()
	});
	$("#editForm")[0].reset();
	$("#editForm").attr("method","POST");
//	var selectItem = "";
	if(data!=null){
//	    alert(data.name)
		$("#editForm input[name=entityname]").val(data.name);
		$("#editForm input[name=entitydes]").val(data.des);
		$("#editForm input[name=concept]").val(data.concept);
		$("#editForm input[name=category]").val(data.type);
		$("#editForm").attr("method","PUT");
//		selectItem = data.roleId;
		layui.form.render('radio');
	}
	$("#btnCancel").click(function(){
		layer.closeAll('page');
	});
	
//	getRoles(selectItem);
}

function UploadModel(data){
	layer.open({
		type: 1,
		title: "上传文件",
		area: '450px',
		offset: '120px',
		content: $("#batchAddModel").html()
	});
	$("#batchForm")[0].reset();
	$("#editForm").attr("method","POST");
}
//获取所有角色
//var roles = null;
//function getRoles(selectItem){
//	if(roles!=null) {
//		layui.laytpl(rolesSelect.innerHTML).render(roles, function(html){
//			$("#role-select").html(html);
//			$("#role-select").val(selectItem);
//			layui.form.render('select');
//			layer.closeAll('loading');
//		});
//	}else{
//		layer.load(1);
//		$.get("api/role",{
//			token: getToken(),
//			isDelete: 0
//		}, function(data){
//			if(0==data.code){
//				roles = data.data;
//				getRoles(selectItem);
//			}
//		});
//	}
//}

//删除
function doDelete(obj){
	layer.confirm('确定要删除吗？', function(index){
		layer.close(index);
		layer.load(1);
		$.ajax({
			url: "api/entity/"+obj.data.id,
			type: "DELETE", 
			dataType: "JSON", 
			success: function(data){
				layer.closeAll('loading');
				if(data.code==200){
					layer.msg(data.msg,{icon: 1});
					obj.del();
				}else{
					layer.msg(data.msg,{icon: 2});
				}
			}
		});
	});
}

//更改状态
function updateStatus(obj){
	layer.load(1);
	var newStatus = obj.elem.checked?0:1;
	$.post("api/entity", {
		userId: obj.elem.value,
		status: newStatus,
		_method: "PUT",
		token: getToken()
	}, function(data){
		layer.closeAll('loading');
		if(data.code==200){
			layui.table.reload('table', {});
		}else{
			layer.msg(data.msg,{icon: 2});
			layui.table.reload('table', {});
		}
	});
}

//搜索
function doSearch(table){
	var key = $("#searchKey").val();
	var value = $("#searchValue").val();
	if (value=='') {
		key = '';
	}
	layui.table.reload('table', {where: {searchKey: key,searchValue: value}});
}

//删除
//function doReSet(userId){
//	layer.confirm('确定要重置密码吗？', function(index){
//		layer.close(index);
//		layer.load(1);
//		$.post("api/user/psw/"+userId, {
//			token: getToken(),
//			_method: "PUT"
//		}, function(data){
//			layer.closeAll('loading');
//			if(data.code==200){
//				layer.msg(data.msg,{icon: 1});
//			}else{
//				layer.msg(data.msg,{icon: 2});
//			}
//		},"JSON");
//	});
//}