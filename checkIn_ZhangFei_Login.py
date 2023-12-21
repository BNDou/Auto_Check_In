'''
new Env('掌上飞车login')
cron: 0 0 * * *
Author       : BNDou
Date         : 2023/12/21 1:10
File         : checkIn_ZhangFei_Login.py
Software     : checkIn_test.py
Description  : 用于完成每日登录从而增加寻宝次数（仅限安卓，ios可能每天会变，会很不方便，还不如自己每天手动上号）

⭕⭕①每日登录掌上飞车可获得3次寻宝机会   （此接口无法对接）
⭕⭕②紫钻玩家可额外获得1次            （自行开紫钻）
⭕⭕③每日登录游戏可获得1次寻宝机会     （有条件的上号就行）

1环境变量COOKIE_ZHANGFEI同签到脚本
2环境变量zhangFei_login🚨🚨🚨这个包比较复杂不懂的就不要用这个脚本了🚨🚨🚨
    直接在config.sh添加，例如export zhangFei_login="xxx&&xxx"
    变量值为login时data数据包（十六进制转base64可以获取到）
    抓包流程：
        （小黄鸟/Fiddler都行）
        ①开启抓包-打开app-等待首页信息加载出来-停止抓包
        ②筛选这个url的包-https://api2.helper.qq.com/user/login
        ③data是加密的乱码的，把请求文件发到电脑用Fiddler打开，选HexView查看
        ④选中header后面的所有内容，也就是所有加密的data，注意这里双横线 -- 代表换行，data前面应该是有换行，不要选中这个符号，可能有空格，空格要选中
        ⑤右击Copy-Copy as Base64，此时复制到的就是环境变量zhangFei_login的值
        例图看：https://github.com/BNDou/Auto_Check_In/issues/34#issuecomment-1866609638

'''
import base64
import datetime
import os
import re
import sys
import time
from urllib.parse import unquote

import requests

# 测试用环境变量
# os.environ['zhangFei_login'] = ""
# os.environ['COOKIE_ZHANGFEI'] = ""

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
            send('掌上飞车login', '❌COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('❌未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车login', '❌未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    if "zhangFei_login" in os.environ:
        login_list = os.environ.get('zhangFei_login').split('&&')
        if len(login_list) <= 0:
            print(
                '❌使用请添加zhangFei_login变量设置login时data数据包（二进制转base64可以获取到,比较复杂不懂的就不要用这个脚本了）')
            print(
                '❌直接在config.sh添加，例如export zhangFei_login="xxx&&xxx"\n❌变量值为login时data数据包（二进制转base64可以获取到,比较复杂不懂的就不要用这个脚本了）\n多账户用&&分割')
            send('掌上飞车login',
                 '❌使用请添加zhangFei_login变量设置login时data数据包（二进制转base64可以获取到,比较复杂不懂的就不要用这个脚本了）\n❌直接在config.sh添加，例如export zhangFei_login="xxx&&xxx"\n❌变量值为login时data数据包（二进制转base64可以获取到,比较复杂不懂的就不要用这个脚本了）\n多账户用&&分割')
            sys.exit(1)
    else:
        print('❌使用请添加zhangFei_login变量设置login时data数据包（二进制转base64可以获取到）')
        print(
            '❌直接在config.sh添加，例如export zhangFei_login="xxx&&xxx"\n❌变量值为login时data数据包（二进制转base64可以获取到）')
        send('掌上飞车login',
             '❌使用请添加zhangFei_login变量设置login时data数据包（二进制转base64可以获取到）\n❌直接在config.sh添加，例如export zhangFei_login="xxx&&xxx"\n❌变量值为login时data数据包（二进制转base64可以获取到）')
        sys.exit(0)

    return cookie_list, login_list


# 登录
def login(login_data):
    url = "https://api2.helper.qq.com/user/login"
    headers = {
        "x-online-host": "api2.helper.qq.com",
        "Accept-Encrypt": "",
        "Gh-Header": "2-1-1003-2103090010-335257132",
        "Content-Encrypt": "",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 13; Mi 10 Build/TKQ1.221114.001)",
        "Content-Type": "application/octet-stream",
        "Content-Length": "912",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }

    # response = requests.post(url, headers=headers, data=base64.b64decode(postData))
    # responseData = base64.b64encode(response.content).decode('utf-8')
    # print(responseData)

    requests.post(url, headers=headers, data=base64.b64decode(login_data))

    try:
        return "YES"
    except Exception as err:
        return "NO"


# token验证
def check(user, branch):
    url = "https://api2.helper.qq.com/report/checklogswitch"
    body = {
        "gameId": "1003",
        "cSystem": "iOS",
        "cGameId": "1003",
        "userId": user.get("userId"),
        "token": user.get("token")
    }

    response = requests.post(url, data=body)
    response_json = response.json()
    # print(response_json)

    if branch == "Login":
        return True if response_json['returnMsg'] == "" else False
    elif "GouWu" or "JinSiLou" or "XunBao":
        if response_json['returnMsg'] != "":
            print("❌账号 {}".format(user.get("userId")), response_json['returnMsg'], "可更新token后重试")

    return True if response_json['returnMsg'] == "" else False


# 剩余寻宝次数
def get_left_times():
    url = "https://bang.qq.com/app/speed/treasure/index"
    params = {
        "roleId": user_data.get('roleId'),  # QQ帐号，抓包抓取
        "areaId": user_data.get('areaId'),  # 1是电信区，抓包抓取
        "uin": user_data.get('roleId')  # QQ帐号，抓包抓取
    }
    response = requests.get(url, params=params)
    response.encoding = 'utf-8'

    return re.search(r'id="leftTimes">(\d+)</i>', response.text).group(1)


if __name__ == '__main__':
    msg = ""
    cookie_zhangfei, login_list = get_env()

    print("----------掌上飞车尝试login----------")

    print("✅检测到共", len(login_list),
          "个掌飞账号login\n每天只成功一次,多试无效\n因为是用寻宝次数的先后变化判断是否登录成功\n")

    i = 0
    while i < len(login_list):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_zhangfei[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a.split('=')[0]: unquote(a.split('=')[1])})
        # print(user_data)

        t = f"🚗账号 {user_data.get('roleId')} token {'有效' if check(user_data, 'Login') else '失效'}"

        # 寻宝次数查询
        left_times_before = get_left_times()
        log = f"{t}\n{datetime.datetime.now().strftime('%m月%d日 %H:%M:%S')} 寻宝次数有：{left_times_before}"
        msg += log + "\n"
        print(log)

        # 登录
        log = f"开始登录... {login(login_list[i])}"
        msg += log + "\n"
        print(log)

        # 等待1秒验证
        time.sleep(1)

        # 验证
        left_times_after = get_left_times()
        log = f"{datetime.datetime.now().strftime('%m月%d日 %H:%M:%S')} 寻宝次数有：{left_times_after}"
        msg += log + "\n"
        print(log)

        if left_times_before != left_times_after:
            log = f"✅寻宝次数有变化,今日已成功登陆掌飞,data有效\n"
        else:
            log = f"❌寻宝次数无变化,可能已经登录过,可能data无效,可能延迟问题等待系统更新\n"
        msg += log + "\n"
        print(log)

        i += 1

    try:
        send('掌上飞车login', msg)
    except Exception as err:
        print('%s\n❌错误，请查看运行日志！' % err)

    print("----------掌上飞车login完毕----------")
