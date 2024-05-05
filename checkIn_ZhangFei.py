'''
new Env('掌上飞车签到')
cron: 10 0 * * *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime: 2024-05-06 01:58:02
FilePath: \Auto_Check_In\checkIn_ZhangFei.py
Description  :
抓包流程：
(推荐)
开启抓包-进入签到页面-等待上方账号信息加载出来-停止抓包
选请求这个url的包-https://speed.qq.com/cp/

(抓不到的话)
可以选择抓取其他页面的包，前提是下面8个值一个都不能少

添加环境变量COOKIE_ZHANGFEI，多账户用 回车 或 && 分开
只需要添加8个值即可，分别是
roleId=QQ号; userId=掌飞社区ID号; accessToken=xxx; appid=xxx; openid=xxx; areaId=xxx; token=xxx; speedqqcomrouteLine=xxx;

其中
speedqqcomrouteLine就是签到页的url中间段，即https://speed.qq.com/cp/xxxxxxxxxx/index.html中的xxxxxxxxxx部分（每月更新一次）
token进入签到页（url参数里面有）或者进入寻宝页（Referer里面会出现）都能获取到
'''
from datetime import datetime as datetime
import os
import re
import sys
from urllib.parse import unquote

import requests

from checkIn_ZhangFei_Login import check

# 测试用环境变量
# os.environ['COOKIE_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n❌加载通知服务失败~' % err)


def get_env():
    '''
    获取环境变量
    :return: 环境变量
    '''
    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    if "COOKIE_ZHANGFEI" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_ZHANGFEI'))
    else:
        # 标准日志输出
        print('❌未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车签到', '❌未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


def get_signIn(user_data):
    '''
    获取签到信息
    :param user_data: 用户信息
    '''
    flow = requests.get(
        f"https://speed.qq.com/cp/{user_data['speedqqcomrouteLine']}/index.js")
    html = flow.text

    # 获取签到信息
    flow_strings = re.findall(r"Milo.emit\(flow_(\d+)\)", html)
    # 累计信息id
    total_id = flow_strings[1]
    user_data.update({"total_id": total_id})
    # 周签到
    week_signIn = flow_strings[2:10]
    user_data.update({"week_signIn": week_signIn})
    # 月签到
    month_SignIn = flow_strings[10:15]
    user_data.update({"month_SignIn": month_SignIn})
    # 任务信息
    task_id = flow_strings[-5:]
    user_data.update({"task_id": task_id})
    # 获取活动ID: iActivityId
    iactivityid = re.findall(r"actId: '(\d+)'", html)[0]
    user_data.update({"iActivityId": iactivityid})


def commit(user_data, sData):
    '''
    提交签到信息
    :param user_data: 用户信息
    :param sData: 签到信息
    :return: 提交结果
    '''
    url = f"https://comm.ams.game.qq.com/ams/ame/amesvr?iActivityId={user_data.get('iActivityId')}"
    headers = {
        'Cookie':
        f"access_token={user_data.get('accessToken')}; "
        f"acctype=qc; "
        f"appid={user_data.get('appid')}; "
        f"openid={user_data.get('openid')}; "
    }

    if sData[0] == "witchDay":  # 累计信息
        iFlowId = user_data.get('total_id')
    elif sData[0] == "number":  # 补签
        iFlowId = user_data.get('week_signIn')[-1:]
    elif sData[0] == "":
        if sData[1] == "":  # 签到
            iFlowId = user_data.get('week_signIn')[datetime.now().weekday()]
        else:  # 月签
            iFlowId = user_data.get('month_SignIn')[sData[1]]

    data = {
        "iActivityId": user_data.get('iActivityId'),
        "iFlowId": iFlowId,
        "g_tk": "1842395457",
        "sServiceType": "speed",
        sData[0]: sData[1]
    }

    response = requests.post(url, headers=headers, data=data)
    response.encoding = "utf-8"

    return response.json()


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    cookie_zhangfei = get_env()

    print("✅检测到共", len(cookie_zhangfei), "个飞车账号")

    i = 0
    while i < len(cookie_zhangfei):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_zhangfei[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a.split('=')[0]: unquote(a.split('=')[1])})
        # print(user_data)

        # 获取签到信息
        get_signIn(user_data)

        # 开始任务
        log = f"\n🚗第 {i + 1} 个账号 {user_data.get('roleId')} {'电信区' if user_data.get('areaId') == '1' else '联通区' if user_data.get('areaId') == '2' else '电信2区'}"
        msg += log + '\n'
        print(f"{log} 开始执行任务...")

        # 获取累计信息
        ret = commit(user_data, ['witchDay', (datetime.now().weekday() + 1)])
        if ret['ret'] == '101':
            # 登录失败
            log = f"❌账号{user_data.get('roleId')}登录失败，请检查账号信息是否正确"
            msg += log + '\n'
            print(log)
            i += 1
            continue
        modRet = ret['modRet']

        # 本周已签到天数
        weekSignIn = modRet['sOutValue5']

        # 周补签（资格剩余）
        if (datetime.now().weekday() + 1) < 3:
            weekSupplementarySignature = "0"
        else:
            weekBuqian = modRet['sOutValue7'].split(',')
            if int(weekBuqian[1]) == 1:
                # 已经使用资格
                weekSupplementarySignature = "0"
            else:
                if int(weekBuqian[0]) >= 3:
                    weekSupplementarySignature = "1"
                else:
                    weekSupplementarySignature = "0"

        # 本月已签到天数
        monthSignIn = modRet['sOutValue4']
        if int(monthSignIn) > 25:
            monthSignIn = "25"

        log = f"本周签到{weekSignIn}/7天，本月签到{monthSignIn}/25天，有{weekSupplementarySignature}天可补签"
        msg += log + '\n'
        print(log)

        # 签到
        ret = commit(user_data, ['', ''])
        log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(
            ret['flowRet']['sMsg'])
        if "网络故障" in log:
            log = f"❌今日{datetime.now().strftime('{}月%d日').format(datetime.now().month)} 星期{datetime.now().weekday() + 1} 已签到"
        else:
            log = f"✅今日{datetime.now().strftime('{}月%d日').format(datetime.now().month)} 星期{datetime.now().weekday() + 1} {log}"
        msg += log + '\n'
        print(log)

        # 补签
        weekStatue = modRet['sOutValue2'].split(',')
        if weekSupplementarySignature == "1":
            for index, value in enumerate(weekStatue):
                if value == "1":
                    if (datetime.now().weekday() + 1) < index + 1:
                        print(f"星期{index + 1} 未领取")
                    elif (datetime.now().weekday() + 1) > index + 1:
                        # 补签
                        ret = commit(user_data, ['number', (index + 1)])
                        log = str(ret['modRet']
                                  ['sMsg']) if ret['ret'] == '0' else str(
                                      ret['flowRet']['sMsg'])
                        msg += f"✅补签：{log}\n"
                        print(f"✅补签：{log}")
                else:
                    print(f"星期{index + 1} 签到已领取")
        else:
            print("本周补签资格已用完")

        # 月签（资格剩余）
        monthStatue = modRet['sOutValue1'].split(',')
        # 可领取的月签奖励
        if int(monthSignIn) >= 5:
            if int(monthStatue[0]) == 0:
                print("可以领取第一个月签奖励，这个功能暂时还没做")
                ret = commit(user_data, ['', 0])
                log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(
                    ret['flowRet']['sMsg'])
                log = f"✅累计签到5天：{log}"
                msg += log + '\n'
                print(log)
            else:
                print("本月签到已达到5天，已领取第一个月签奖励")
        else:
            print("本月签到未达到5天，无法领取奖励")
        if int(monthSignIn) >= 10:
            if int(monthStatue[1]) == 0:
                print("可以领取第二个月签奖励，这个功能暂时还没做")
                ret = commit(user_data, ['', 1])
                log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(
                    ret['flowRet']['sMsg'])
                log = f"✅累计签到5天：{log}"
                msg += log + '\n'
                print(log)
            else:
                print("本月签到已达到10天，已领取第二个月签奖励")
        else:
            print("本月签到未达到10天，无法领取奖励")
        if int(monthSignIn) >= 15:
            if int(monthStatue[2]) == 0:
                print("可以领取第三个月签奖励，这个功能暂时还没做")
                ret = commit(user_data, ['', 2])
                log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(
                    ret['flowRet']['sMsg'])
                log = f"✅累计签到5天：{log}"
                msg += log + '\n'
                print(log)
            else:
                print("本月签到已达到15天，已领取第三个月签奖励")
        else:
            print("本月签到未达到15天，无法领取奖励")
        if int(monthSignIn) >= 20:
            if int(monthStatue[3]) == 0:
                print("可以领取第四个月签奖励，这个功能暂时还没做")
                ret = commit(user_data, ['', 3])
                log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(
                    ret['flowRet']['sMsg'])
                log = f"✅累计签到5天：{log}"
                msg += log + '\n'
                print(log)
            else:
                print("本月签到已达到20天，已领取第四个月签奖励")
        else:
            print("本月签到未达到20天，无法领取奖励")
        if int(monthSignIn) >= 25:
            if int(monthStatue[4]) == 0:
                print("可以领取第五个月签奖励，这个功能暂时还没做")
                ret = commit(user_data, ['', 4])
                log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(
                    ret['flowRet']['sMsg'])
                log = f"✅累计签到5天：{log}"
                msg += log + '\n'
                print(log)
            else:
                print("本月签到已达到25天，已领取第五个月签奖励")
        else:
            print("本月签到未达到25天，无法领取奖励")

        i += 1

    if sendnoty:
        try:
            send('掌上飞车签到', msg)
        except Exception as err:
            print('%s\n❌错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车开始尝试签到----------")
    main()
    print("----------掌上飞车签到执行完毕----------")
