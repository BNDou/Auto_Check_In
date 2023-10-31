'''
new Env('掌上飞车签到')
cron: 10 0 * * *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime : 2023-11-01 2:26:10
FilePath     : /Auto_Check_In/checkIn_ZhangFei.py
Description  :
抓包流程：
(推荐)
开启抓包-进入签到页面-等待上方账号信息加载出来-停止抓包
选请求这个url的包-https://speed.qq.com/lbact/

(抓不到的话)
可以选择抓取其他页面的包，前提是下面7个值一个都不能少

添加环境变量COOKIE_ZHANGFEI，多账号用回车换行分开
只需要添加7个值即可，分别是
roleId=xxx; accessToken=xxx; appid=xxx; openid=xxx; areaId=xxx; token=xxx; speedqqcomrouteLine=xxx;

其中
speedqqcomrouteLine就是签到页的url中间段，即http://speed.qq.com/lbact/xxxxxxxxxx/zfmrqd.html中的xxxxxxxxxx部分
token进入签到页（url参数里面有）或者进入寻宝页（Referer里面会出现）都能获取到
'''
import datetime
import re
import os
import sys
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup

sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 用户信息、奖励信息、特别福利日期
user_data = {}
giftid_list = []
date_list = []

# 获取环境变量
def get_env():
    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    if "COOKIE_ZHANGFEI" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_ZHANGFEI').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_ZHANGFEI变量未启用')
            send('掌上飞车签到', 'COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车签到', '未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


# 定义一个获取url页面下label标签的attr属性的函数
def getHtml(url):
    zfmrqd = requests.get(f"http://speed.qq.com/lbact/{url}/zfmrqd.html")
    zfmrqd.encoding = 'utf-8'
    html = zfmrqd.text
    soup = BeautifulSoup(html, 'html.parser')

    for target in soup.find_all('a'):
        if target.get('id'):
            if target.get('id').find('Hold_') + 1:
                giftid_list.append(target.get('id').split('Hold_')[-1])

    for target in soup.find_all('p'):
        if target.get('class'):
            if str(target.get('class')).find('tab2_number') + 1:
                date_list.append(target.text)

    # 获取活动ID: iActivityId
    bridgeTpl_2373 = requests.get(f"http://speed.qq.com/lbact/{url}/bridgeTpl_2373.js")
    bridgeTpl_2373.encoding = 'utf-8'
    regex = r'window.iActivityId=(.*?);'
    user_data.update({"iActivityId": re.findall(regex, bridgeTpl_2373.text)[0]})


# 签到
def sign_gift(user_data, iflowid):
    msg = ""

    url = f"https://comm.ams.game.qq.com/ams/ame/amesvr?iActivityId={user_data.get('iActivityId')}"
    headers = {
        'Cookie': f"access_token={user_data.get('accessToken')}; "
                  f"acctype=qc; "
                  f"appid={user_data.get('appid')}; "
                  f"openid={user_data.get('openid')}; "
    }
    data = {
        "iActivityId": user_data.get('iActivityId'),
        "iFlowId": iflowid,
        "g_tk": "1842395457",
        "sServiceType": "speed"
    }

    response = requests.post(url, headers=headers, data=data)
    response.encoding = "utf-8"

    return str(response.json()['modRet']['sMsg']) if response.json()['ret'] == '0' else str(
        response.json()['flowRet']['sMsg'])


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    cookie_zhangfei = get_env()
    day = datetime.datetime.now().strftime('%m月%d日')

    i = 0
    while i < len(cookie_zhangfei):
        # 获取user_data参数
        for a in cookie_zhangfei[i].replace(" ","").split(';'):
            if not a == '':
                user_data.update({a.split('=')[0]: unquote(a.split('=')[1])})
        # print(user_data)

        # 获取累计信息、奖励信息、特别福利日期
        getHtml(user_data['speedqqcomrouteLine'])

        # 开始任务
        log = f"第 {i + 1} 个账号 {user_data.get('roleId')} {'电信区' if user_data.get('areaId') == '1' else '联通区' if user_data.get('areaId') == '2' else '电信2区'} 开始执行任务"
        msg += log + '\n'
        print(f"{log}\n{datetime.datetime.now().strftime('%m月')}礼物有:{str(giftid_list)}")

        # 签到
        log = sign_gift(user_data, giftid_list[0])
        msg += f"今日{day} {log}\n"
        print(f"今日{day} {log}")

        # 特别福利
        date_dict = dict(zip(date_list, giftid_list[-len(date_list):]))
        if day in date_dict:
            log = sign_gift(user_data, date_dict[day])
            if '非常抱歉！您的资格已用尽！' in log:
                log = "已领取完^!^请勿贪心哦"
            msg += f"特殊福利:{log}\n"
            print(f"特殊福利:{log}")
        else:
            msg += "今日无特殊福利礼物\n"
            print("今日无特殊福利礼物")

        # 累计签到奖励
        for gift in giftid_list[1:-len(date_list)]:
            log = sign_gift(user_data, gift)
            if log not in ['您已领取过奖励！', '非常抱歉，您的签到天数不足！']:
                msg += f"累计签到礼物id[{gift}]：{log}\n"
            print(f"累计签到礼物id[{gift}]：{log}")

        i += 1

    if sendnoty:
        try:
            send('掌上飞车签到', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('掌上飞车签到', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车开始尝试签到----------")
    main()
    print("----------掌上飞车签到执行完毕----------")
