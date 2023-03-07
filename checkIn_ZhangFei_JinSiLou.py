'''
new Env('掌上飞车-0点开金丝篓')
cron: 0 0 * * *
Author       : BNDou
Date         : 2022-12-28 23:58:11
LastEditTime : 2023-03-07 22:17:22
FilePath     : /Auto_Check_In/checkIn_ZhangFei_JinSiLou.py
Description  : 端游 金丝篓开永久雷诺
添加zhangFei_jinSiLouNum变量于config.sh用于控制开启金丝篓个数，变量为整数
添加环境变量COOKIE_ZHANGFEI、REFERER_ZHANGFEI、USER_AGENT_ZHANGFEI，多账号用回车换行分开
值分别是cookie、referer和User-Agent
'''
from urllib.parse import unquote
import requests
import os
import sys
sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['zhangFei_jinSiLouNum'] = ''
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
            send('掌上飞车开金丝篓', 'COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车开金丝篓', '未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    # 判断 REFERER_ZHANGFEI是否存在于环境变量
    if "REFERER_ZHANGFEI" in os.environ:
        referer_list = os.environ.get('REFERER_ZHANGFEI').split('\n')
        if len(referer_list) <= 0:
            print('REFERER_ZHANGFEI变量未启用')
            send('掌上飞车开金丝篓', 'REFERER_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加REFERER_ZHANGFEI变量')
        send('掌上飞车开金丝篓', '未添加REFERER_ZHANGFEI变量')
        sys.exit(0)

    # 判断 USER_AGENT_ZHANGFEI是否存在于环境变量
    if "USER_AGENT_ZHANGFEI" in os.environ:
        userAgent = os.environ.get('USER_AGENT_ZHANGFEI')
        if len(userAgent) <= 0:
            print('USER_AGENT_ZHANGFEI变量未启用')
            send('掌上飞车开金丝篓', 'USER_AGENT_ZHANGFEI变量未启用')
            sys.exit(1)
    else:
        print('未添加USER_AGENT_ZHANGFEI变量')
        send('掌上飞车开金丝篓', '未添加USER_AGENT_ZHANGFEI变量')
        sys.exit(0)

    # 判断 金丝篓开启个数 变量zhangFei_jinSiLouNum是否存在于环境变量
    if "zhangFei_jinSiLouNum" in os.environ:
        if len(os.environ.get('zhangFei_jinSiLouNum')) <= 0 or int(os.environ.get('zhangFei_jinSiLouNum')) == 0:
            print(
                '使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n直接在config.sh添加export zhangFei_jinSiLouNum=**\n变量为整数')
            send('掌上飞车开金丝篓', '使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n直接在config.sh添加export zhangFei_jinSiLouNum=**\n变量为大于零的整数')
            sys.exit(1)
    else:
        print('使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n直接在config.sh添加export zhangFei_jinSiLouNum=**\n变量为整数')
        send('掌上飞车开金丝篓', '使用请添加zhangFei_jinSiLouNum变量控制开启金丝篓个数\n直接在config.sh添加export zhangFei_jinSiLouNum=**\n变量为大于零的整数')
        sys.exit(0)

    return cookie_list, referer_list, userAgent


# 开箱子
def openBox(cookie, user_data):
    msg = ''
    s = requests.Session()
    s.headers.update({'User-Agent': user_data.get('userAgent')})

    url = "https://bang.qq.com/app/speed/chest/ajax/openBoxByKey"
    headers = {
        'User-Agent': user_data.get('userAgent'),
        'Connection': 'keep-alive',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'Referer': f"https://bang.qq.com/app/speed/chest/index/v2?uin={user_data.get('roleId')}&roleId={user_data.get('roleId')}&uniqueRoleId={user_data.get('uniqueRoleId')}&accessToken={user_data.get('accessToken')}&userId={user_data.get('userId')}&token={user_data.get('token')}&areaId={user_data.get('areaId')}&",
        'Cookie': cookie
    }

    # 生成表单
    data = {
        'userId': user_data.get('userId'),  # 掌飞id
        'uin': user_data.get('roleId'),  # QQ账号
        'areaId': user_data.get('areaId'),  # 大区
        'token': user_data.get('token'),  # 令牌
        'keyId1': '17456',  # 大闸蟹17456
        'keyNum1': '2',  # 1个金丝篓开2个大闸蟹
        'boxId': '17455',  # 金丝篓17455
        'openNum': '1'  # 1个金丝篓开2个大闸蟹
    }

    # 延迟2秒执行，防止频繁
    # time.sleep(2)

    r = s.post(url=url, data=data, headers=headers)
    a = r.json()
    # 是否成功
    if 'data' in a:
        if 'itemList' in a.get('data'):
            itemList = a.get('data').get('itemList')
            num = 0
            for num in range(len(itemList)):
                msg += f"{itemList[num].get('avtarname')} * {itemList[num].get('num')} "
                print(
                    f"{itemList[num].get('avtarname')} * {itemList[num].get('num')}")
                num += 1

        if 'msg' in a.get('data'):
            msg += a.get('data').get('msg')
            print(a.get('data').get('msg'))

    return msg


def main(*arg):
    msg = ""
    log_push = ""
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
            print(f"第 {i+1} 个账号 {user_data.get('uin')} {user_data.get('roleName')} {'端游' if 'speed' == user_data.get('game') else '手游'} 暂无开道具")
        user_data.update({'userAgent': userAgent})
        # print(user_data)

        # 开始任务
        print(
            f"第 {i+1} 个账号 {user_data.get('uin')} {user_data.get('roleName')} 开始执行任务")

        # 开金丝篓
        num = 0
        for num in range(int(os.environ.get('zhangFei_jinSiLouNum'))):
            print(f"开第{num+1}个：")

            # 开箱子
            log = openBox(cookie_zhangfei[i].replace(' ', ''), user_data)
            msg += log + '\n'
            if '不足' in log:
                break

        if '霸天虎' in msg:
            log_push += '\n❗❗❗❗❗❗\n成功开出 霸天虎，离永久雷诺不远了\n❗❗❗❗❗❗\n'
            print('\n❗❗❗❗❗❗\n成功开出 霸天虎，离永久雷诺不远了\n❗❗❗❗❗❗\n')
        if '公牛' in msg:
            log_push += '\n❗❗❗❗❗❗\n成功开出 公牛，离永久雷诺不远了\n❗❗❗❗❗❗\n'
            print('\n❗❗❗❗❗❗\n成功开出 公牛，离永久雷诺不远了\n❗❗❗❗❗❗\n')
        if '雷诺' in msg:
            log_push += '\n❗❗❗❗❗❗\n成功开出 永久雷诺，少年终于圆梦成功\n❗❗❗❗❗❗\n'
            print('\n❗❗❗❗❗❗\n成功开出 永久雷诺，少年终于圆梦成功\n❗❗❗❗❗❗\n')
        i += 1

    if sendnoty:
        try:
            if len(log_push) > 0:
                send('掌上飞车开金丝篓', log_push)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('掌上飞车开金丝篓', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车开始尝试开金丝篓----------")
    main()
    print("----------掌上飞车开金丝篓执行完毕----------")
