'''
new Env('脚本猫论坛签到')
cron: 1 0 * * *
Author       : BNDou
Date         : 2024-06-14 03:24:38
LastEditTime: 2024-06-15 21:41:44
FilePath: \Auto_Check_In\checkIn_ScriptCat.py
Description  : 添加环境变量COOKIE_SCRIPTCART，多账号用 回车 或 && 分开
'''

import os
import re
import sys

import requests
from lxml import etree

# 测试用环境变量
# os.environ['COOKIE_SCRIPTCART'] = ''

try:  # 异常捕捉
    from utils.sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_SCRIPTCART是否存在于环境变量
    if "COOKIE_SCRIPTCART" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_SCRIPTCART'))
    else:
        # 标准日志输出
        print('未添加COOKIE_SCRIPTCART变量')
        send('脚本猫论坛签到', '未添加COOKIE_SCRIPTCART变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


class ScriptCat:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_name = None
        self.leijiqiandao = None
        self.benyueleijiqiandao = None
        self.coin_zong = None
        self.coin_huode = None
        self.user_group = None
        self.haixvqiandao = None
        self.xiayige_group = None
        self.date = None
        self.log = None

    def get_qiandao(self):
        """签到"""
        url = "https://bbs.tampermonkey.net.cn/plugin.php"
        params = {
            "id": "dsu_paulsign:sign",
            "operation": "qiandao",
            "infloat": "1",
            "inajax": "1",
        }
        data = {
            "formhash": "738cc5d7",
            "qdxq": "kx",
            "qdmode": "3",
            "todaysay": "",
            "fastreply": "0",
        }
        log_res = requests.post(url=url,
                                params=params,
                                headers={'Cookie': self.cookie},
                                data=data)
        if log_res.status_code == 200:
            self.log = re.search(r'<div class="c">\r\n(.*?) </div>',
                                 log_res.text).group(1)

    def get_log(self):
        """获取签到日期记录"""
        log_url = "https://bbs.tampermonkey.net.cn/plugin.php?id=dsu_paulsign:sign"
        log_res = requests.get(url=log_url, headers={'Cookie': self.cookie})
        # print(log_res.text)
        html = etree.HTML(log_res.text)
        self.user_name = html.xpath('//b//text()')[0]
        self.leijiqiandao = html.xpath('//b//text()')[1]
        self.benyueleijiqiandao = html.xpath('//b//text()')[2]
        self.coin_zong = html.xpath('//b//text()')[3]
        self.coin_huode = html.xpath('//b//text()')[4]
        self.user_group = html.xpath('//b//text()')[5]
        self.haixvqiandao = html.xpath('//b//text()')[6]
        self.xiayige_group = html.xpath('//b//text()')[7]
        self.date = html.xpath('//p[3]/font//text()')[0]

    def main(self):
        """执行"""
        self.get_qiandao()
        self.get_log()

        if self.log:
            return (
                f'👶 {self.user_name}，目前的等级: {self.user_group}\n'
                f'⭐ {self.log}\n'
                f'⭐ 累计已签到: {self.leijiqiandao} 天\n'
                f'⭐ 本月已累计签到:{self.benyueleijiqiandao} 天\n'
                f'⭐ 目前获得的总奖励为：油猫币 {self.coin_zong}\n'
                f'⭐ 上次获得的奖励为：油猫币 {self.coin_huode}\n'
                f'⭐ 上次签到时间:{self.date}\n'
                f'Tips：再签到 {self.haixvqiandao} 天就可以提升到下一个等级: {self.xiayige_group}'
            )
        else:
            return '❌️签到失败，可能是cookie失效了！'


if __name__ == "__main__":
    print("----------脚本猫论坛开始尝试签到----------")

    msg, cookie_ScriptCat = "", get_env()

    i = 0
    while i < len(cookie_ScriptCat):
        log = f"第 {i + 1} 个账号开始执行任务\n"
        log += ScriptCat(cookie_ScriptCat[i]).main()
        msg += log + "\n\n"
        print(log)
        i += 1

    try:
        send('脚本猫论坛签到', msg)
    except Exception as err:
        print('%s\n❌️错误，请查看运行日志！' % err)

    print("----------脚本猫论坛签到执行完毕----------")
