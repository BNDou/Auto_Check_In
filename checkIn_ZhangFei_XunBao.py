'''
new Env('掌上飞车每日寻宝')
cron: 0 0 * * *
Author       : BNDou
Date         : 2023-02-21 01:09:51
LastEditTime : 2023-03-07 21:52:33
FilePath     : /Auto_Check_In/checkIn_ZhangFei_XunBao.py
Description  : 启动寻宝后最少需要10秒领取，所以建议时间定到开奖时间前10秒运行
测试用，目前只能！！！开始和结束！！！\n领取奖励报错不能用！！！浪费次数不负责哦

添加环境变量ZHANGFEI_XUNBAO、COOKIE_ZHANGFEI、REFERER_ZHANGFEI、USER_AGENT_ZHANGFEI，多账号用回车换行分开
'''
import re
import time
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 自定义寻宝地图星级: 1 2 3 4 5 6（必须是已解锁的）
MAP_STARID = ''
# 测试用环境变量
# os.environ['ZHANGFEI_XUNBAO'] = ''
# os.environ['COOKIE_ZHANGFEI'] = ''
# os.environ['REFERER_ZHANGFEI'] = ''
# os.environ['USER_AGENT_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 ZHANGFEI_XUNBAO是否存在于环境变量
    if "ZHANGFEI_XUNBAO" in os.environ:
        # 判断变量是否为空
        if len(os.environ.get('ZHANGFEI_XUNBAO')) <= 0:
            # 标准日志输出
            print('测试用，目前只能！！！开始和结束！！！\n领取奖励报错不能用！！浪费次数不负责哦\n使用请添加ZHANGFEI_XUNBAO变量')
            send(
                '掌上飞车每日寻宝', '测试用，目前只能！！！开始和结束！！！\n领取奖励报错不能用！！浪费次数不负责哦\n使用请添加ZHANGFEI_XUNBAO变量')
            # 脚本退出
            sys.exit(0)

    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    if "COOKIE_ZHANGFEI" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_ZHANGFEI').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_ZHANGFEI变量未启用')
            send('掌上飞车每日寻宝', 'COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车每日寻宝', '未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

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

    # 判断 USER_AGENT_ZHANGFEI是否存在于环境变量
    if "USER_AGENT_ZHANGFEI" in os.environ:
        userAgent = os.environ.get('USER_AGENT_ZHANGFEI')
        if len(userAgent) <= 0:
            print('USER_AGENT_ZHANGFEI变量未启用')
            send('掌上飞车每日寻宝', 'USER_AGENT_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加USER_AGENT_ZHANGFEI变量')
        send('掌上飞车每日寻宝', '未添加USER_AGENT_ZHANGFEI变量')
        sys.exit(0)

    return cookie_list, referer_list, userAgent


# 定义一个获取url页面下label标签的attr属性的函数
def getHtml(url):
    count_list = []
    giftId_list = []
    date_list = []
    response = requests.get(url)
    response.encoding = 'utf-8'
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')

    for target in soup.find_all('span'):
        try:
            value = target.text
        except:
            value = ''
        if value:
            count_list.append(value)

    for target in soup.find_all('a'):
        try:
            value = target.get('giftid')
        except:
            value = ''
        if value:
            giftId_list.append(value)

    for target in soup.find_all('div'):
        try:
            if 'text2' in target.get('class'):
                value = target.text
            else:
                value = ''
        except:
            value = ''
        if value:
            date_list.append(value)

    return count_list, giftId_list, date_list


# 快速寻宝-10s
def startDigTreasure(cookie, user_data):
    msg = ""
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = 'https://bang.qq.com/app/speed/treasure/ajax/startDigTreasure'
    headers = {
        'User-Agent': user_data.get('userAgent'),
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': f"https://bang.qq.com/app/speed/treasure/index?uin={user_data.get('roleId')}&roleId={user_data.get('roleId')}&uniqueRoleId={user_data.get('uniqueRoleId')}&accessToken={user_data.get('accessToken')}&userId={user_data.get('userId')}&token={user_data.get('token')}&areaId={user_data.get('areaId')}&",
        'Cookie': cookie
    }

    # 生成表单
    data = {
        'userId': user_data.get('userId'),  # 掌飞id
        'uin': user_data.get('uin'),  # QQ账号
        'roleId': user_data.get('roleId'),  # QQ账号
        'areaId': user_data.get('areaId'),  # 大区
        'token': user_data.get('token'),  # 令牌
        'mapId': user_data.get('mapId'),  # 地图id
        'starId': user_data.get('starId'),  # 地图星级id
        'type': '2',  # 1普通寻宝 or 2快速寻宝
        'game': user_data.get('game')  # 端游 or 手游
    }

    r = s.post(url=url, data=data, headers=headers)
    a = r.json()
    # 是否成功
    if 'msg' in a:
        msg += a.get('msg', '')

    return msg


# 结束寻宝
def endDigTreasure(cookie, user_data):
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = "https://bang.qq.com/app/speed/treasure/ajax/endDigTreasure"
    headers = {
        'User-Agent': user_data.get('userAgent'),
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': f"https://bang.qq.com/app/speed/treasure/index?uin={user_data.get('roleId')}&roleId={user_data.get('roleId')}&uniqueRoleId={user_data.get('uniqueRoleId')}&accessToken={user_data.get('accessToken')}&userId={user_data.get('userId')}&token={user_data.get('token')}&areaId={user_data.get('areaId')}&",
        'Cookie': cookie
    }

    # 生成表单
    data = {
        'userId': user_data.get('userId'),  # 掌飞id
        'uin': user_data.get('uin'),  # QQ账号
        'roleId': user_data.get('roleId'),  # QQ账号
        'areaId': user_data.get('areaId'),  # 大区
        'token': user_data.get('token'),  # 令牌
        'mapId': user_data.get('mapId'),  # 地图id
        'starId': user_data.get('starId'),  # 地图星级id
        'type': '2',  # 1普通寻宝 or 2快速寻宝
        'game': user_data.get('game')  # 端游 or 手游
    }

    r = s.post(url=url, data=data, headers=headers)
    a = r.json()
    # 是否成功
    if 'msg' in a:
        msg += a.get('msg', '')

    return msg


# 领取奖励
def getGift(cookie, user_data):
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = "http://act.game.qq.com/ams/ame/amesvr?ameVersion=0.3& =bb&iActivityId=468228&sServiceDepartment=xinyue&sSDID=42a6eb3c5e2fec32f90c3b085368457a&sMiloTag=AMS-MILO-468228-856162-3CCD3D9E40083C0B4A9EB2BE6F073116-1676831452329-d5zK3l&_=1676831452333"
    headers = {
        'User-Agent': user_data.get('userAgent'),
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie,
    }

    # 生成表单
    data = {
        'sRoleId':	user_data.get('roleId'),  # QQ账号
        'accessToken':	user_data.get('accessToken'),  # 访问令牌
        'iActivityId':	'468228',
        'iFlowId':	'856162',
        'g_tk':	'1842395457',
        'game': user_data.get('game')  # 端游 or 手游
    }

    r = s.post(url=url, data=data, headers=headers)
    a = r.json()
    # # 是否成功
    if 'modRet' in a:
        if 'sMsg' in a.get('modRet'):
            msg += a.get('msg', '')
    else:
        msg += a.get('msg', '')

    return msg


# 今日大吉筛选
def isdaji(user_data):
    response = requests.get(
        f"https://bang.qq.com/app/speed/treasure/index?uin={user_data.get('roleId')}&roleId={user_data.get('roleId')}&uniqueRoleId={user_data.get('uniqueRoleId')}&accessToken={user_data.get('accessToken')}&userId={user_data.get('userId')}&token={user_data.get('token')}&areaId={user_data.get('areaId')}&")
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    tagList = soup.find_all("script")
    for tag in tagList:
        # 获取用户地图解锁信息
        if 'window.userInfo' in tag.text:
            userInfo = re.findall(
                r"window.userInfo = eval\(\'\((.*?)\)\'\);", tag.text)
            # print(userInfo)
        # 获取地图信息
        if 'window.mapInfo' in tag.text:
            mapInfo = re.findall(
                r"window.mapInfo = eval\(\'\((.*?)\)\'\);", tag.text)
            # print(mapInfo)
            break

    # 星级地图解锁信息
    starInfo = eval(userInfo[0].encode(
        'utf-8').decode('unicode_escape'))['starInfo']
    for i in range(6):
        starId = 6 - i
        if starInfo[f'{starId}'] == 1:
            print(f'最高地图解锁星级[{starId}]')
            break

    if MAP_STARID:
        starId = MAP_STARID
        print(f'自定义寻宝星级[{starId}]')
    else:
        print(f'默认最高寻宝星级[{starId}]，如需自定义请修改变量MAP_STARID的值!')

    # 大吉地图信息
    daji = eval(mapInfo[0].encode(
        'utf-8').decode('unicode_escape'))[f'{starId}']
    for i in daji:
        if i['isdaji'] == 1:
            mapId = i['id']
            mapName = i['name']
            print(f'今日大吉地图是[{mapName}] 地图id是[{mapId}]')
            break

    return starId, mapId


def main(*arg):
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    global referer_zhangfei
    cookie_zhangfei, referer_zhangfei, userAgent = get_env()

    i = 0
    while i < len(cookie_zhangfei):
        # 获取user_data参数
        user_data = {}
        for a in referer_zhangfei[i].split('?')[1].split('&'):
            if len(a) > 0:
                user_data.update(
                    {a.split('=')[0]: unquote(a.split('=')[1])})
        if 'speedm' in referer_zhangfei[i]:
            user_data.update({'game': 'speedm'})  # 手游
        else:
            user_data.update({'game': 'speed'})  # 端游
        user_data.update({'userAgent': userAgent})
        # print(user_data)

        # 开始任务
        log = f"第 {i+1} 个账号 {user_data.get('uin')} {user_data.get('roleName')} {'端游' if 'speed' == user_data.get('game') else '手游'} 开始执行任务"
        msg += log + '\n'
        print(log)
        # 设置寻宝地图星级: 1 2 3 4 5 6（必须是已解锁的）
        user_data['starId'], user_data['mapId'] = isdaji(user_data)

        # 每日5次寻宝
        for n in range(5):
            n += 1
            # 快速寻宝
            log = startDigTreasure(
                cookie_zhangfei[i].replace(' ', ''), user_data)
            print(f"第{n}次寻宝：" + log)

            # 10s后结束寻宝
            print("等待11秒寻宝时间...")
            time.sleep(11)

            # 结束寻宝
            log = endDigTreasure(
                cookie_zhangfei[i].replace(' ', ''), user_data)
            print(f"结束寻宝：" + log)

            # 领取奖励
            log = getGift(cookie_zhangfei[i].replace(' ', ''), user_data)
            msg += f"第{n}次寻宝：" + log + '\n'
            print(f"领取奖励：" + log)

        i += 1

    if sendnoty:
        try:
            send('掌上飞车每日寻宝', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('掌上飞车每日寻宝', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车开始尝试每日寻宝----------")
    main()
    print("----------掌上飞车每日寻宝执行完毕----------")
