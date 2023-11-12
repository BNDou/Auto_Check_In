'''
new Env('恩山论坛签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-10-30 22:21:48
LastEditTime : 2022-12-05 17:48:35
FilePath     : /Auto_Check_In/checkIn_EnShan.py
Description  : 添加环境变量COOKIE_ENSHAN，多账号用回车换行分开
'''

from lxml import etree
import requests
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

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
        r = s.get(url=url, headers=headers, timeout=120)
        # print(r.text)
        if '每天登录' in r.text:
            h = etree.HTML(r.text)
            data = h.xpath('//tr/td[6]/text()')
            msg += f'签到成功或今日已签到\n最后签到时间：{data[0]}'
        else:
            msg += '签到失败，可能是cookie失效了！'
    except:
        msg = '无法正常连接到网站，请尝试改变网络环境，试下本地能不能跑脚本，或者换几个时间点执行脚本'

    return msg + '\n\n'


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_enshan
    cookie_enshan = get_env()

    i = 0
    while i < len(cookie_enshan):
        msg += f"第 {i+1} 个账号开始执行任务\n"
        msg += run(cookie_enshan[i])
        i += 1

    print(msg[:-1])

    if sendnoty:
        try:
            send('恩山论坛签到', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------恩山论坛开始尝试签到----------")
    main()
    print("----------恩山论坛签到执行完毕----------")
