'''
new Env('test')
cron: 10 0 * * *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime: 2024-07-17 23:22:18
FilePath: \Auto_Check_In\backUp\checkIn_test.py
Description  :

'''
import os
import sys

import requests

sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['cookie_test'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 cookie_test是否存在于环境变量
    if "cookie_test" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('cookie_test').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('cookie_test变量未启用')
            send('test', 'cookie_test变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加cookie_test变量')
        send('test', '未添加cookie_test变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


def main(*arg):
    msg, cookie_test = "", get_env()

    i = 0
    while i < len(cookie_test):
        # 获取user_data参数
        user_data = {}
        for a in cookie_test[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a[0:a.index('=')]: a[a.index('=') + 1:]})
        # print(user_data)

        i += 1

    try:
        send('test', msg)
    except Exception as err:
        print('%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------test开始尝试签到----------")
    main()
    print("----------test签到执行完毕----------")
