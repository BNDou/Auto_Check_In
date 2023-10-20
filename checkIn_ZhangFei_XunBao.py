'''
new Env('掌上飞车每日寻宝')
cron: 10 0 * * *
Author       : BNDou
Date         : 2023-02-21 01:09:51
LastEditTime : 2023-10-20 14:39:33
FilePath     : /Auto_Check_In/checkIn_ZhangFei_XunBao.py
Description  :
感谢@chiupam(https://github.com/chiupam)寻宝脚本

每日登录掌上飞车可获得3次寻宝机会，紫钻玩家可额外获得1次，每日登录游戏可获得1次寻宝机会，共5次
建议启动前先领取5次机会
浪费次数不负责哦

添加环境变量REFERER_ZHANGFEI，多账号用回车换行分开

访问寻宝页面时候抓包获取Referer,即环境变量REFERER_ZHANGFEI的值
'''
import json
import os
import re
import sys
import threading
import time
from urllib.parse import unquote

import requests

sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
os.environ['REFERER_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 REFERER_ZHANGFEI是否存在于环境变量
    if "REFERER_ZHANGFEI" in os.environ:
        referer_list = os.environ.get('REFERER_ZHANGFEI').split('\n')
        if len(referer_list) <= 0:
            print('REFERER_ZHANGFEI变量未启用')
            send('掌上飞车每日寻宝', 'REFERER_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加REFERER_ZHANGFEI变量')
        send('掌上飞车每日寻宝', '未添加REFERER_ZHANGFEI变量')
        sys.exit(0)

    return referer_list


# 寻宝
def dig(status, user_data):
    # 只需要抓 https://bang.qq.com/app/speed/treasure/ajax/startDigTreasure 包就可以获取了
    url = f"https://bang.qq.com/app/speed/treasure/ajax/{status}DigTreasure"
    headers = {
        "Referer": "https://bang.qq.com/app/speed/treasure/index",
        "Cookie": f"access_token={user_data.get('accessToken')}; "
                  f"acctype={user_data.get('accType')}; "
                  f"appid={user_data.get('appid')}; "
                  f"openid={user_data.get('appOpenid')}"
    }
    data = {
        "mapId": user_data.get('mapId'),  # 地图Id
        "starId": user_data.get('starId'),  # 地图星级Id
        "areaId": user_data.get('areaId'),  # 1是电信区，2是联通
        "type": user_data.get('type'),  # 1是普通寻宝，2是快速寻宝（紫钻用户）
        "roleId": user_data.get('roleId'),  # QQ号
        "userId": user_data.get('userId'),  # 掌飞号
        "uin": user_data.get('uin'),  # QQ号
        "token": user_data.get('token')
    }
    response = requests.post(url, headers=headers, data=data)

    return False if response.json()['res'] == 0 else True


# 领取奖励
def get_treasure(iFlowId, user_data):
    url = "https://act.game.qq.com/ams/ame/amesvr?ameVersion=0.3&iActivityId=468228"
    headers = {
        "Cookie": f"access_token={user_data.get('accessToken')}; "
                  f"acctype={user_data.get('accType')}; "
                  f"appid={user_data.get('appid')}; "
                  f"openid={user_data.get('appOpenid')}"
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

    return str(response.json()['modRet']['sMsg']) if response.json()['ret'] == '0' else '非常抱歉，您还不满足参加该活动的条件！'


# 今日大吉筛选
def luck_day(user_data):
    # 这里只需要填写查询的QQ号就行
    def extract(_html, _pattern):
        match = re.search(_pattern, _html)
        if match:
            return json.loads(re.sub(r'^\((.*)\)$', r'\1', match.group(1)))
        return None

    url = "https://bang.qq.com/app/speed/treasure/index"
    params = {
        "roleId": user_data.get('roleId'),  # QQ帐号，抓包抓取
        "areaId": user_data.get('areaId'),  # 1是电信区，抓包抓取
        "uin": user_data.get('uin')  # QQ帐号，抓包抓取
    }

    response = requests.get(url, params=params)
    response.encoding = 'utf-8'
    user = extract(response.text, r'window\.userInfo\s*=\s*eval\(\'([^\']+)\'\);')

    if user:
        vip_flag = bool(user.get('vip_flag'))
        print("紫钻用户:", vip_flag)
        starId = max([key for key, value in user.get('starInfo', {}).items() if value == 1])
        print("最高地图解锁星级:", starId)
    else:
        print("未找到用户信息")

    if starId:
        map_dicts = extract(response.text, r'window\.mapInfo\s*=\s*eval\(\'([^\']+)\'\);')
        luck_dicts = [item for item in map_dicts[starId] if item.get('isdaji') == 1]
        mapId, mapName = (luck_dicts[0]['id'], luck_dicts[0]['name']) if luck_dicts else (False, False)
        print(f'今日大吉地图是[{mapName}] 地图id是[{mapId}]')
    else:
        print("未找到地图信息")

    return 2 if vip_flag == True else 1, starId, mapId


# 开始任务
lock = threading.RLock()  # 创建锁


def run(user_data):
    sendnoty = 'true'
    msg = ""
    log = f"账号 {user_data.get('uin')} {user_data.get('roleName')} {'电信区' if user_data.get('areaId') == '1' else '联通区' if user_data.get('areaId') == '2' else '电信2区'} 开始执行任务"
    msg += log + '\n'
    lock.acquire()
    print(log)
    lock.release()
    # 获取紫钻信息、地图解锁信息
    user_data['type'], user_data['starId'], user_data['mapId'] = luck_day(user_data)
    # 星级地图对应的iFlowId
    iFlowId_dict = {'1': ['856152', '856155'], '2': ['856156', '856157'], '3': ['856158', '856159'],
                    '4': ['856160', '856161'], '5': ['856162', '856163'], '6': ['856164', '856165']}

    # 每日5次寻宝
    for n in range(5):
        n += 1
        # 寻宝
        if dig('start', user_data):
            msg += f"第{n}次寻宝...对不起，当天的寻宝次数已用完\n"
            lock.acquire()
            print(f"第{n}次寻宝...对不起，当天的寻宝次数已用完")
            lock.release()
            break
        msg += f"第{n}次寻宝...\n"
        lock.acquire()
        print(f"第{n}次寻宝...")
        lock.release()

        # 寻宝倒计时
        if user_data['type'] == 2:
            lock.acquire()
            print("等待10秒寻宝时间...")
            lock.release()
            time.sleep(10)
        else:
            lock.acquire()
            print("等待十分钟寻宝时间...")
            lock.release()
            time.sleep(600)

        # 结束寻宝
        if not dig('end', user_data):
            lock.acquire()
            print('结束寻宝...')
            lock.release()

        # 领取奖励
        for iflowid in iFlowId_dict[user_data['starId']]:
            log = get_treasure(iflowid, user_data)
            msg += log + '\n'
            lock.acquire()
            print(log)
            lock.release()

    if sendnoty:
        try:
            send('掌上飞车每日寻宝', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('掌上飞车每日寻宝', '%s\n错误，请查看运行日志！' % err)


# def main(*arg):
#
#
#     return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车开始尝试每日寻宝----------")

    thread = []
    global referer_zhangfei
    referer_zhangfei = get_env()

    i = 0
    while i < len(referer_zhangfei):
        # 获取user_data参数
        user_data = {}
        for a in referer_zhangfei[i].split('?')[1].split('&'):
            if len(a) > 0:
                user_data.update(
                    {a.split('=')[0]: unquote(a.split('=')[1])})
        # print(user_data)

        # 传个任务,和参数进来
        thread.append(threading.Thread(target=run, args=[user_data]))

        i += 1

    for t in thread:
        t.start()
    for t in thread:
        t.join()

    print("----------掌上飞车每日寻宝执行完毕----------")
