'''
new Env('测试TEST')
cron: 11 11 11 11 *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime : 2022-12-30 23:56:11
FilePath     : /Auto_Check_In/checkIn_test.py
Description  : 
'''
from urllib.parse import unquote
import requests
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_ZHANGFEI'] = 'aaaaaa'
# os.environ['COOKIE_ZHANGFEI'] = 'ssssss'
# os.environ['REFERER_ZHANGFEI'] = 'qqqqqq'
# os.environ['REFERER_ZHANGFEI'] = 'wwwwww'


# 获取环境变量
def get_env():
    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    if "COOKIE_ZHANGFEI" in os.environ:
        # 读取系统变量 以 & 分割变量
        cookie_list = os.environ.get('COOKIE_ZHANGFEI').split('&')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    # 判断 REFERER_ZHANGFEI是否存在于环境变量
    if "REFERER_ZHANGFEI" in os.environ:
        referer_list = os.environ.get('REFERER_ZHANGFEI').split('&')
        if len(referer_list) <= 0:
            print('REFERER_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加REFERER_ZHANGFEI变量')
        sys.exit(0)

    return cookie_list, referer_list


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    global referer_zhangfei
    cookie_zhangfei, referer_zhangfei = get_env()

    print(cookie_zhangfei)
    print('\n')
    print(referer_zhangfei)

    return msg[:-1]


if __name__ == "__main__":
    main()
