# -*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings
from bearychat.models import Subscribe
from weixin.models import User, New, Message
from utils.tianqi import weather
import requests
import json
from datetime import datetime
# trial for bearychat InComing Robot
# Create your views here.
def ingo(request):
    #method1 post json to the server
    payload = {"text": "caohai123",
               "attachments": [{"title": "Star Wars III", "text": "Return of the Jedi", "color": "#ffa500"}]}
    headers = {'content=type': 'application/json'}
    r = requests.post(settings.BC_WEBHOOK, json=payload, headers=headers)
    if r.ok:
        return render_to_response("index.html")

        #method2 post payload form data to server
        # data = {"payload": '{"text":"haha"}'}
        # session = requests.Session()
        # r2 = session.post(url=settings.BC_WEBHOOK, data=data)
        # print r2
        # if r2.ok:
        #     return render_to_response("index.html")


#trial for bearychat OutComing Robot
@csrf_exempt
def outcome(request):
    bcdata = json.loads(request.body)
    print bcdata
    print bcdata['text'], bcdata['user_name'], bcdata['trigger_word'], bcdata['token'], bcdata['ts'], bcdata[
        'channel_name']
    message = '输入有误，请输入justpic help继续操作'
    print type(bcdata['text'])
    if bcdata['text'].startswith('justpic'):
        cmd = bcdata['text'].split()
        if len(cmd) > 1 and cmd[1] == 'sub':
            #store the bearychat room info: subscribe info
            if len(cmd) > 2:
                try:
                    sub = Subscribe.objects.get(token=bcdata['token'])
                    if sub is not None:
                        message = '已订阅推送，请尝试其他操作'
                except Exception, e:
                    sub = Subscribe(
                        username=bcdata['user_name'],
                        channel=bcdata['channel_name'],
                        url=cmd[2],
                        token=bcdata['token']
                    )
                    sub.save()
                    message = '订阅推送成功！'
            else:
                message = '命令justpic sub <incoming url>！'
        elif len(cmd) > 1 and cmd[1] == 'cancel':
            Subscribe.objects.filter(username=bcdata['user_name'], channel=bcdata['channel_name'],
                                     token=bcdata['token']).delete()
            message = '取消推送成功'
        elif len(cmd) > 1 and cmd[1] == 'wx':
            message = 'justpic wx users--显示微信关注用户  justpic wx news--显示微信推送消息 ' \
                      'justpic wx message <userid>--显示特定用户发送的消息 ' \
                      'justpic wx pub <title> <description> <picurl> <url>--发布微信新闻消息'
            if len(cmd) > 2 and cmd[2] == 'users':
                users = User.objects.all()
                usernames = [item.FromUserName for item in users]
                message = ','.join(usernames)
            elif len(cmd) > 2 and cmd[2] == 'news':
                news = New.objects.order_by('-Chuangjianshijian')
                i = 0
                mess = ""
                for new in news:
                    if i > 5:
                        break
                    new.Title, new.PicUrl, new.Url, new.Description
                    mess += new.Title + " [![pic](" + new.PicUrl + ")](" + new.Url + ") ;"
                message = mess if mess != "" else message
            elif len(cmd) > 2 and cmd[2] == 'pub':
                try:
                    new = New(
                        Title=cmd[3],
                        Description=cmd[4],
                        PicUrl=cmd[5],
                        Url=cmd[6],
                        Chuangjianshijian=datetime.now())
                    new.save()
                    message = "新闻发送成功"
                except Exception, e:
                    print e
                    message = "新闻发送失败，更正后重新发送"
            else:
                message = "输入justpic wx查看相关功能"

        elif len(cmd) > 1 and cmd[1] == 'weather':
            city = cmd[2] if len(cmd) > 2 else '重庆'
            message = weather(city)
        elif len(cmd) > 1 and cmd[1] == 'help':
            message = 'justpic sub <incomgin url>--订阅推送  justpic cancel--取消订阅推送  justpic wx--微信公众号管理  justpic weather <city>--天气预报'
        else:
            message = '输入有误，请输入justpic help查看帮助'
    elif 'help' in bcdata['text']:
        message = 'help message'
    else:
        message = "目前仅支持justpic，请输入" + str(bcdata['text']) + " help查看帮助"
    data = {"text": message, "markdown": True,
            "attachments": [{"title": "", "text": "Cool,Attachments supported in Outcoming robot", "color": "#ffa500"}]}
    data = {"text": message, "markdown": True,
            "attachments": [{"title": "Star Wars III", "text": "Return of the Jedi", "color": "#ffa500"}]}
    return HttpResponse(json.dumps(data))
