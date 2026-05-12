'''
new Env('掌上飞车-0点开金丝篓')
cron: 59 59 23 * * *
Author       : BNDou
Date         : 2022-12-28 23:58:11
LastEditTime : 2026-05-13 00:10:27
FilePath: \Auto_Check_In\checkIn_ZhangFei_JinSiLou.py
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
    role_id = user_data.get('roleId', 'unknown')
    result = "  "  # 添加账号标识，便于日志区分
    try:
        r = requests.post(url=url, headers=headers, data=data, timeout=15)
        a = r.json()

        # 是否成功
        if 'data' in a:
            if 'itemList' in a.get('data'):
                item_list = a.get('data').get('itemList')
                for item in item_list:
                    result += f"✅{item.get('avtarname')}*{item.get('num')} "
            if 'msg' in a.get('data'):
                # 失败信息单独一行，避免与成功结果混在一起
                result += f"❌开箱失败: {a.get('data').get('msg')}"
        else:
            result = f"❌开箱异常: {a}"
    except Exception as e:
        result = f"❌开箱异常: {str(e)}"
    return result


# token验证（返回True=有效，False=失效；错误信息通过返回值传递，不直接打印）
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

    # 返回(状态, 错误信息)，不在此打印，统一由调用方处理日志
    return (True, "") if response_json['returnMsg'] == "" else (False, response_json['returnMsg'])


def main(*arg):
    """主函数"""
    msg = ""
    log_push = ""
    sendnoty = 'true'
    cookie_zhangfei = get_env()

    print("✅检测到共", len(cookie_zhangfei), "个飞车账号\n")

    # 准备所有开箱任务
    open_box_tasks = []
    # 记录每个任务对应的roleId（用于结果分组）
    task_role_ids = []

    i = 0
    while i < len(cookie_zhangfei):
        role_id = ""  # 用于日志展示
        user_data = {}
        for a in cookie_zhangfei[i].replace(" ", "").split(';'):
            if not a == '':
                parts = a.split('=', 1)
                user_data.update({parts[0]: unquote(parts[1])})
                if parts[0] == 'roleId':
                    role_id = parts[1]

        # 检查token是否过期
        check_result = check(user_data)
        if not check_result[0]:  # 登录态失效
            print(f"❌账号 {role_id} 登录态失效，请重新登录 | {check_result[1]}")
            i += 1
            continue

        # 有效账号，开金丝篓
        box_count = int(os.environ.get('zhangFei_jinSiLouNum'))
        print(f"✅账号 {role_id} 登录态有效，开始开金丝篓 x{box_count}")
        for num in range(box_count):
            open_box_tasks.append(user_data)
            task_role_ids.append(role_id)
        i += 1

    # 使用ThreadPoolExecutor并发执行
    if open_box_tasks:
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(open_box, open_box_tasks))

        # 按账号分组汇总结果
        role_results = {}
        for idx, r in enumerate(results):
            rid = task_role_ids[idx]
            if rid not in role_results:
                role_results[rid] = []
            role_results[rid].append(r)

        # 输出格式化日志
        print("\n" + "=" * 40)
        print("📋 开箱结果汇总")
        print("=" * 40)
        for rid, r_list in role_results.items():
            print(f"\n【账号 {rid}】")
            for r in r_list:
                print(f"  {r}")
        print("\n" + "=" * 40)

        # 汇总推送消息
        msg = "".join(results)
    else:
        print("\n⚠️ 无有效账号可开金丝篓")
        msg = ""

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
