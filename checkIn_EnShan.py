'''
new Env('恩山论坛签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-10-30 22:21:48
LastEditTime : 2022-12-02 20:00:11
FilePath     : \Auto_Check_In\checkIn_EnShan.py
Description  : 添加环境变量COOKIE_ENSHAN
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

cookie = os.environ.get("COOKIE_ENSHAN")


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
    s.headers.update(
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'})

    # 签到
    url = "https://www.right.com.cn/forum/home.php?mod=spacecp&ac=credit&op=log&suboperation=creditrulelog"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Connection': 'keep-alive',
        'Cookie': cookie,
        'Host': 'www.right.com.cn',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0'
    }
    try:
        r = s.get(url, headers=headers, timeout=120)
        # print(r.text)
        if '每天登录' in r.text:
            h = etree.HTML(r.text)
            data = h.xpath('//tr/td[6]/text()')
            msg += f'签到成功或今日已签到，最后签到时间：{data[0]}'
        else:
            msg += '签到失败，可能是cookie失效了！'
            pusher(msg)
    except:
        msg = '无法正常连接到网站，请尝试改变网络环境，试下本地能不能跑脚本，或者换几个时间点执行脚本'
    return msg + '\n'


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie
    if "\\n" in cookie:
        clist = cookie.split("\\n")
    else:
        clist = cookie.split("\n")
    i = 0
    while i < len(clist):
        msg += f"第 {i+1} 个账号开始执行任务\n"
        cookie = clist[i]
        msg += run(cookie)
        i += 1
    print(msg[:-1])
    if sendnoty:
        try:
            send('恩山论坛签到', msg)
        except:
            send('恩山论坛签到', '错误，请查看运行日志！')
    return msg[:-1]


if __name__ == "__main__":
    if cookie:
        print("----------恩山论坛开始尝试签到----------")
        main()
        print("----------恩山论坛签到执行完毕----------")
