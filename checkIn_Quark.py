'''
new Env('夸克自动签到')
cron: 0 9 * * *
Author       : BNDou
Date         : 2024/3/15 21:43
File         : checkIn_Quark
Description  :
抓包流程：
    ①浏览器访问-https://pan.quark.cn/ 并登录
    ②按F12打开“调试”，选中“网络”，找到一个以“sort”开头的文件即url=https://drive-pc.quark.cn/1/clouddrive/file/sort的请求信息
    ③复制全部cookie粘贴到环境变量，环境变量名为 COOKIE_QUARK，多账户用 回车 或 && 分开
'''
import os
import re
import sys

import requests

# 测试用环境变量
# os.environ['COOKIE_QUARK'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n❌加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_QUARK是否存在于环境变量
    if "COOKIE_QUARK" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_QUARK'))
    else:
        # 标准日志输出
        print('❌未添加COOKIE_QUARK变量')
        send('夸克自动签到', '❌未添加COOKIE_QUARK变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


def get_growth_info(cookie):
    url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
    querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
    headers = {"cookie": cookie}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if response.get("data"):
        return response["data"]
    else:
        return False


def get_growth_sign(cookie):
    url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
    querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
    payload = {"sign_cyclic": True}
    headers = {"cookie": cookie}
    response = requests.request(
        "POST", url, json=payload, headers=headers, params=querystring).json()
    if response.get("data"):
        return True, response["data"]["sign_daily_reward"]
    else:
        return False, response["message"]


def get_account_info(cookie):
    url = "https://pan.quark.cn/account/info"
    querystring = {"fr": "pc", "platform": "pc"}
    headers = {"cookie": cookie}
    response = requests.request("GET", url, headers=headers, params=querystring).json()
    if response.get("data"):
        return response["data"]
    else:
        return False


def do_sign(cookie):
    msg = ""
    # 验证账号
    account_info = get_account_info(cookie)
    if not account_info:
        msg = f"\n❌该账号登录失败，cookie无效"
    else:
        log = f" 昵称: {account_info['nickname']}"
        msg += log + "\n"
        # 每日领空间
        growth_info = get_growth_info(cookie)
        if growth_info:
            if growth_info["cap_sign"]["sign_daily"]:
                log = f"✅ 执行签到: 今日已签到+{int(growth_info['cap_sign']['sign_daily_reward'] / 1024 / 1024)}MB，连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})"
                msg += log + "\n"
            else:
                sign, sign_return = get_growth_sign(cookie)
                if sign:
                    log = f"✅ 执行签到: 今日签到+{int(sign_return / 1024 / 1024)}MB，连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})"
                    msg += log + "\n"
                else:
                    msg += f"✅ 执行签到: {sign_return}\n"

    return msg


def main():
    msg = ""
    global cookie_quark
    cookie_quark = get_env()

    print("✅检测到共", len(cookie_quark), "个夸克账号\n")

    i = 0
    while i < len(cookie_quark):
        # 开始任务
        log = f"🙍🏻‍♂️ 第{i + 1}个账号"
        msg += log
        # 登录
        log = do_sign(cookie_quark[i])
        msg += log + "\n"

        i += 1

    print(msg)

    try:
        send('夸克自动签到', msg)
    except Exception as err:
        print('%s\n❌错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------夸克网盘开始尝试签到----------")
    main()
    print("----------夸克网盘签到执行完毕----------")
