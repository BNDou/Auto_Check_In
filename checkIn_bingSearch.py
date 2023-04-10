'''
new Env('必应搜索')
cron: 0 13 * * *
Author       : BNDou
Date         : 2023-04-09 01:07:07
LastEditTime : 2023-04-09 17:31:44
FilePath     : /Auto_Check_In/checkIn_bingSearch.py
Description  : 
'''
import requests
import time
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_BING'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_BING是否存在于环境变量
    if "COOKIE_BING" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_BING').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_BING变量未启用')
            send('必应手机端搜索', 'COOKIE_BING变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_BING变量')
        send('必应手机端搜索', '未添加COOKIE_BING变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


# 搜索
def search1(cookie, num):
    msg = ''
    s = requests.Session()
    s.headers.update(
        {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; HLK-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Mobile Safari/537.36 EdgA/104.0.1293.70'})

    url = f"https://cn.bing.com/search?q={num}"
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 10; HLK-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Mobile Safari/537.36 EdgA/104.0.1293.70',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'X-Client-Data': 'eyIxIjoiMCIsIjEwIjoiIiwiMiI6IjAiLCIzIjoiMCIsIjQiOiI3ODMxOTQzNjUyNTEyNDAyOTY5IiwiNSI6IlwiQ28vWlVHL0hIbDdLTnYyUXNDQWszK1g5K3kvblVzQlkxUFpPVTZ0QTczaz1cIiIsIjYiOiJzdGFibGUiLCI3IjoiOTUxMzM1MjU2MDY0MiIsIjkiOiJkZXNrdG9wIn0=',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'sec-ch-ua': '"Edge";v="104", "Chromium";v="104", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'Referer': 'https://cn.bing.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
    }

    r = s.get(url=url, headers=headers, timeout=120)
    # 延迟2秒执行，防止频繁
    time.sleep(2)

    return r.reason


def search2(cookie, num):
    msg = ''
    s = requests.Session()
    s.headers.update(
        {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5026.0 Safari/537.36 Edg/103.0.1254.0'})

    url = f"https://cn.bing.com/search?q={num}"
    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5026.0 Safari/537.36 Edg/103.0.1254.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'X-Client-Data': 'eyIxIjoiMCIsIjEwIjoiIiwiMiI6IjAiLCIzIjoiMCIsIjQiOiI3ODMxOTQzNjUyNTEyNDAyOTY5IiwiNSI6IlwiQ28vWlVHL0hIbDdLTnYyUXNDQWszK1g5K3kvblVzQlkxUFpPVTZ0QTczaz1cIiIsIjYiOiJzdGFibGUiLCI3IjoiOTUxMzM1MjU2MDY0MiIsIjkiOiJkZXNrdG9wIn0=',
        'Sec-Fetch-Site': 'same-site',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Dest': 'document',
        'sec-ch-ua': '"Edge";v="103", "Chromium";v="103", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://cn.bing.com/',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
    }

    r = s.get(url=url, headers=headers, timeout=120)
    # 延迟2秒执行，防止频繁
    time.sleep(2)

    return r.reason


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_bing
    cookie_bing = get_env()

    i = 0
    while i < len(cookie_bing):
        # 搜索
        err = 0
        log = f"第 {i+1} 个账号开始执行任务"
        msg += log + '\n'
        print(log)
        # 手机端
        for num in range(20):
            log = search1(cookie_bing[i].replace(' ', ''), num)
            print(f"手机端搜索{num}-" + log)
            if log not in 'OK':
                err += 1
        log = f"手机端成功✅✅{20-err}次"
        msg += log + '\n'
        print(log)
        # PC端
        for num in range(30, 60):
            log = search2(cookie_bing[i].replace(' ', ''), num)
            print(f"PC端搜索{num}-" + log)
            if log not in 'OK':
                err += 1
        log = f"PC端成功✅✅{30-err}次"
        msg += log + '\n'
        print(log)

        i += 1

    if sendnoty:
        try:
            send('必应手机端搜索', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('必应手机端搜索', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------必应手机端搜索开始尝试----------")
    main()
    print("----------必应手机端搜索执行完毕----------")
