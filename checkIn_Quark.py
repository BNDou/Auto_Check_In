'''
new Env('夸克自动签到')
cron: 0 9 * * *

受大佬 @Cp0204 的仓库项目启发改编
源码来自 GitHub 仓库：https://github.com/Cp0204/quark-auto-save
提取“登录验证”“签到”“领取”方法封装到下文中的“Quark”类中

Author: BNDou
Date: 2024-03-15 21:43:06
LastEditTime: 2024-05-28 21:44:55
FilePath: \Auto_Check_In\checkIn_Quark.py
Description: 
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


class Quark:
    '''
    Quark类封装了登录验证、签到、领取签到奖励的方法
    '''
    def __init__(self, cookie):
        '''
        初始化方法
        :param cookie: 用户登录后的cookie，用于后续的请求
        '''
        self.cookie = cookie

    def get_growth_info(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        headers = {"content-type": "application/json", "cookie": self.cookie}
        response = requests.get(url=url, headers=headers,
                                params=querystring).json()
        #print(f"info={response}\n")
        if response.get("data"):
            return response["data"]
        else:
            return False

    def get_growth_sign(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        querystring = {"pr": "ucpro", "fr": "pc", "uc_param_str": ""}
        payload = {"sign_cyclic": True}
        headers = {"content-type": "application/json", "cookie": self.cookie}
        response = requests.post(url=url,
                                 json=payload,
                                 headers=headers,
                                 params=querystring).json()
        #print(f"sign={response}\n")
        if response.get("data"):
            return True, response["data"]["sign_daily_reward"]
        else:
            return False, response["message"]

    def get_account_info(self):
        '''
        获取用户账号信息
        :return: 返回一个字典，包含用户账号信息
        '''
        url = "https://pan.quark.cn/account/info"
        querystring = {"fr": "pc", "platform": "pc"}
        headers = {"content-type": "application/json", "cookie": self.cookie}
        response = requests.get(url=url, headers=headers,
                                params=querystring).json()
        if response.get("data"):
            return response["data"]
        else:
            return False

    def b_to_mb(self, b):
        '''
        将字节转换为MB
        :param b: 字节数
        :return: 返回转换后的MB数
        '''
        return b / (1024 * 1024)

    def b_to_gib(self, b):
        '''
        将字节转换为GB
        :param b: 字节数
        :return: 返回转换后的GB数(保留两位小数)
        '''
        gib = b / (1024 * 1024 * 1024)
        return round(gib, 1)

    def do_sign(self):
        '''
        执行签到任务
        :return: 返回一个字符串，包含签到结果
        '''
        msg = ""
        # 验证账号
        account_info = self.get_account_info()
        if not account_info:
            msg = f"\n❌该账号登录失败，cookie无效"
        else:
            log = f" 昵称: {account_info['nickname']}"
            msg += log + "\n"
            # 每日领空间
            growth_info = self.get_growth_info()
            if growth_info:
                log = f"💾 网盘总容量：{self.b_to_gib(growth_info['total_capacity'])}GB，签到累计容量：{self.b_to_gib(growth_info['cap_composition']['sign_reward'])}GB\n"
                if growth_info["cap_sign"]["sign_daily"]:
                    log += f"✅ 签到日志: 今日已签到+{self.b_to_mb(growth_info['cap_sign']['sign_daily_reward'])}MB，连签进度({growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']})"
                else:
                    sign, sign_return = self.get_growth_sign()
                    if sign:
                        log += f"✅ 执行签到: 今日签到+{self.b_to_mb(sign_return)}MB，连签进度({growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']})"
                    else:
                        log = f"❌ 签到异常: {sign_return}"
            msg += log + "\n"
        return msg


def main():
    '''
    主函数
    :return: 返回一个字符串，包含签到结果
    '''
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
        log = Quark(cookie_quark[i]).do_sign()
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
