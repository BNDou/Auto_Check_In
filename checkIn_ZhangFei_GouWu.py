'''
new Env('掌上飞车购物')
cron: 50 23 * * *
Author       : BNDou
Date         : 2023-11-7 01:11:27
LastEditTime : 2023-11-01 2:26:10
FilePath     : /Auto_Check_In/checkIn_ZhangFei_GouWu.py
Description  :每日定时执行消费券购物，月末执行点券+消费券购物

除了设置下面cookie，还需要另外添加购物脚本需要的变量“zhangFei_shopName”
直接在config.sh添加例如export zhangFei_shopName="进气系统+1"  变量值为掌飞商城道具名全称，设为需要购买的商品名称

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
import calendar
import datetime
import os
import re
import sys
from urllib.parse import unquote

import requests

sys.path.append('.')
requests.packages.urllib3.disable_warnings()

# 测试用环境变量
# os.environ['zhangFei_shopName'] = ""
# os.environ['COOKIE_ZHANGFEI'] = ""

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
            send('掌上飞车购物', 'COOKIE_ZHANGFEI变量未启用')
            # 脚本退出
            sys.exit(1)
    else:
        # 标准日志输出
        print('未添加COOKIE_ZHANGFEI变量')
        send('掌上飞车购物', '未添加COOKIE_ZHANGFEI变量')
        # 脚本退出
        sys.exit(0)

    # 判断 设置商品名称 变量zhangFei_shopName是否存在于环境变量
    if "zhangFei_shopName" in os.environ:
        if len(os.environ.get('zhangFei_shopName')) <= 0:
            print('使用请添加zhangFei_shopName变量设置需要购买的商品名称')
            print('直接在config.sh添加，例如export zhangFei_shopName="进气系统+1"\n变量值为掌飞商城道具名全称')
            send('掌上飞车购物',
                 '使用请添加zhangFei_shopName变量设置需要购买的商品名称\n直接在config.sh添加，例如export zhangFei_shopName="进气系统+1"\n变量值为掌飞商城道具名全称')
            sys.exit(1)
    else:
        print('使用请添加zhangFei_shopName变量设置需要购买的商品名称')
        print('直接在config.sh添加，例如export zhangFei_shopName="进气系统+1"\n变量值为掌飞商城道具名全称')
        send('掌上飞车购物',
             '使用请添加zhangFei_shopName变量设置需要购买的商品名称\n直接在config.sh添加，例如export zhangFei_shopName="进气系统+1"\n变量值为掌飞商城道具名全称')
        sys.exit(0)

    return cookie_list


# 获取点券、消费券信息
def getPackInfo(user_data, argument):
    # 创建一个空对象，用于存储点券和消费券信息
    purse = {}

    # 根据参数值设置状态文本
    statu = "当前" if (argument == "before") else "剩余"

    url = f"https://bang.qq.com/app/speed/mall/main2"
    # 获取 url 中的查询参数
    params = {
        'uin': user_data.get('roleId'),
        'userId': user_data.get('userId'),
        'areaId': user_data.get('areaId'),
        'token': user_data.get('token'),
    }
    response = requests.get(url, params)
    response.encoding = "utf-8"

    # 使用正则表达式匹配点券和消费券数量
    purse['money'] = re.findall(r'<b id="super_money">(\d+)<', response.text)[0]
    purse['coupons'] = re.findall(r'<b id="coupons">(\d+)<', response.text)[0]

    return purse


def process_data(input_dict):
    item = input_dict['szItems'][0]
    if item['ItemNum'] == "":
        mapping = {
            "4320,720,": "180,30",
            "4320,720,-1,": "180,30,99999999",
            "720,168,-1,": "30,7,99999999",
            "168,720,-1,": "7,30,99999999",
            "-1,": "99999999"
        }
        item['ItemNum'] = mapping.get(item['ItemAvailPeriod'], "")
    price_idx = {
        item_num: {
            "index": str(i),
            "price": int(price['SuperMoneyPrice'])
        } for i, (item_num, price) in enumerate(zip(item.get('ItemNum', '180,30').split(','), input_dict['szPrices']))
    }
    output_dict = {
        input_dict['szName']: {
            "commodity_id": input_dict['iId'],
            "price_idx": sorted(price_idx.items(), key=lambda x: int(x[0]), reverse=True),  # 道具可购买数量和价格由高到低排序
            "unit": "个" if item['ItemNum'] else "天"
        }
    }

    return output_dict


# 获取商城列表
def getMallList(user_data):
    url = "https://bang.qq.com/app/speed/mall/getItemListByPage"
    headers = {
        "Referer": "https://bang.qq.com/app/speed/mall/main2",
    }
    base_params = {
        "uin": user_data.get('roleId'),
        "userId": user_data.get('userId'),
        "token": user_data.get('token'),
        "paytype": 1,  # paytype为1时order选择2则是按点券筛选，paytype为0时order选择1则是按新品筛选
        "sex": 1,  # 角色性别，1男性，2女性
        "order": 2  # paytype为1时order选择2则是按点券筛选，paytype为0时order选择1则是按新品筛选
    }
    # 查询赛车、功能、宠物，服装除外
    for typeValue in (2, 4, 5):
        params = base_params.copy()
        params["type"] = typeValue
        for startValue in range(0, 18000, 18):
            params["start"] = startValue
            response = requests.post(url, headers=headers, params=params)
            # 获取完毕时退出
            if not response.json()['data']:
                break
            for input_dict in response.json()['data']:
                output_dict = process_data(input_dict)
                print(output_dict)


# 搜索商品信息
def searchShop(user_data, shopName):
    url = f"https://bang.qq.com/app/speed/mall/search"
    params = {
        "uin": user_data.get('roleId'),
        "userId": user_data.get('userId'),
        "token": user_data.get('token'),
        "start": "0",
        "paytype": "1",  # 按点券筛选
        "order": "2",  # 按点券筛选
        "text": shopName
    }
    headers = {"Referer": "https://bang.qq.com/app/speed/mall/main2"}

    response = requests.post(url, params=params, headers=headers)
    response.encoding = "utf-8"

    # 获取完毕时退出
    if len(response.json()['data']) == 1:
        return process_data(response.json()['data'][0])
    else:
        print(f"❗❗❗检测道具”{shopName}“在商店中未售卖或不唯一，请在掌飞商城中认真核对商品名全称")
        return None


# 检查当天是否是本月的最后一天
def is_last_day_of_month():
    # 获取今天的日期
    today = datetime.datetime.now()
    # 判断今天的日期是否等于本月的最大天数，即最后一天
    return today.day == calendar.monthrange(today.year, today.month)[1]


# 根据当前余额和道具价格生成购物列表
def getShopItems(itme_data, purse):
    # 初始化总购物数量和购物列表
    money = int(purse['money']) + int(purse['coupons']) if is_last_day_of_month() else int(purse['coupons'])
    total = 0
    shopArray = []

    for item in itme_data:
        i = 0
        while i < len(itme_data[item]['price_idx']):
            # 商品数量索引
            shopIdx = itme_data[item]['price_idx'][i][0]

            # 如果购买的商品可以购买永久且当前余额可以购买永久
            if itme_data[item]['price_idx'][i][0] == "99999999" and money > itme_data[item]['price_idx'][i][1]['price']:
                shopArray.append({"name": item, "count": "99999999", "commodity_id": itme_data[item]['commodity_id'],
                                  "price_idx": shopIdx})
                itme_data[item]['unit'] = "永久"
                break

            # 计算当前余额可以购买的最大道具数量
            # 这是一个计算出的整数，表示根据当前余额和道具价格，最多可以购买的道具数量
            maxCounts = money // itme_data[item]['price_idx'][i][1]['price']
            # 这是一个累加的变量，用于跟踪购买的总道具数量
            total += maxCounts * int(itme_data[item]['price_idx'][i][0])
            # 这是当前可用的余额。在每次购买道具后，余额会根据购买的道具数量和价格进行更新，以反映购买后的余额
            money -= maxCounts * itme_data[item]['price_idx'][i][1]['price']

            if maxCounts:
                # 将可购买的道具添加到购物列表
                m = 0
                while m < maxCounts:
                    shopArray.append(
                        {"name": item, "count": itme_data[item]['price_idx'][i][0],
                         "commodity_id": itme_data[item]['commodity_id'],
                         "price_idx": shopIdx})
                    m += 1

            # 如果当前余额不足以购买最便宜的道具，跳出循环
            if money < itme_data[item]['price_idx'][len(itme_data[item]['price_idx']) - 1][1]['price']:
                break

            i += 1

        return shopArray, total, itme_data[item]['unit']


# 购买道具
def getPurchase(user_data, buyInfo):
    total = 0
    url = "https://bang.qq.com/app/speed/mall/getPurchase"
    headers = {"Referer": "https://bang.qq.com/app/speed/mall/detail2"}
    data = {
        "uin": user_data.get('roleId'),
        "userId": user_data.get('userId'),
        "areaId": user_data.get('areaId'),
        "token": user_data.get('token'),
        "pay_type": "1",
        "commodity_id": buyInfo['commodity_id'],
        "price_idx": buyInfo['price_idx']
    }
    response = requests.post(url, headers=headers, data=data)
    response.encoding = "utf-8"

    if "恭喜购买成功" in response.json()['msg']:
        total = buyInfo['count']
    else:
        print(f"❗❗❗{response.json()['msg']}")

    return total


def main():
    msg = ""
    sendnoty = 'true'
    global cookie_zhangfei
    cookie_zhangfei = get_env()
    day = datetime.datetime.now().strftime('%m月%d日')

    i = 0
    while i < len(cookie_zhangfei):
        # 获取user_data参数
        user_data = {}  # 用户信息
        for a in cookie_zhangfei[i].replace(" ", "").split(';'):
            if not a == '':
                user_data.update({a.split('=')[0]: unquote(a.split('=')[1])})
        # print(user_data)

        # 开始任务
        # 获取当前点券、消费券
        purse = getPackInfo(user_data, "before")
        log = f"第 {i + 1} 个账号 {user_data.get('roleId')} {'电信区' if user_data.get('areaId') == '1' else '联通区' if user_data.get('areaId') == '2' else '电信2区'} 开始执行任务\n截至{day}共有 {purse['money']}点券 {purse['coupons']}消费券"
        msg += log + '\n'
        print(log)

        # 搜索商品信息
        itme_data = searchShop(user_data, os.environ.get('zhangFei_shopName'))
        # 获取商城列表
        # getMallList(user_data)
        # 生成购物车列表
        shopArray, total, unit = getShopItems(itme_data, purse)
        # 开始购买循环
        if shopArray:
            log = f"预计可购买{total if total == 0 else ''}{unit} {os.environ.get('zhangFei_shopName')}\n"
            print(log)
            successBuyCounts = 0
            failedBuyCounts = 0

            # 购买道具
            for buyInfo in shopArray:
                # 成功统计
                successBuyCounts += getPurchase(user_data, buyInfo)
            # 失败统计
            failedBuyCounts = total - (1 if successBuyCounts == 99999999 else successBuyCounts)
            #
            if successBuyCounts > 0:
                successBuyCounts = "" if successBuyCounts == 99999999 else successBuyCounts
                log = f"成功购买{successBuyCounts}${unit}${os.environ.get('zhangFei_shopName')}\n"
                if failedBuyCounts > 0:
                    log = f"未购买成功{failedBuyCounts}${unit}\n"
            else:
                log = f"全部购买失败，共计{total if total == 0 else ''}{unit}\n"
            msg += log
            print(log)
        else:
            log = f"{'本月余额' if isLastDays() else '今日消费券'}不足以购买{os.environ.get('zhangFei_shopName')}\n"
            msg += log
            print(log)

        i += 1

    if sendnoty:
        try:
            send('掌上飞车购物', msg)
        except Exception as err:
            print('%s\n错误，请查看运行日志！' % err)
            send('掌上飞车购物', '%s\n错误，请查看运行日志！' % err)

    return msg[:-1]


if __name__ == "__main__":
    print("----------掌上飞车尝试购物----------")
    main()
    print("----------掌上飞车购物完毕----------")
