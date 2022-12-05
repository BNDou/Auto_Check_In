'''
new Env('掌上飞车签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime : 2022-12-05 17:48:59
FilePath     : /Auto_Check_In/checkIn_ZhangFei.py
Description  : 添加环境变量COOKIE_ZHANGFEI、URL_ZHANGFEI，多账号用回车换行分开
'''
from lxml import etree
import requests
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


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

    # 判断 URL_ZHANGFEI是否存在于环境变量
    if "URL_ZHANGFEI" in os.environ:
        url_list = os.environ.get('URL_ZHANGFEI').split('\n')
        if len(url_list) <= 0:
            print('URL_ZHANGFEI变量未启用')
            send('掌上飞车签到', 'URL_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加URL_ZHANGFEI变量')
        send('掌上飞车签到', '未添加URL_ZHANGFEI变量')
        sys.exit(0)

    return cookie_list, url_list


def run(cookie, url):
    msg = ""
    s = requests.Session()
    s.headers.update({'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Mi 10 Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36 GH_QQConnect GameHelper_1003/2103040778'})

    # 签到
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; Mi 10 Build/SKQ1.211006.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/96.0.4664.104 Mobile Safari/537.36 GH_QQConnect GameHelper_1003/2103040778',
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
    }

    r = s.get(url=url, headers=headers, timeout=120)
    rjson = r.json()
    msg += rjson.get('message', '')
    if 'send_result' in rjson:
        msg += '\n' + rjson.get('send_result').get('sMsg', '')

    return msg + '\n\n'


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    global url_zhangfei
    cookie_zhangfei, url_zhangfei = get_env()

    i = 0
    while i < len(cookie_zhangfei):
        msg += f"第 {i+1} 个账号开始执行任务\n"
        msg += run(cookie_zhangfei[i].replace(' ', ''),
                   url_zhangfei[i].replace(' ', ''))
        i += 1

    print(msg[:-1])

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
