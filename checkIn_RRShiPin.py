#!/usr/bin/env python
# coding=utf-8
'''
new Env('人人视频日常')
cron: 0 9 * * *

FilePath     : /Auto_Check_In/checkIn_RRShiPin.py
Author       : BNDou
Date         : 2024-06-05 01:56:28
LastEditTime : 2026-05-12 23:21:49
Description  :  
抓包流程：
    ①开启抓包，打开签到页
    ②找到url = https://api.qwdjapp.com/activity/index/integral 的请求头
    ③分别复制 clientVersion clientType token aliId st 四个值，写到环境变量中，格式如下：
    环境变量名为 COOKIE_RRShiPin 多账户用 回车 或 && 分开
    clientVersion=xxx; clientType=xxx; token=xxx; aliId=xxx; st=xxx;
'''
import os
import re
import sys

import requests

# 测试用环境变量
# os.environ['COOKIE_RRShiPin'] = ''

try:  # 异常捕捉
    from utils.notify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n🔴加载通知服务失败~' % err)

# 导入公共环境变量工具
from utils.env_utils import get_env as common_get_env


# 获取环境变量（使用公共模块）
def get_env():
    # 判断 COOKIE_RRShiPin 是否存在于环境变量
    cookie_list = common_get_env('COOKIE_RRShiPin')
    if not cookie_list:
        # 标准日志输出
        print('🔴未添加 COOKIE_RRShiPin 变量')
        send('人人视频日常', '🔴未添加 COOKIE_RRShiPin 变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


class RRShiPin:
    '''
    人人视频签到类，封装了积分查询、签到任务列表查询、签到、激活任务、领取任务奖励的方法
    '''
    def __init__(self, cookie):
        '''
        初始化方法
        :param cookie: 用户登录后的cookie，用于后续的请求
        '''
        self.cookie = {}
        for a in cookie.replace(" ", "").split(';'):
            if a and '=' in a:
                parts = a.split('=', 1)
                self.cookie[parts[0]] = parts[1]

    def user_information(self):
        '''
        获取用户信息
        :return: 返回用户信息
        '''
        url = f"https://api.qwdjapp.com/user/personal/information?token={self.cookie.get('token')}"
        headers = {
            "clientVersion": self.cookie.get('clientVersion'),
            "clientType": self.cookie.get('clientType'),
            "token": self.cookie.get('token'),
            "aliId": self.cookie.get('aliId'),
            "st": self.cookie.get('st'),
        }
        rjson = requests.get(url, headers=headers, timeout=15).json()
        if rjson['code'] == '0000':
            self.cookie['nickName'] = rjson['data']['user']['nickName']
            return f"👶 登录账号: {rjson['data']['user']['nickName']}"
        return f"🔴 登录账号: 失败\n{rjson}"

    def get_integral(self):
        '''
        获取用户当前的积分信息
        :return: 返回用户当前的积分信息
        '''
        url = "https://api.qwdjapp.com/activity/index/integral"
        headers = {
            "clientVersion": self.cookie.get('clientVersion'),
            "clientType": self.cookie.get('clientType'),
            "token": self.cookie.get('token'),
            "aliId": self.cookie.get('aliId'),
            "st": self.cookie.get('st'),
        }
        rjson = requests.get(url, headers=headers, timeout=15).json()
        if rjson['code'] == '0000':
            if not rjson['data'] == None:
                return rjson['data']['integral']
        return f"🔴 获取积分信息失败: \n{rjson}"

    def get_sign(self):
        '''
        请求签到
        :return: 返回签到信息
        '''
        url = "https://api.qwdjapp.com/activity/sign"
        headers = {
            "clientVersion": self.cookie.get('clientVersion'),
            "clientType": self.cookie.get('clientType'),
            "token": self.cookie.get('token'),
            "aliId": self.cookie.get('aliId'),
            "st": self.cookie.get('st'),
        }
        data = {"sectionId": "0"}
        rjson = requests.post(url, headers=headers, data=data, timeout=15).json()
        if rjson['code'] == '0000':
            if not rjson['data'] == None:
                return f"🟢 领取签到奖励: {rjson['data']['value']}"
            else:
                return '🟢 领取签到奖励: 今日签到奖励已领取！'
        return f"🔴 签到失败: \n{rjson}"

    def get_list(self):
        '''
        请求签到任务列表
        :return: 返回签到任务列表
        '''
        url = 'https://api.qwdjapp.com/activity/index/list'
        headers = {
            "clientVersion": self.cookie.get('clientVersion'),
            "clientType": self.cookie.get('clientType'),
            "token": self.cookie.get('token'),
            "aliId": self.cookie.get('aliId'),
            "st": self.cookie.get('st'),
        }
        rjson = requests.get(url, headers=headers, timeout=15).json()
        if rjson['code'] == '0000':
            if not rjson['data'] == None:
                dailyTaskList = rjson['data']['dailyTaskDto']
                if len(dailyTaskList):
                    dailyTaskList = sorted(dailyTaskList,
                                           key=lambda x: x['id'])
                    return dailyTaskList
        return []

    def get_receive(self, taskId):
        '''
        激活任务
        :param taskId: 任务ID
        :return: 返回激活任务信息
        '''
        url = 'https://api.qwdjapp.com/activity/task/status/receive'
        headers = {
            "clientVersion": self.cookie.get('clientVersion'),
            "clientType": self.cookie.get('clientType'),
            "token": self.cookie.get('token'),
            "aliId": self.cookie.get('aliId'),
            "st": self.cookie.get('st'),
        }
        data = {'taskId': taskId}
        rjson = requests.post(url, headers=headers, data=data, timeout=15).json()
        if rjson['code'] == '0000':
            return f"🟢 任务{taskId}: 激活成功"
        return f"🔴 任务{taskId}: 激活失败\n{rjson}"

    def get_complete(self, taskId):
        '''
        领取任务奖励
        :param taskId: 任务ID
        :return: 返回领取奖励信息
        '''
        url = "https://api.qwdjapp.com/activity/task/status/complete"
        headers = {
            "clientVersion": self.cookie.get('clientVersion'),
            "clientType": self.cookie.get('clientType'),
            "token": self.cookie.get('token'),
            "aliId": self.cookie.get('aliId'),
            "st": self.cookie.get('st'),
        }
        data = {"taskId": taskId}
        rjson = requests.post(url, headers=headers, data=data, timeout=15).json()
        if rjson['code'] == '0000':
            return f"🟢 任务{taskId}: 奖励领取成功"
        return f"🔴 任务{taskId}: 奖励领取失败\n{rjson}"

    def sendLog(self, msg, log):
        '''
        添加推送日志
        :param msg: 消息内容
        :param log: 日志内容
        :return: 无
        '''
        print(log)
        return (msg + log + "\n")

    def run(self):
        '''
        执行日常任务
        :return: 返回一个字符串，包含签到结果
        '''
        # 获取用户信息
        msg = self.sendLog("", self.user_information())
        # 获取初始积分信息
        print(f"🏅 初始积分: {self.get_integral()}")
        # 请求签到
        msg = self.sendLog(msg, self.get_sign())
        # 获取签到任务列表
        dailyTaskList = self.get_list()
        # 激活任务和领取奖励
        for task in dailyTaskList:
            print(f"💠 任务{task['id']}: {task['taskName']} 奖励: {task['count']}")
            # 激活任务
            print(self.get_receive(task['id']))
            # 领取奖励
            msg = self.sendLog(msg, self.get_complete(task['id']))
        # 获取最终积分信息
        msg = self.sendLog(msg, f"🏅 总积分: {self.get_integral()}\n")
        return msg


if __name__ == "__main__":
    print("----------人人视频开始尝试日常----------")
    msg = ""
    for cookie_rrshipin in get_env():
        msg += f"{RRShiPin(cookie_rrshipin).run()}"
    print("----------人人视频日常执行完毕----------")

    try:
        send('人人视频日常', msg)
    except Exception as err:
        print('%s\n🔴 错误，请查看运行日志！' % err)
