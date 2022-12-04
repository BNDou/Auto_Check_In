'''
new Env('小米社区日常')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-12-03 16:58:45
LastEditTime : 2022-12-04 22:01:49
FilePath     : /Auto_Check_In/checkIn_XiaoMiClub.py
Description  : 
添加环境变量COOKIE_XIAOMICLUB，多账号用回车换行分开
建议手机端访问签到页面时抓cookie
电脑端的随便访问一个帖子时抓到的才可以用，其他页面的不行
cookie有效期不清楚，包含字段：miui_vip_serviceToken、cUserId
在抓到的cookie后面多加一个字段 userId 并赋上值（小米ID）
格式如下：miui_vip_serviceToken=***; cUserId=***; userId=***;
'''

from lxml import etree
import requests
import time
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()


# 获取环境变量
def get_env():
    # 判断 COOKIE_XIAOMICLUB是否存在于环境变量
    if "COOKIE_XIAOMICLUB" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_XIAOMICLUB').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_XIAOMICLUB变量未启用')
            send('小米社区日常', 'COOKIE_XIAOMICLUB变量未启用')
            # 脚本退出
            sys.exit(0)
    else:
        # 标准日志输出
        print('未添加COOKIE_XIAOMICLUB变量\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
        send('小米社区日常', '未添加COOKIE_XIAOMICLUB变量\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
        # 脚本退出
        sys.exit(0)

    return cookie_list


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


def run(cookie, url):
    # 延迟5秒执行，防止频繁
    time.sleep(5)
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/106.0.0.0'})
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/106.0.0.0',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cookie': cookie.replace(' ', '')
    }
    data = {'action': 'BROWSE_POST_10S', 'pathname': '/mio/detail', 'version': 'dev.20001', 'miui_version': 'undefined', 'android_version': 'undefined',
            'oaid': 'false', 'device': '', 'restrict_imei': '', 'miui_big_version': '', 'model': '', 'androidVersion': 'undefined', 'miuiBigVersion': ''}

    r = s.get(url=url, data=data, headers=headers, timeout=120)
    a = r.json()

    if 'code' in a:
        if a.get('code') in (401, 500):
            print(
                '失败，可能是cookie失效了\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
            send(
                '小米社区日常', '失败，可能是cookie失效了\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
            # 脚本退出
            sys.exit(0)

    msg += a.get('message', '')
    if 'entity' in a:
        if 'desc' in a.get('entity'):
            msg += a.get('entity').get('desc', '')
        if 'title' in a.get('entity'):
            msg += a.get('entity').get('title', '')

    return msg + '\n'


def main(*arg):
    msg = ''
    sendnoty = 'true'
    global cookie_xiaomiclub
    # 签到
    checkin_url = 'https://api.vip.miui.com/mtop/planet/vip/user/checkin?ref=vipAccountShortcut&pathname=/mio/checkIn&version=dev.221116&miui_version=V13.0.5.1.47.DEV&android_version=12&oaid=e8f4a0444d8fb4d2&device=umi&restrict_imei=&miui_big_version=V130&model=Mi%2010&androidVersion=12&miuiBigVersion=V130'
    # 浏览帖子*3
    browse_url1 = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?action=BROWSE_POST_10S&pathname=/mio/detail&version=dev.20001&miui_version=undefined&android_version=undefined&oaid=false&device=&restrict_imei=&miui_big_version=&model=&androidVersion=undefined&miuiBigVersion=&userId='
    # 浏览专题页*1
    browse_url2 = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?action=BROWSE_SPECIAL_PAGES_SPECIAL_PAGE&ref=vipAccountShortcut&pathname=/mio/subject&version=dev.221116&miui_version=V13.0.5.1.47.DEV&android_version=12&oaid=e8f4a0444d8fb4d2&device=umi&restrict_imei=&miui_big_version=V130&model=Mi%2010&androidVersion=12&miuiBigVersion=V130&userId='
    # 浏览个人页*1
    browse_url3 = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?action=BROWSE_SPECIAL_PAGES_USER_HOME&ref=vipAccountShortcut&pathname=/mio/homePage&version=dev.221116&miui_version=V13.0.5.1.47.DEV&android_version=12&oaid=e8f4a0444d8fb4d2&device=umi&restrict_imei=&miui_big_version=V130&model=Mi%2010&androidVersion=12&miuiBigVersion=V130&userId='
    # 加入MIUI综合讨论圈子
    join_miui = 'https://api.vip.miui.com/api/community/board/follow?boardId=558495&ref=communityGrowUp&pathname=/mio/singleBoard&version=dev.221116&miui_version=V13.0.5.1.47.DEV&android_version=12&oaid=e8f4a0444d8fb4d2&device=umi&restrict_imei=&miui_big_version=V130&model=Mi%2010&androidVersion=12&miuiBigVersion=V130'
    # 获取cookie环境变量
    cookie_xiaomiclub = get_env()

    i = 0
    while i < len(cookie_xiaomiclub):
        # 获取小米id
        userId = cookie_xiaomiclub[i][cookie_xiaomiclub[i].find(
            'userId=')+7:].replace(';', '')

        msg += f"第 {i+1} 个账号{userId}开始执行任务\n"
        # 签到
        msg += '每日签到 ' + run(cookie_xiaomiclub[i], checkin_url)
        # 浏览帖子*3
        j = 0
        while j < 3:
            msg += f'浏览帖子{j+1} ' + \
                run(cookie_xiaomiclub[i], browse_url1 + userId)
            j += 1
        # 浏览专题页*1
        msg += '浏览专题页 ' + run(cookie_xiaomiclub[i], browse_url2 + userId)
        # 浏览个人页*1
        msg += '浏览个人页 ' + run(cookie_xiaomiclub[i], browse_url3 + userId)
        # 加入MIUI综合讨论圈子*1
        msg += '加入MIUI综合讨论圈子 ' + run(cookie_xiaomiclub[i], join_miui)

        i += 1

    print(msg[:-1])

    if sendnoty:
        try:
            send('小米社区日常', msg)
        except:
            send('小米社区日常', '错误，请查看运行日志！')

    return msg[:-1]


if __name__ == "__main__":
    print("----------小米社区开始执行----------")
    main()
    print("----------小米社区执行完毕----------")
