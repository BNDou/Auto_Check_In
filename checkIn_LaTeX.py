'''
new Env('LaTeX工作室签到')
cron: 2 1 * * *

Author: BNDou
Date: 2024-08-22 23:19:20
LastEditTime: 2025-11-18 03:49:26
FilePath: \Auto_Check_In\checkIn_LaTeX.py
Description: 
'''

import os
import re
import sys

import requests

# 测试用环境变量
# os.environ['COOKIE_LATEX_TOKEN'] = ''

try:  # 异常捕捉
    from utils.notify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_LATEX_TOKEN 是否存在于环境变量
    if "COOKIE_LATEX_TOKEN" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_LATEX_TOKEN'))
    else:
        # 标准日志输出
        print('未添加 COOKIE_LATEX_TOKEN 变量')
        send('LaTeX工作室签到', '未添加 COOKIE_LATEX_TOKEN 变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


class LaTeX:
    '''LaTeX工作室签到类'''
    def __init__(self, token):
        self.token = token
        self.logintime = None
        self.money = None
        self.nickname = None
        self.score = None
        self.sign_num = None
        self.sign_text = None
        self.vip_text = None
        self.msg = None

    def sign(self):
        """签到"""
        url = f"https://www.latexstudio.net/api/Sign/Sign?token={self.token}"
        res = requests.post(url).json()
        self.sign_text = res['msg']

    def user(self):
        """获取用户信息"""
        url = f"https://www.latexstudio.net/api/user/index?token={self.token}"
        res = requests.get(url).json()
        if res['code'] == 1:
            self.logintime = res['data']['logintime']
            self.money = res['data']['money']
            self.nickname = res['data']['nickname']
            self.score = res['data']['score']
            self.sign_num = res['data']['tongji']['sign_num']
            self.vip_text = res['data']['vip_text']
        else:
            self.msg += res['msg']

    def main(self):
        """执行"""
        self.user()
        self.sign()

        if self.msg:
            return '❌️ 签到失败，可能是token失效了！'
        else:
            return (f'👶 {self.nickname}\n'
                    f'⭐ 会员套餐: {self.vip_text}\n'
                    f'⭐ 余额: {self.money}\n'
                    f'⭐ 积分: {self.score}\n'
                    f'⭐ 累计已签到: {self.sign_num} 天\n'
                    f'⭐ {self.sign_text}\n'
                    f'⭐ 上次登录: {self.logintime}\n')


if __name__ == "__main__":
    print("----------LaTeX工作室开始尝试签到----------")

    msg, cookie_LaTeX_Tokens = "", get_env()

    i = 0
    while i < len(cookie_LaTeX_Tokens):
        log = f"第 {i + 1} 个账号开始执行任务\n"
        try:
            log += LaTeX(cookie_LaTeX_Tokens[i]).main()
        except Exception as e:
            print(f"第 {i + 1} 个账号 处理时发生错误: {str(e)}")
            print("继续处理下一个账号...")
            continue
        msg += log + "\n"
        print(log)
        i += 1

    try:
        send('LaTeX工作室签到', msg)
    except Exception as err:
        print('%s\n❌️错误，请查看运行日志！' % err)

    print("----------LaTeX工作室签到执行完毕----------")
