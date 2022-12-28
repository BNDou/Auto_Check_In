'''
new Env('小米社区日常')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-12-03 16:58:45
LastEditTime : 2022-12-29 02:08:50
FilePath     : /Auto_Check_In/checkIn_XiaoMiClub.py
Description  : 
添加环境变量COOKIE_XIAOMICLUB，多账号用回车换行分开
建议手机端访问签到页面时抓cookie
电脑端的随便访问一个帖子时抓到的才可以用，其他页面的不行
cookie有效期好像是24小时，包含字段：miui_vip_serviceToken、cUserId
在抓到的cookie后面多加一个字段 userId 并赋上值（小米ID）
格式如下：miui_vip_serviceToken=***; cUserId=***; userId=***;
'''

import requests
import time
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_XIAOMICLUB'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


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


def run_get(cookie, url):
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

    r = s.get(url=url, headers=headers, timeout=120)
    a = r.json()

    if 'code' in a:
        if a.get('code') in (401, 500):
            print(msg +
                  '\n失败，可能是cookie失效了\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
            send(
                '小米社区日常', msg + '\n失败，可能是cookie失效了\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
            # 脚本退出
            sys.exit(0)

    msg += a.get('message', '')
    if 'entity' in a:
        if isinstance(a.get('entity'), dict):
            if 'desc' in a.get('entity'):
                msg += ' ' + a.get('entity').get('desc', '')
            if 'title' in a.get('entity'):
                msg += ' ' + a.get('entity').get('title', '')
        else:
            msg += ' ' + str(a.get('entity', ''))

    return msg


def run_post(cookie, url):
    # 延迟1秒执行，防止频繁
    time.sleep(1)
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/106.0.0.0'})
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1 Edg/106.0.0.0',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip',
        'Cookie': cookie.replace(' ', '')
    }
    data = {
        'postId': '35066013',
    }

    r = s.post(url=url, data=data, headers=headers, timeout=120)
    a = r.json()

    if 'code' in a:
        if a.get('code') in (401, 500):
            print(msg +
                  '\n失败，可能是cookie失效了\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
            send(
                '小米社区日常', msg + '\n失败，可能是cookie失效了\n建议手机端访问签到页面时抓cookie，其包含字段：miui_vip_serviceToken、cUserId、userId')
            # 脚本退出
            sys.exit(0)

    msg += a.get('message', '')

    return msg


def main(*arg):
    msg = ''
    sendnoty = 'true'
    global cookie_xiaomiclub
    # 签到
    checkin_url = 'https://api.vip.miui.com/mtop/planet/vip/user/checkin'
    # 浏览帖子*3
    browse_url1 = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?action=BROWSE_POST_10S&pathname=/mio/detail&oaid=false&userId='
    # 浏览专题页*1
    browse_url2 = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?action=BROWSE_SPECIAL_PAGES_SPECIAL_PAGE&pathname=/mio/subject&oaid=e8f4a0444d8fb4d2&userId='
    # 浏览个人页*1
    browse_url3 = 'https://api.vip.miui.com/mtop/planet/vip/member/addCommunityGrowUpPointByAction?action=BROWSE_SPECIAL_PAGES_USER_HOME&pathname=/mio/homePage&oaid=e8f4a0444d8fb4d2&userId='
    # 加入MIUI综合讨论圈子
    join_miui = 'https://api.vip.miui.com/api/community/board/follow?boardId=558495'
    # 点赞他人帖子*2
    thumb_up = 'https://api.vip.miui.com/mtop/planet/vip/content/'
    # 获取cookie环境变量
    cookie_xiaomiclub = get_env()

    i = 0
    while i < len(cookie_xiaomiclub):
        # 获取小米id
        userId = cookie_xiaomiclub[i][cookie_xiaomiclub[i].find(
            'userId=')+7:].replace(';', '')

        log = f"第 {i+1} 个账号{userId}开始执行任务"
        msg += log + '\n'
        print(log)
        # 签到
        log = '每日签到 ' + run_get(cookie_xiaomiclub[i], checkin_url)
        msg += log + '\n'
        print(log)
        # 浏览帖子*3
        for num in range(3):
            log = f'浏览帖子{num+1} ' + \
                run_get(cookie_xiaomiclub[i], browse_url1 + userId)
            msg += log + '\n'
            print(log)
        # 浏览专题页*1
        log = '浏览专题页 ' + run_get(cookie_xiaomiclub[i], browse_url2 + userId)
        msg += log + '\n'
        print(log)
        # 浏览个人页*1
        log = '浏览个人页 ' + run_get(cookie_xiaomiclub[i], browse_url3 + userId)
        msg += log + '\n'
        print(log)
        # 加入MIUI综合讨论圈子*1
        log = '加入MIUI综合讨论圈子 ' + run_get(cookie_xiaomiclub[i], join_miui)
        msg += log + '\n'
        print(log)
        # 点赞他人帖子*2
        for num in range(2):
            log = f'点赞他人帖子{num+1}次 ' + \
                run_post(cookie_xiaomiclub[i], thumb_up+'announceThumbUp')
            log += f' 取消点赞 ' + \
                run_post(cookie_xiaomiclub[i],
                         thumb_up+'announceCancelThumbUp')
            msg += log + '\n'
            print(log)
        msg += '\n'
        i += 1

    if sendnoty:
        try:
            send('小米社区日常', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('小米社区日常', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------小米社区开始执行----------")
    main()
    print("----------小米社区执行完毕----------")
