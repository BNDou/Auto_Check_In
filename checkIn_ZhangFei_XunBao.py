'''
new Env('掌上飞车每日寻宝')
cron: 10 0 * * *
Author       : BNDou
Date         : 2023-02-21 01:09:51
LastEditTime : 2023-12-19 1:09:20
FilePath     : /Auto_Check_In/checkIn_ZhangFei_XunBao.py
Description  :
感谢@chiupam(https://github.com/chiupam)寻宝脚本

⭕⭕①每日登录掌上飞车可获得3次寻宝机会   （此接口无法对接）
⭕⭕②紫钻玩家可额外获得1次            （自行开紫钻）
⭕⭕③每日登录游戏可获得1次寻宝机会     （有条件的上号就行）

没次数的注意这个官方规则，你之所以上号看到有次数，是因为已经触发了规则①，此时再运行就可以寻宝了
建议启动前先领取5次机会，或者开紫钻每天直接获取1次机会

抓包流程：
(推荐)
开启抓包-进入签到页面-等待上方账号信息加载出来-停止抓包
选请求这个url的包-https://speed.qq.com/lbact/

(抓不到的话)
可以选择抓取其他页面的包，前提是下面8个值一个都不能少

添加环境变量COOKIE_ZHANGFEI，多账号用回车换行分开
只需要添加8个值即可，分别是
roleId=QQ号; userId=掌飞社区ID号; accessToken=xxx; appid=xxx; openid=xxx; areaId=xxx; token=xxx; speedqqcomrouteLine=xxx;

其中
speedqqcomrouteLine就是签到页的url中间段，即http://speed.qq.com/lbact/xxxxxxxxxx/zfmrqd.html中的xxxxxxxxxx部分
token进入签到页（url参数里面有）或者进入寻宝页（Referer里面会出现）都能获取到
'''
import json
import os
import re
import sys
import threading
import time
from urllib.parse import unquote

import requests

from checkIn_ZhangFei_Login import check

sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n❌加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    if "COOKIE_ZHANGFEI" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_ZHANGFEI').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('❌COOKIE_ZHANGFEI变量未启用')
            send('掌上飞车每日寻宝', '❌COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('❌未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车每日寻宝', '❌未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


# 寻宝
def dig(status, user_data):
    url = f"https://bang.qq.com/app/speed/treasure/ajax/{status}DigTreasure"
    headers = {
        "Referer": "https://bang.qq.com/app/speed/treasure/index",
        "Cookie": f"access_token={user_data.get('accessToken')}; "
                  f"acctype=qc; "
                  f"appid={user_data.get('appid')}; "
                  f"openid={user_data.get('openid')}"
    }
    data = {
        "mapId": user_data.get('mapId'),  # 地图Id
        "starId": user_data.get('starId'),  # 地图星级Id
        "areaId": user_data.get('areaId'),  # 1是电信区，2是联通
        "type": user_data.get('type'),  # 1是普通寻宝，2是快速寻宝（紫钻用户）
        "roleId": user_data.get('roleId'),  # QQ号
        "userId": user_data.get('userId'),  # 掌飞号
        "uin": user_data.get('roleId'),  # QQ号
        "token": user_data.get('token')
    }
    response = requests.post(url, headers=headers, data=data)

    return False if response.json()['res'] == 0 else True


# 领取奖励
def get_treasure(iFlowId, user_data):
    url = "https://act.game.qq.com/ams/ame/amesvr?ameVersion=0.3&iActivityId=468228"
    headers = {
        "Cookie": f"access_token={user_data.get('accessToken')}; "
                  f"acctype=qc; "
                  f"appid={user_data.get('appid')}; "
                  f"openid={user_data.get('openid')}"
    }
    data = {
        'appid': user_data.get('appid'),
        'sArea': user_data.get('areaId'),
        'sRoleId': user_data.get('roleId'),
        'accessToken': user_data.get('accessToken'),
        'iActivityId': "468228",
        'iFlowId': iFlowId,
        'g_tk': '1842395457',
        'sServiceType': 'bb'
    }
    response = requests.post(url, headers=headers, data=data)
    response.encoding = "utf-8"

    return ("✅" + str(response.json()['modRet']['sPackageName'])) if response.json()[
                                                                         'ret'] == '0' else '❌非常抱歉，您还不满足参加该活动的条件！'


# 今日大吉筛选
def luck_day(user_data):
    t = f"🚗账号 {user_data.get('roleId')}"

    def extract(_html, _pattern):
        match = re.search(_pattern, _html)
        if match:
            return json.loads(re.sub(r'^\((.*)\)$', r'\1', match.group(1)))
        return None

    url = "https://bang.qq.com/app/speed/treasure/index"
    params = {
        "roleId": user_data.get('roleId'),  # QQ帐号，抓包抓取
        "areaId": user_data.get('areaId'),  # 1是电信区，抓包抓取
        "uin": user_data.get('roleId')  # QQ帐号，抓包抓取
    }

    response = requests.get(url, params=params)
    response.encoding = 'utf-8'
    user = extract(response.text, r'window\.userInfo\s*=\s*eval\(\'([^\']+)\'\);')
    # 剩余寻宝次数
    left_times = re.search(r'id="leftTimes">(\d+)</i>', response.text).group(1)

    if user:
        vip_flag = bool(user.get('vip_flag'))
        print(f"{t}💎紫钻用户：{'是' if vip_flag else '否'}")
        starId = max([key for key, value in user.get('starInfo', {}).items() if value == 1])
        print(f"{t}⭐最高地图解锁星级：{starId}")
    else:
        print(t, "❌未找到用户信息")

    if starId:
        map_dicts = extract(response.text, r'window\.mapInfo\s*=\s*eval\(\'([^\']+)\'\);')
        luck_dicts = [item for item in map_dicts[starId] if item.get('isdaji') == 1]
        mapId, mapName = (luck_dicts[0]['id'], luck_dicts[0]['name']) if luck_dicts else (False, False)
        print(f"{t}🌏今日大吉地图是[{mapName}]-地图ID是[{mapId}]")
    else:
        print(t, "❌未找到地图信息")

    print("{}⏰剩余寻宝次数：{}".format(t, left_times))

    return 2 if vip_flag == True else 1, starId, mapId, left_times


# 创建锁
lock = threading.RLock()


# 开始任务
def run(user_data):
    sendnoty = 'true'
    msg = ""
    t = f"🚗账号 {user_data.get('roleId')}"
    log = f"{t} {'电信区' if user_data.get('areaId') == '1' else '联通区' if user_data.get('areaId') == '2' else '电信2区'}"
    msg += log + '\n'
    lock.acquire()
    print(f"{log} 开始执行任务")
    lock.release()

    # 检查token是否过期
    if not check(user_data, "XunBao"):
        return

    # 获取紫钻信息、地图解锁信息
    user_data['type'], user_data['starId'], user_data['mapId'], user_data['left_times'] = luck_day(user_data)
    # 星级地图对应的iFlowId
    iFlowId_dict = {'1': ['856152', '856155'], '2': ['856156', '856157'], '3': ['856158', '856159'],
                    '4': ['856160', '856161'], '5': ['856162', '856163'], '6': ['856164', '856165']}

    if user_data['left_times'] != "0":
        # 每日5次寻宝
        for n in range(5):
            n += 1
            # 寻宝
            if dig('start', user_data):
                msg += f"❌第{n}次寻宝...对不起，当天的寻宝次数已用完\n"
                lock.acquire()
                print(f"{t}❌第{n}次寻宝...对不起，当天的寻宝次数已用完")
                lock.release()
                break
            msg += f"✅第{n}次寻宝...\n"
            lock.acquire()
            print(f"{t}✅第{n}次寻宝...")
            lock.release()

            # 寻宝倒计时
            if user_data['type'] == 2:
                lock.acquire()
                print(f"{t}🔎等待10秒寻宝时间...")
                lock.release()
                time.sleep(10)
            else:
                lock.acquire()
                print(f"{t}🔎等待十分钟寻宝时间...")
                lock.release()
                time.sleep(600)

            # 结束寻宝
            if not dig('end', user_data):
                lock.acquire()
                print(f"{t}✅结束寻宝...")
                lock.release()

            # 领取奖励
            for iflowid in iFlowId_dict[user_data['starId']]:
                log = get_treasure(iflowid, user_data)
                msg += log + '\n'
                lock.acquire()
                print(f"{t}{log}")
                lock.release()
    else:
        print(f"{t}❌对不起，当天的寻宝次数已用完")

    if sendnoty:
        lock.acquire()
        try:
            send('掌上飞车每日寻宝', msg)
        except Exception as err:
            print('%s\n❌错误，请查看运行日志！' % err)
        lock.release()


if __name__ == "__main__":
    print("----------掌上飞车开始尝试每日寻宝----------")

    thread = []
    global cookie_zhangfei
    cookie_zhangfei = get_env()

    print("✅检测到共", len(cookie_zhangfei), "个飞车账号\n")

    i = 0
    while i < len(cookie_zhangfei):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_zhangfei[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a.split('=')[0]: unquote(a.split('=')[1])})

        # 传个任务,和参数进来
        thread.append(threading.Thread(target=run, args=[user_data]))

        i += 1

    for t in thread:
        t.start()
    for t in thread:
        t.join()

    print("----------掌上飞车每日寻宝执行完毕----------")
