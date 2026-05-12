#!/usr/bin/env python
# coding=utf-8
'''
new Env('掌上飞车-0点开金丝篓')
cron: 59 59 23 * * *

FilePath     : /Auto_Check_In/checkIn_ZhangFei_JinSiLou.py
Author       : BNDou
Date         : 2022-12-28 23:58:11
LastEditTime : 2026-05-12 23:27:25
Description  : 端游 金丝篓开永久雷诺
默认只有出货才推送通知

①添加zhangFei_jinSiLouNum变量于config.sh用于控制开启金丝篓个数，变量为大于零的整数
②添加环境变量COOKIE_ZHANGFEI，多账户用 回车 或 && 分开
同签到的环境变量，只需要添加8个值即可，分别是
roleId=QQ号; userId=掌飞社区ID号; accessToken=xxx; appid=xxx; openid=xxx; areaId=xxx; token=xxx;

其中
token进入签到页（url参数里面有）或者进入寻宝页（Referer里面会出现）都能获取到
'''
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import unquote

import requests

# 测试用环境变量
# os.environ['zhangFei_jinSiLouNum'] = '1'
# os.environ['COOKIE_ZHANGFEI'] = ''

try:  # 异常捕捉
    from utils.notify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n❌加载通知服务失败~' % err)

# 导入公共环境变量工具
from utils.env_utils import get_env as common_get_env


# 获取环境变量（使用公共模块）
def get_env():
    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    cookie_list = common_get_env('COOKIE_ZHANGFEI')
    if not cookie_list:
        # 标准日志输出
        print('❌未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车开金丝篓', '❌未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    # 判断 金丝篓开启个数 变量zhangFei_jinSiLouNum是否存在于环境变量
    if "zhangFei_jinSiLouNum" in os.environ:
        if len(os.environ.get('zhangFei_jinSiLouNum')) <= 0 or int(
                os.environ.get('zhangFei_jinSiLouNum')) == 0:
            print('❌使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n'
                  '❌直接在config.sh添加export zhangFei_jinSiLouNum=**\n'
                  '❌变量为大于零的整数')
            send('掌上飞车开金丝篓', ('❌使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n'
                              '❌直接在config.sh添加export zhangFei_jinSiLouNum=**\n'
                              '❌变量为大于零的整数'))
            sys.exit(1)
    else:
        print('❌使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n'
              '❌直接在config.sh添加export zhangFei_jinSiLouNum=**\n'
              '❌变量为大于零的整数')
        send('掌上飞车开金丝篓', ('❌使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n'
                          '❌直接在config.sh添加export zhangFei_jinSiLouNum=**\n'
                          '❌变量为大于零的整数'))
        sys.exit(0)

    return cookie_list


# 开箱函数（用于ThreadPoolExecutor）
def open_box(user_data):
    """开金丝篓"""
    url = "https://bang.qq.com/app/speed/chest/ajax/openBox"
    headers = {'Referer': f"https://bang.qq.com/app/speed/chest/index/v2"}
    # 生成表单
    data = {
        'userId': user_data.get('userId'),  # 掌飞id
        'uin': user_data.get('roleId'),  # QQ账号
        'areaId': user_data.get('areaId'),  # 大区
        'token': user_data.get('token'),  # 令牌
        'boxId': '17455',  # 金丝篓17455
        'openNum': '1'  # 1个金丝篓开2个大闸蟹
    }
    result = ''
    try:
        r = requests.post(url=url, headers=headers, data=data, timeout=15)
        a = r.json()

        # 是否成功
        if 'data' in a:
            if 'itemList' in a.get('data'):
                item_list = a.get('data').get('itemList')
                for num in range(len(item_list)):
                    result += f"✅{item_list[num].get('avtarname')}*{item_list[num].get('num')} "
                    num += 1
            if 'msg' in a.get('data'):
                result += "❌" + str(a)
    except Exception as e:
        result = f"❌开箱异常: {str(e)}"
    return result


# token验证
def check(user):
    url = "https://api2.helper.qq.com/report/checklogswitch"
    body = {
        "gameId": "1003",
        "cSystem": "iOS",
        "cGameId": "1003",
        "userId": user.get("userId"),
        "token": user.get("token")
    }

    response = requests.post(url, data=body, timeout=15)
    response_json = response.json()
    # print(response_json)

    if response_json['returnMsg'] != "":
        print("❌账号 {}".format(user.get("roleId")),
                response_json['returnMsg'], "可更新token后重试")

    return True if response_json['returnMsg'] == "" else False


def main(*arg):
    """主函数"""
    msg = ""
    log_push = ""
    sendnoty = 'true'
    cookie_zhangfei = get_env()

    print("✅检测到共", len(cookie_zhangfei), "个飞车账号\n")

    # 准备所有开箱任务
    open_box_tasks = []
    
    i = 0
    while i < len(cookie_zhangfei):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_zhangfei[i].replace(" ", "").split(';'):
            if not a == '':
                parts = a.split('=', 1)
                user_data.update({parts[0]: unquote(parts[1])})

        # 检查token是否过期
        if not check(user_data):
            i += 1
            continue

        # 开金丝篓 - 添加到任务列表
        for num in range(int(os.environ.get('zhangFei_jinSiLouNum'))):
            open_box_tasks.append(user_data)

        i += 1

    # 使用ThreadPoolExecutor并发执行
    if open_box_tasks:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(open_box, open_box_tasks))
        
        # 合并结果
        msg = ''.join(results)

    print(msg)

    if '霸天虎' in msg:
        log_push += '⭕⭕⭕\n有账号成功开出 霸天虎，离永久雷诺不远了\n⭕⭕⭕\n'
    if '公牛' in msg:
        log_push += '⭕⭕⭕\n有账号成功开出 公牛，离永久雷诺不远了\n⭕⭕⭕\n'
    if '雷诺' in msg:
        log_push += '⭕⭕⭕\n有账号成功开出 永久雷诺，少年终于圆梦成功\n⭕⭕⭕\n'

    if sendnoty:
        try:
            if len(log_push) > 0:
                print(log_push)
                send('掌上飞车开金丝篓', log_push)
        except Exception as err:
            print('%s\n❌错误，请查看运行日志！' % err)

    return msg[:-1] if msg else ''


if __name__ == "__main__":
    print("⭕⭕⭕\n并发执行开箱，接口无法避免频繁现象，百分百会出现”开箱失败“，根据情况自己适当增加开箱次数\n⭕⭕⭕")
    print("----------掌上飞车开始尝试开金丝篓----------")
    main()
    print("----------掌上飞车开金丝篓执行完毕----------")
