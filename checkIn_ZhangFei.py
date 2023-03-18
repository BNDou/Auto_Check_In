'''
new Env('掌上飞车签到')
cron: 10 0 * * *
Author       : BNDou
Date         : 2022-12-02 19:03:27
LastEditTime : 2023-03-18 23:03:43
FilePath     : /Auto_Check_In/checkIn_ZhangFei.py
Description  : 支持端游、手游双端的签到和领取
添加环境变量COOKIE_ZHANGFEI、REFERER_ZHANGFEI、USER_AGENT_ZHANGFEI，多账号用回车换行分开
值分别是cookie、referer和User-Agent
'''
import datetime
import time
from urllib.parse import unquote
from bs4 import BeautifulSoup
import requests
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['COOKIE_ZHANGFEI'] = ''
# os.environ['REFERER_ZHANGFEI'] = ''
# os.environ['USER_AGENT_ZHANGFEI'] = ''

try:  # 异常捕捉
    from sendNotify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n加载通知服务失败~' % err)


# 获取环境变量
def get_env():
    # 判断 COOKIE_ZHANGFEI是否存在于环境变量
    if "COOKIE_ZHANGFEI" in os.environ:
        # 读取系统变量 以 \n 分割变量
        cookie_list = os.environ.get('COOKIE_ZHANGFEI').split('\n')
        # 判断 cookie 数量 大于 0 个
        if len(cookie_list) <= 0:
            # 标准日志输出
            print('COOKIE_ZHANGFEI变量未启用')
            send('掌上飞车签到', 'COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车签到', '未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    # 判断 REFERER_ZHANGFEI是否存在于环境变量
    if "REFERER_ZHANGFEI" in os.environ:
        referer_list = os.environ.get('REFERER_ZHANGFEI').split('\n')
        if len(referer_list) <= 0:
            print('REFERER_ZHANGFEI变量未启用')
            send('掌上飞车签到', 'REFERER_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加REFERER_ZHANGFEI变量')
        send('掌上飞车签到', '未添加REFERER_ZHANGFEI变量')
        sys.exit(0)

    # 判断 USER_AGENT_ZHANGFEI是否存在于环境变量
    if "USER_AGENT_ZHANGFEI" in os.environ:
        userAgent = os.environ.get('USER_AGENT_ZHANGFEI')
        if len(userAgent) <= 0:
            print('USER_AGENT_ZHANGFEI变量未启用')
            send('掌上飞车签到', 'USER_AGENT_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加USER_AGENT_ZHANGFEI变量')
        send('掌上飞车签到', '未添加USER_AGENT_ZHANGFEI变量')
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


# 签到
def checkIn(cookie, user_data, giftid):
    msg = ""
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = f"https://mwegame.qq.com/ams/sign/doSign/month?userId={user_data.get('userId')}&uin={user_data.get('uin')}&roleId={user_data.get('roleId')}&uniqueRoleId={user_data.get('uniqueRoleId')}&areaId={user_data.get('areaId')}&accessToken={user_data.get('accessToken')}&token={user_data.get('token')}&gift_id={giftid}&game={user_data.get('game')}"
    headers = {
        'User-Agent': user_data.get('userAgent'),
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie
    }

    r = s.get(url=url, headers=headers, timeout=120)
    rjson = r.json()
    msg += rjson.get('message', '')
    if 'send_result' in rjson:
        msg += '\n' + rjson.get('send_result').get('sMsg', '')

    return msg


# 累计签到奖励
def getGift(cookie, count_list, giftId_list, user_data):
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = "https://mwegame.qq.com/ams/send/handle"
    headers = {
        'User-Agent': user_data.get('userAgent'),
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Cookie': cookie,
    }

    num = 3
    for num in range(len(count_list)-3):
        # 累计签到天数是否足够，否则退出
        if int(count_list[1])+1 < int(count_list[num+3]):
            break

        # 生成表单
        data = {
            'userId': user_data.get('userId'),  # 掌飞id
            'uin': user_data.get('uin'),  # QQ账号
            'toUin': user_data.get('toUin'),  # QQ账号
            'roleId': user_data.get('roleId'),  # QQ账号
            'uniqueRoleId': user_data.get('uniqueRoleId'),  # 唯一角色id
            'areaId': user_data.get('areaId'),  # 大区
            'accessToken': user_data.get('accessToken'),  # 访问令牌
            'token': user_data.get('token'),  # 令牌
            'gift_id': giftId_list[num+1],  # 礼物id（第一个是签到用）
            'game': user_data.get('game'),  # 端游 or 手游
            'openid': user_data.get('openid')
        }

        # 延迟2秒执行，防止频繁
        time.sleep(2)

        r = s.post(url=url, data=data, headers=headers)
        a = r.json()
        # 是否成功
        if 'status' in a:
            if a.get('status') == 1:
                msg += '累计签到' + count_list[num+3] + '天的礼物:' + \
                    giftId_list[num+1] + ' ' + a.get('data', '') + '\n'
                print('累计签到' + count_list[num+3] + '天的礼物:' +
                      giftId_list[num+1] + ' ' + a.get('data', ''))
                if 'send_result' in a:
                    msg += a.get('send_result').get('sMsg', '') + '\n'
                    print(a.get('send_result').get('sMsg', ''))
            else:
                print('累计签到' + count_list[num+3] + '天的礼物:' +
                      giftId_list[num+1] + ' ' + a.get('message', ''))

    return msg


# 特别福利
def getGiftDays(cookie, count_list, giftId_list, user_data):
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = "https://mwegame.qq.com/ams/send/handle"
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
        'userId': user_data.get('userId'),  # 掌飞id
        'uin': user_data.get('uin'),  # QQ账号
        'toUin': user_data.get('toUin'),  # QQ账号
        'roleId': user_data.get('roleId'),  # QQ账号
        'uniqueRoleId': user_data.get('uniqueRoleId'),  # 唯一角色id
        'areaId': user_data.get('areaId'),  # 大区
        'accessToken': user_data.get('accessToken'),  # 访问令牌
        'token': user_data.get('token'),  # 令牌
        'gift_id': giftId_list[len(count_list)-2],  # 礼物id
        'game': user_data.get('game')  # 端游 or 手游
    }

    # 延迟2秒执行，防止频繁
    time.sleep(2)

    r = s.post(url=url, data=data, headers=headers)
    a = r.json()
    # 是否成功
    if 'status' in a:
        if a.get('status') == 1:
            msg += f"今日{datetime.datetime.now().strftime('%m月%d日')}特殊福利:{a.get('data', '')}\n"
            print(
                f"今日{datetime.datetime.now().strftime('%m月%d日')}特殊福利:{a.get('data', '')}")
            if 'send_result' in a:
                msg += a.get('send_result').get('sMsg', '') + '\n'
                print(a.get('send_result').get('sMsg', '') + '\n')
        else:
            print(f"今日{datetime.datetime.now().strftime('%m月%d日')}特殊福利 已领取过\n")

    return msg


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
        user_data.update({'userAgent': userAgent})  # 端游
        # print(user_data)
        # 获取累计信息、奖励信息、特别福利日期
        count_list, giftId_list, date_list = getHtml(referer_zhangfei[i])

        # 开始任务
        log = f"第 {i+1} 个账号 {user_data.get('uin')} {user_data.get('roleName')} {'端游' if 'speed' == user_data.get('game') else '手游'} 开始执行任务"
        msg += log + '\n' + count_list[0] + \
            ' 已累计签到' + count_list[1] + '天\n'
        print(log)
        print(count_list[0] + ' 已累计签到' + count_list[1] +
              '天\n当月礼物有:' + str(giftId_list))

        # 签到
        log = checkIn(cookie_zhangfei[i].replace(
            ' ', ''), user_data, giftId_list[0])
        msg += f"今日{datetime.datetime.now().strftime('%m月%d日')} " + \
            log + '\n'
        print(f"今日{datetime.datetime.now().strftime('%m月%d日')} " + log)

        # 累计签到奖励
        log = getGift(cookie_zhangfei[i].replace(
            ' ', ''), count_list, giftId_list, user_data)
        if len(log) > 0:
            msg += log

        # 特别福利
        if date_list:
            if datetime.datetime.now().strftime('%m月%d日') == date_list[0]:
                log = getGiftDays(cookie_zhangfei[i].replace(
                    ' ', ''), count_list, giftId_list, user_data)
                msg += log + '\n'
            else:
                log = f"今日{datetime.datetime.now().strftime('%m月%d日')}无特殊福利礼物\n"
                print(log)
                msg += log + '\n'
        else:
            log = "本月特别福利已领取完^!^"
            print(log)
            msg += log + '\n'

        i += 1

    if sendnoty:
        try:
            send('掌上飞车签到', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('掌上飞车签到', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车开始尝试签到----------")
    main()
    print("----------掌上飞车签到执行完毕----------")
