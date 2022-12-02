'''
new Env('掌上飞车签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime : 2022-12-02 20:17:47
FilePath     : \Auto_Check_In\checkIn_ZhangFei.py
Description  : 添加环境变量COOKIE_ZHANGFEI、URL_ZHANGFEI、REFERER_ZHANGFEI
'''
from lxml import etree
import requests
import json
import time
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()
try:
    from pusher import pusher
except:
    pass

# 获取环境变量
cookie_zhangfei = os.environ.get("COOKIE_ZHANGFEI")
url_zhangfei = os.environ.get("URL_ZHANGFEI")
referer_zhangfei = os.environ.get("REFERER_ZHANGFEI")


def load_send():
    global send
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        try:
            from sendNotify import send
        except:
            send = False
            print("加载通知服务失败~")
    else:
        send = False
        print("加载通知服务失败~")


load_send()


def run(*arg):
    msg = ""
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Mi 10 Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36 GH_QQConnect GameHelper_1003/2103040778'})

    # 签到
    url = url_zhangfei
    headers = {
        'Host': 'mwegame.qq.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Mi 10 Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36 GH_QQConnect GameHelper_1003/2103040778',
        'X-Requested-With': 'XMLHttpRequest',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': referer_zhangfei,
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie_zhangfei,
    }

    r = s.get(url, headers=headers, timeout=120)
    rjson = r.json()
    msg += rjson['message']

    return msg + '\n'


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    if "\\n" in cookie_zhangfei:
        clist = cookie_zhangfei.split("\\n")
    else:
        clist = cookie_zhangfei.split("\n")
    i = 0
    while i < len(clist):
        msg += f"第 {i+1} 个账号开始执行任务\n"
        cookie_zhangfei = clist[i]
        msg += run(cookie_zhangfei)
        i += 1
    print(msg[:-1])
    if sendnoty:
        try:
            send('掌上飞车签到', msg)
        except:
            send('掌上飞车签到', '错误，请查看运行日志！')
    return msg[:-1]


if __name__ == "__main__":
    if cookie_zhangfei:
        print("----------掌上飞车开始尝试签到----------")
        main()
        print("----------掌上飞车签到执行完毕----------")
