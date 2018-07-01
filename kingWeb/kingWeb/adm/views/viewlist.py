from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpRequest
from django.db.models import Q
import json
from kingWeb.DynamicRouter import urls
from kingWeb.models import *
from kingWeb.contrib.sqlhelper import *
from kingWeb.contrib.syshelper import *
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
    return render(request,
        'adm/viewlist/add.html',
        {
            'title':'添加XX',
        })

def detail(request,kwargs):
    assert isinstance(request, HttpRequest)
    return render(request,
        'adm/viewlist/add.html',
        {
            'title':'添加XX',
        })

def edit(request,kwargs):
    assert isinstance(request, HttpRequest)
    id = kwargs.get('id','')
    if id == '':
        return render(request, 'adm/viewlist/index')
    object = SysModule.objects.get(id=id)
    return render(request,
        'adm/viewlist/edit.html',
        {
            'title':'编辑XX',
            'id':object.id,
            'name':object.name,
            'description':object.description,
        })

@csrf_exempt
def post_add(request,kwargs):
    assert isinstance(request, HttpRequest)
    result = ResultModel()
    name = request.POST.get('Name','')
    description = request.POST.get('Description','')
    object = SysModule.objects.create(name=name,description=description)
    result.msg = '操作成功'
    result.flag = True
    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

@csrf_exempt
def post_edit(request,kwargs):
    assert isinstance(request, HttpRequest)
    result = ResultModel()
    id = request.POST.get('Id','')
    name = request.POST.get('Name','')
    description = request.POST.get('Description','')
    object = SysModule.objects.filter(id=id).update(name=name,description=description)
    result.msg = '操作成功'
    result.flag = True
    return HttpResponse(json.dumps(result.tojson()), content_type="application/json")

@csrf_exempt
def post_delete(request,kwargs):
    result = ResultModel()
    assert isinstance(request, HttpRequest)
    ids = request.POST.getlist('ids[]')
    if ids == '':
        result.msg = '操作失败'
        return HttpResponse(json.dumps(result.tojson()), content_type="application/json")
    object = SysModule.objects.filter(id__in=ids).delete()
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

    table = SysTableList.objects.get(table)
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
       for sc in search_columns:
           condition+=" {0} like '%{1}%' or".format(sc,searchkey)
       condition = '(' + condition.rstrip('or') + ')'

    if table.defaultfilter != '':
        condition +=' and ' + table.defaultfilter

    sql = 'select {0} from {1} where {2} order by {3} limit {4},{5}'
    list_columns = syshelper.get_column_names(tableid, "ListVisible=1", "ListOrder").split(',')
    pagedata = sqlhelper.query(sql.format(list_columns,table.name,condition,orderby,start,length))
    data_count = sqlhelper.single('select count(*) from {0} where {1}'.format(table.name, condition))
    out_type_column_names = syshelper.get_column_names(tableid, "ListVisible=1 and DataType='out'", "ListOrder").split(',')

    rownum = int(start)
    for dic in pagedata:
        rownum = rownum + 1
        row['rownum'] = rownum
        for key in dic:
            if key in out_type_column_names:
                dic[key]  = syshelper.get_out_value(tableid,key,dic[key])
            else:
                if key == 'CreateDateTime':
                    dic[key] = str(dic[key])
        if table.extendfunction !='':
            dic['ExtendFunction'] = table.extendfunction.replace('{Id}',dic['Id']).replace('{UserId}',request.user.id)

    datatable = DataTableModel(draw,data_count,data_count,pagedata)

    return HttpResponse(json.dumps(datatable.tojson()), content_type="application/json")

def post_import(request,kwargs):
    assert isinstance(request, HttpRequest)
    return render(request,
        'adm/viewlist/add.html',
        {
            'title':'添加XX',
        })
def post_export(request,kwargs):
    assert isinstance(request, HttpRequest)
    return render(request,
        'adm/viewlist/add.html',
        {
            'title':'添加XX',
        })

def download_import_template(request,kwargs):
    assert isinstance(request, HttpRequest)
    return render(request,
        'adm/viewlist/add.html',
        {
            'title':'添加XX',
        })
