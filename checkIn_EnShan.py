'''
new Env('恩山论坛签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2022-10-30 22:21:48
LastEditTime: 2024-05-29 01:57:44
FilePath: \Auto_Check_In\checkIn_EnShan.py
Description  : 添加环境变量COOKIE_ENSHAN，多账号用 回车 或 && 分开
'''

import os
import re
import sys

import requests
from lxml import etree

# 测试用环境变量
# os.environ["COOKIE_ENSHAN"] = ""

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print("%s\n加载通知服务失败~" % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_ENSHAN是否存在于环境变量
    if "COOKIE_ENSHAN" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split("\n|&&", os.environ.get("COOKIE_ENSHAN"))
    else:
        # 标准日志输出
        print("未添加COOKIE_ENSHAN变量")
        send("恩山论坛签到", "未添加COOKIE_ENSHAN变量")
        # 脚本退出
        sys.exit(0)

    return cookie_list


class EnShan:
    """恩山论坛签到"""
    def __init__(self, cookie):
        """初始化"""
        self.cookie = cookie
        self.user_name = None
        self.user_group = None
        self.coin = None
        self.contribution = None
        self.point = None
        self.date = None

    def get_user(self):
        """获取用户积分"""
        user_url = "https://www.right.com.cn/FORUM/home.php?mod=spacecp&ac=credit"
        user_res = requests.get(url=user_url, headers={'Cookie': self.cookie})
        self.user_name = re.findall(r'访问我的空间">(.*?)</a>', user_res.text)[0]
        self.user_group = re.findall(r'用户组: (.*?)</a>', user_res.text)[0]
        self.contribution = re.findall(r'贡献: </em>(.*?) 分', user_res.text)[0]
        self.coin = re.findall(r'恩山币: </em>(.*?) 币', user_res.text)[0]
        self.point = re.findall(r'积分: </em>(.*?) ', user_res.text)[0]

    def get_log(self):
        """获取签到日期记录"""
        log_url = "https://www.right.com.cn/forum/home.php?mod=spacecp&ac=credit&op=log&suboperation=creditrulelog"
        log_res = requests.get(url=log_url, headers={'Cookie': self.cookie})
        html = etree.HTML(log_res.text)
        self.date = html.xpath('//tr/td[6]/text()')[0]

    def main(self):
        """执行"""
        self.get_log()
        self.get_user()

        if self.date:
            return (
                f"👶{self.user_group}：{self.user_name}\n"
                f"🏅恩山币：{self.coin} 贡献：{self.contribution} 积分：{self.point}\n"
                f"⭐签到成功或今日已签到\n"
                f"⭐最后签到时间：{self.date}")
        else:
            return '❌️签到失败，可能是cookie失效了！'


if __name__ == "__main__":
    print("----------恩山论坛开始尝试签到----------")

    msg, cookie_EnShan = "", get_env()

    i = 0
    while i < len(cookie_EnShan):
        log = f"第 {i + 1} 个账号开始执行任务\n"
        log += EnShan(cookie_EnShan[i]).main()
        msg += log + "\n\n"
        print(log)
        i += 1

    try:
        send("恩山论坛签到", msg)
    except Exception as err:
        print("%s\n❌️错误，请查看运行日志！" % err)

    print("----------恩山论坛签到执行完毕----------")
