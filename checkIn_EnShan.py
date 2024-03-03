'''
new Env('恩山论坛签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-10-30 22:21:48
LastEditTime : 2024-03-03 15:03:35
FilePath     : /Auto_Check_In/checkIn_EnShan.py
Description  : 添加环境变量COOKIE_ENSHAN，多账号用回车换行分开
'''

import os
import sys

import requests
from lxml import etree

# 测试用环境变量
# os.environ['COOKIE_ENSHAN'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_ENSHAN是否存在于环境变量
    if "COOKIE_ENSHAN" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_ENSHAN').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_ENSHAN变量未启用')
            send('恩山论坛签到', 'COOKIE_ENSHAN变量未启用')
            # 脚本退出
            sys.exit(0)
    else:
        # 标准日志输出
        print('未添加COOKIE_ENSHAN变量')
        send('恩山论坛签到', '未添加COOKIE_ENSHAN变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


def run(cookie):
    msg = ""

    # 签到
    url = "https://www.right.com.cn/forum/home.php?mod=spacecp&ac=credit&op=log&suboperation=creditrulelog"
    try:
        r = requests.get(url=url, headers={'Cookie': cookie}, timeout=120)
        # print(r.text)
        if '每天登录' in r.text:
            h = etree.HTML(r.text)

            user = h.xpath('//strong[@class="vwmy qq"]//a/text()')[0]
            date = h.xpath('//tr/td[6]/text()')[0]
            money = h.xpath('//a[@id="extcreditmenu"]/text()')[0]

            msg += f'账号{user} 签到成功或今日已签到\n最后签到时间：{date}\n总恩山币：{money}'
        else:
            msg += '签到失败，可能是cookie失效了！'
    except:
        msg = '无法正常连接到网站，请尝试改变网络环境，试下本地能不能跑脚本，或者换几个时间点执行脚本'

    return msg + '\n\n'


def main(*arg):
    msg, cookie_enshan = "", get_env()

    i = 0
    while i < len(cookie_enshan):
        log = f"第 {i + 1} 个账号开始执行任务\n"
        log += run(cookie_enshan[i])
        msg += log
        print(log)
        i += 1

    try:
        send('恩山论坛签到', msg)
    except Exception as err:
        print('%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------恩山论坛开始尝试签到----------")
    main()
    print("----------恩山论坛签到执行完毕----------")
