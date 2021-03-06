from django.shortcuts import render_to_response,redirect
from kingWeb.models import ResultModel,SysOperationLog
from django.http import HttpResponse,JsonResponse,HttpRequest
from kingWeb.util.WebHelper import WebHelper
from kingWeb.util.SysHelper import SysHelper
from kingWeb.util.LogHelper import LogHelper
import json
def process(request,**kwargs):
    '''接收所有匹配url的请求，根据请求url中的参数，通过反射动态指定view中的方法'''

    app = kwargs.get('app',None)
    controller = kwargs.get('controller',None)
    action = kwargs.get('action',None)

    ip = WebHelper.get_client_ip(request)
    agent = WebHelper.get_client_agent(request)
    user = request.user
    url = request.get_full_path()
    #POST请求就不写入日志了
    if request.method != 'POST':
        SysOperationLog.objects.create(clientip=ip,clientinfo = agent,username=user.username,operationdescription='访问',\
            operationurl = url)
    SysHelper.userid = str(user.id)
    try:
        viewObj = __import__("kingWeb.apps.%s.views" % (app,),fromlist=(controller,))
        ctrlObj = getattr(viewObj, controller)
        actionObj = getattr(ctrlObj, action)
        #执行view.py中的函数，并获取其返回值
        result = actionObj(request,kwargs)
        return result
    except(ImportError,AttributeError) as e:
        LogHelper.error(str(e))
        if request.method == 'POST':
            result = ResultModel()
            result.flag = False
            result.msg = '操作失败:' + str(e)
            return JsonResponse(result.tojson())
        else:
           return redirect('/adm/home/error')
    except Exception as e:
        LogHelper.error(str(e))
        if request.method == 'POST':
            result = ResultModel()
            result.flag = False
            result.msg = '操作失败:' + str(e)
            return JsonResponse(result.tojson())
        else:
            return redirect('/adm/home/error')

