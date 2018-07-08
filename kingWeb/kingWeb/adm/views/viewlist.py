from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpRequest
from django.db.models import Q
import json
import time
from kingWeb.DynamicRouter import urls
from kingWeb.models import *
from kingWeb.util.sqlhelper import *
from kingWeb.util.syshelper import *
def index(request,kwargs):
    assert isinstance(request, HttpRequest)
    tableid = kwargs.get('id','')
    table_desc = ''
    columns = None
    table = None
    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowview != 1:
            return render(request,'/adm/home/error.html')
        table_desc = table.description
        tablecolumns = list(SysTableColumn.objects.filter(Q(tableid=int(tableid)) & Q(listvisible=1)))
    return render(request,
        'adm/viewlist/index.html',
        {
            'title':table_desc + '管理',
            'tablecolumns':tablecolumns,
            'tableid':tableid,
            'table':table
        })

def add(request,kwargs):
    assert isinstance(request, HttpRequest)
    tableid = kwargs.get('id','')
    columns = None
    table = None
    enum_col_data = {}
    out_col_data = {}
    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowadd != 1:
            return render(request,'/adm/home/error.html')
        table_desc = table.description
        tablecolumns = list(SysTableColumn.objects.filter(Q(tableid=int(tableid)) & Q(addvisible=1)))
    for col in tablecolumns:
        if col.datatype == 'out':
            outdata_arr = col.outsql.split('|') #Example: Id,Name|Sys_Department|ParentId=0
            colnames = outdata_arr[0].split(',') # value,text
            tablename = outdata_arr[1]
            condition = outdata_arr[2]
            primarkey = colnames[0] #作为下拉菜单value的列
            textkey = colnames[1] #作为下拉菜单的text的列
            outdatalist = sqlhelper.query('select {0} from {1} where {2}'.\
                format(outdata_arr[0],tablename,condition))
            out_col_data[col.name] = outdatalist
        elif col.datatype == 'enum':
            enumdata = col.enumrange.split(',')
            enumlist = []
            for e in enumdata:
               enumlist.append(e)
            enum_col_data[col.name] = enumlist


    return render(request,
        'adm/viewlist/add.html',
        {
            'title':'添加' + table.description,
            'tablecolumns':tablecolumns,
            'tableid':tableid,
            'table':table,
            'enum_col_data':enum_col_data,
            'out_col_data':out_col_data,
        })

def detail(request,kwargs):
    assert isinstance(request, HttpRequest)
    id = kwargs.get('id','')
    tableid = kwargs.get('value','')
    if tableid == '' or id == '':
        return render(request, 'adm/viewlist/index')
    tablecolumns = None
    table = None
    out_col_data = {}
    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowview != 1:
              return HttpResponse(json.dumps(result.tojson()), content_type="application/json")
        tablecolumns = list(SysTableColumn.objects.filter(Q(tableid=int(tableid)) & Q(viewvisible=1)))
    columnnames = syshelper.get_column_names(tableid, "viewvisible=1", "ListOrder")
    data = sqlhelper.query('select {0} from {1} where {2}'\
        .format(columnnames,table.name,'Id=' + str(id)))[0]
    for col in tablecolumns:
        if col.datatype == 'out':
            outdata_arr = col.outsql.split('|') #Example: Id,Name|Sys_Department|ParentId=0
            colnames = outdata_arr[0].split(',') # value,text
            tablename = outdata_arr[1]
            condition = outdata_arr[2]
            primarkey = colnames[0] #作为下拉菜单value的列
            textkey = colnames[1] #作为下拉菜单的text的列
            outvalue = sqlhelper.query('select {0} from {1} where {2}'.\
                format(outdata_arr[0],tablename,'Id=' + str(data[col.name])))
            out_col_data[col.name] = outvalue

    return render(request,
        'adm/viewlist/detail.html',
        {
            'id':id,
            'title': table.description + '详情',
            'tablecolumns':tablecolumns,
            'tableid':tableid,
            'table':table,
            'out_col_data':out_col_data,
            'data':data,
        })

def edit(request,kwargs):
    assert isinstance(request, HttpRequest)
    id = kwargs.get('id','')
    tableid = kwargs.get('value','')
    if tableid == '' or id == '':
        return render(request, 'adm/viewlist/index')
    tablecolumns = None
    table = None
    enum_col_data = {}
    out_col_data = {}
    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowedit != 1:
              return HttpResponse(json.dumps(result.tojson()), content_type="application/json")
        tablecolumns = list(SysTableColumn.objects.filter(Q(tableid=int(tableid)) & Q(editvisible=1)))
    columnnames = syshelper.get_column_names(tableid, "EditVisible=1", "ListOrder")
    data = sqlhelper.query('select {0} from {1} where {2}'\
        .format(columnnames,table.name,'Id=' + str(id)))[0]
    for col in tablecolumns:
        if col.datatype == 'out':
            outdata_arr = col.outsql.split('|') #Example: Id,Name|Sys_Department|ParentId=0
            colnames = outdata_arr[0].split(',') # value,text
            tablename = outdata_arr[1]
            condition = outdata_arr[2]
            primarkey = colnames[0] #作为下拉菜单value的列
            textkey = colnames[1] #作为下拉菜单的text的列
            outdatalist = sqlhelper.query('select {0} from {1} where {2}'.\
                format(outdata_arr[0],tablename,condition))
            out_col_data[col.name] = outdatalist
        elif col.datatype == 'enum':
            enumdata = col.enumrange.split(',')
            enumlist = []
            for e in enumdata:
               enumlist.append(e)
            enum_col_data[col.name] = enumlist

    return render(request,
        'adm/viewlist/edit.html',
        {
            'id':id,
            'title':'编辑' + table.description,
            'tablecolumns':tablecolumns,
            'tableid':tableid,
            'table':table,
            'enum_col_data':enum_col_data,
            'out_col_data':out_col_data,
            'data':data,
        })

@csrf_exempt
def post_add(request,kwargs):
    assert isinstance(request, HttpRequest)
    result = ResultModel()
    formdata = request.POST.dict()
    tableid = kwargs.get('id','')
    tablecolumns = None
    table = None
    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowadd != 1:
              return HttpResponse(json.dumps(result.tojson()), content_type="application/json")
        tablecolumns = list(SysTableColumn.objects.filter(Q(tableid=int(tableid)) & Q(addvisible=1)))
    addmodel = {}
    for col in tablecolumns:
        if col.name in formdata.keys():
            addmodel[col.name] = formdata.get(col.name,'')
    addmodel['CreateDateTime'] = time.strftime("%Y-%m-%d %H:%M:%S")
    addmodel['ModifyDateTime'] = time.strftime("%Y-%m-%d %H:%M:%S")
    addmodel['Creator'] = str(request.user.id)
    addmodel['Modifier'] = str(request.user.id)
    sql = 'insert into {0}({1}) values({2})'
    sql = sql.format(table.name,\
        ','.join(addmodel.keys()),\
        "'" + ','.join(addmodel.values()).replace(',' , "','") + "'")
    sqlhelper.execute(sql)
    result.msg = '操作成功'
    result.flag = True
    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

@csrf_exempt
def post_edit(request,kwargs):
    assert isinstance(request, HttpRequest)
    result = ResultModel()
    formdata = request.POST.dict()
    id = kwargs.get('id','')
    tableid = kwargs.get('value','')
    tablecolumns = None
    table = None
    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowedit != 1:
              return HttpResponse(json.dumps(result.tojson()), content_type="application/json")
        update_filter = SysTableList.objects.get(id=int(tableid)).forbiddenupdatefilter
        condition = '1=1'
        if forbidden_delete_filter != '':
            condition = update_filter
        tablecolumns = list(SysTableColumn.objects.filter(Q(tableid=int(tableid)) & Q(editvisible=1)))
    editmodel = {}
    for col in tablecolumns:
        if col.name in formdata.keys():
            editmodel[col.name] = formdata.get(col.name,'')

    editmodel['ModifyDateTime'] = time.strftime("%Y-%m-%d %H:%M:%S")
    editmodel['Modifier'] = str(request.user.id)
    sql = 'update {0} set {1} where {2}'
    newvalues = ''
    for key,value in editmodel.items():
        newvalues += "{0}='{1}',".format(key,value)
    newvalues = newvalues.rstrip(',')
    sql = sql.format(table.name,newvalues,'Id=' + str(id) + ' and ' + condition)
    sqlhelper.execute(sql)
    result.msg = '操作成功'
    result.flag = True
    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

@csrf_exempt
def post_delete(request,kwargs):
    result = ResultModel()
    assert isinstance(request, HttpRequest)
    ids = request.POST.getlist('ids[]')
    tableid = request.POST.get('value','')
    forbidden_delete_filter = SysTableList.objects.get(id=int(tableid)).forbiddendeletefilter
    condition = '1=1'
    if forbidden_delete_filter != '':
        condition = forbidden_delete_filter
    if len(ids) <= 0:
        result.msg = '操作失败'
        return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

    if tableid != '':
        table = SysTableList.objects.get(id=int(tableid))
        if table.allowdelete != 1:
              return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

    sqllist = []
    for id in ids:
        sqllist.append('delete from {0} where {1}'.format(table.name,'Id=' + str(id) + ' and ' + condition))
    sqlhelper.bulk_execute(sqllist)
    result.msg = '操作成功'
    result.flag = True
    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")


@csrf_exempt
def get_page_data(request,kwargs):
    assert isinstance(request, HttpRequest)
    start = request.POST.get('start','0')
    length = request.POST.get('length','0')
    searchkey = request.POST.get('searchKey','')
    orderby = request.POST.get('orderBy','')
    orderdir = request.POST.get('orderDir','')
    draw = request.POST.get('draw','')
    tableid = request.POST.get('value','')

    table = SysTableList.objects.get(id=tableid)
    if table.allowview != 1:
        return HttpResponse('', content_type="application/json")

    _orderby = ''
    if orderdir == 'desc':
        _orderby = '-'

    if orderby != '':
        _orderby +=orderby
    elif table.defaultsort != '':
        _orderby +=table.defaultsort
    else:
        _orderby +='id'

    condition = '1=1'
    alldata = None
    if searchkey != '':
       search_columns = syshelper.get_column_names(tableid, "SearchVisible=1", "ListOrder").split(',')
       condition = ''
       for sc in search_columns:
           condition+=" {0} like '%{1}%' or".format(sc,searchkey)
       condition = '(' + condition.rstrip('or') + ')'

    if table.defaultfilter != '':
        condition += ' and ' + table.defaultfilter

    sql = 'select {0} from {1} where {2} order by {3} limit {4},{5}'
    list_columns = syshelper.get_column_names(tableid, "ListVisible=1", "ListOrder")
    pagedata = sqlhelper.query(sql.format(list_columns,table.name,condition,_orderby,start,length))
    data_count = sqlhelper.single('select count(*) from {0} where {1}'.format(table.name, condition))
    out_type_column_names = syshelper.get_column_names(tableid, "ListVisible=1 and DataType='out'", "ListOrder").split(',')

    rownum = int(start)
    for dic in pagedata:
        rownum = rownum + 1
        dic['rownum'] = rownum
        for key in dic:
            if key in out_type_column_names:
                dic[key] = syshelper.get_out_value(tableid,key,dic[key])
            else:
                if key == 'CreateDateTime' or key == 'ModifyDateTime':
                    dic[key] = str(dic[key])
        if table.extendfunction != '':
            dic['ExtendFunction'] = table.extendfunction.replace('{Id}',str(dic['Id'])).replace('{UserId}',str(request.user.id))

    datatable = DataTableModel(draw,data_count,data_count,pagedata)

    return HttpResponse(json.dumps(datatable.tojson()), content_type="application/json")

def post_import(request,kwargs):
    assert isinstance(request, HttpRequest)
    tableid = request.POST.get('tableid','')
    file = request.FILES['excelFile']
    result = syshelper.import_excel(tableid,file)
    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")


def post_export(request,kwargs):
    assert isinstance(request, HttpRequest)
    tableid = request.POST.get('tableid','')
    result = syshelper.export_excel(tableid)

    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

def download_import_template(request,kwargs):
    assert isinstance(request, HttpRequest)
    tableid = request.POST.get('tableid','')
    result = syshelper.download_import_template(tableid)

    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")