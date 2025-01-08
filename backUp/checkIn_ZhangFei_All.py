'''
new Env('掌上飞车全能版')
cron: 10 0 * * *
Author       : BNDou
Date         : 2025-01-09 01:38:32
LastEditTime : 2025-01-09 03:27:43
FilePath     : /Auto_Check_In/backUp/checkIn_ZhangFei_All.py
Description  : 掌上飞车签到+购物+寻宝一体化脚本

抓包说明：
(推荐方式)
开启抓包-进入签到页面-等待上方账号信息加载出来-停止抓包
选请求这个url的包-https://speed.qq.com/cp/

添加环境变量说明：
1. 基础Cookie变量(必需)：
COOKIE_ZHANGFEI，多账户用 回车 或 && 分开

Cookie参数说明：
1. 基础参数(必需)：
roleId=QQ号; userId=掌飞社区ID号; accessToken=xxx; appid=xxx; openid=xxx; areaId=xxx; token=xxx; speedqqcomrouteLine=xxx;

2. 功能控制参数(可选，默认均为false)：
enable_signin=true/false; - 签到功能
enable_shopping=true/false; - 购物功能
enable_treasure=true/false; - 寻宝功能

3. 购物功能参数(enable_shopping=true时必需)：
shopName=xxx; - 要购买的商品名称(掌飞商城里面的全称)
giftPackId=1-6; - 月签20和25天礼包选择，默认1
'''
import calendar
import datetime
import json
import os
import re
import sys
import threading
import time
from urllib.parse import unquote

import requests

try:
    from utils.sendNotify import send
except Exception as err:
    print(f'%s\n❌加载通知服务失败~' % err)

# 全局变量
isvip = 0  # 紫钻状态

class ZhangFeiUser:
    """掌上飞车用户类"""
    def __init__(self, cookie_str):
        self.user_data = {}
        # 解析cookie字符串到user_data
        for item in cookie_str.replace(" ", "").split(';'):
            if item:
                key, value = item.split('=')
                self.user_data[key] = unquote(value)
        
        # 设置功能控制参数默认值
        self.user_data.setdefault('enable_signin', 'false')
        self.user_data.setdefault('enable_shopping', 'false')
        self.user_data.setdefault('enable_treasure', 'false')
        self.user_data.setdefault('giftPackId', '1')
    
    def is_feature_enabled(self, feature):
        """检查功能是否启用"""
        return self.user_data.get(f'enable_{feature}', 'false').lower() == 'true'
    
    def get_account_info(self):
        """获取账号显示信息"""
        area_name = '电信区' if self.user_data.get('areaId') == '1' else '联通区' if self.user_data.get('areaId') == '2' else '电信2区'
        return f"🚗账号 {self.user_data.get('roleId')} {area_name}"

    def check_token(self, feature=""):
        """检查token是否有效"""
        url = "https://bang.qq.com/app/speed/treasure/index"
        params = {
            "roleId": self.user_data.get('roleId'),
            "areaId": self.user_data.get('areaId'),
            "uin": self.user_data.get('roleId')
        }
        try:
            response = requests.get(url, params=params)
            if "登录态失效" in response.text:
                print(f"❌账号{self.user_data.get('roleId')}登录失效，请重新获取token")
                return False
            return True
        except Exception as e:
            print(f"❌检查token时发生错误: {e}")
            return False

class SignIn:
    """签到功能类"""
    def __init__(self, user):
        self.user = user
        
    def get_sign_info(self):
        """获取签到信息"""
        try:
            flow = requests.get(
                f"https://speed.qq.com/cp/{self.user.user_data['speedqqcomrouteLine']}/index.js"
            )
            html = flow.text
            # 解析签到信息
            flow_strings = re.findall(r"Milo.emit\(flow_(\d+)\)", html)
            self.user.user_data.update({
                "total_id": flow_strings[1],
                "week_signIn": flow_strings[2:10],
                "month_SignIn": flow_strings[10:15],
                "task_id": flow_strings[-5:],
                "iActivityId": re.findall(r"actId: '(\d+)'", html)[0]
            })
            return True
        except Exception as e:
            print(f"❌获取签到信息失败: {e}")
            return False

    def commit(self, sData):
        """提交签到信息"""
        url = f"https://comm.ams.game.qq.com/ams/ame/amesvr?iActivityId={self.user.user_data.get('iActivityId')}"
        headers = {
            'Cookie': f"acctype=qc; access_token={self.user.user_data.get('accessToken')}; appid={self.user.user_data.get('appid')}; openid={self.user.user_data.get('openid')};"
        }
        
        # 根据不同类型设置iFlowId
        if sData[0] == "witchDay":  # 累计信息
            iFlowId = self.user.user_data.get('total_id')
        elif sData[0] == "signIn":  # 签到
            iFlowId = self.user.user_data.get('week_signIn')[datetime.datetime.now().weekday()]
        elif sData[0] == "number":  # 补签
            iFlowId = self.user.user_data.get('week_signIn')[-1]
        elif sData[0] == "giftPackId":  # 月签
            iFlowId = self.user.user_data.get('month_SignIn')[sData[-1]]
        elif sData[0] == "task_id":  # 任务
            iFlowId = self.user.user_data.get('task_id')[sData[1]]

        data = {
            "curl_userId": self.user.user_data.get('userId'),
            "curl_qq": self.user.user_data.get('roleId'),
            "curl_token": self.user.user_data.get('token'),
            "iActivityId": self.user.user_data.get('iActivityId'),
            "iFlowId": iFlowId,
            "g_tk": "1842395457",
            "sServiceType": "speed",
            sData[0]: sData[1]
        }

        response = requests.post(url, headers=headers, data=data)
        response.encoding = "utf-8"
        return response.json()

    def get_out_value(self):
        """获取累计信息"""
        ret = self.commit(['witchDay', (datetime.datetime.now().weekday() + 1)])
        if ret['ret'] == '101':
            print(f"❌账号{self.user.user_data.get('roleId')}登录失败，请检查账号信息是否正确")
            return False
        elif ret['ret'] == '700':
            print(f"❌账号{self.user.user_data.get('roleId')} 请确认 token 是否有效")
            return False
            
        modRet = ret['modRet']

        # 本周已签到天数
        self.user.user_data["weekSignIn"] = modRet['sOutValue5']

        # 周补签（资格剩余）
        if (datetime.datetime.now().weekday() + 1) < 3:
            weekSupplementarySignature = "0"
        else:
            weekBuqian = modRet['sOutValue7'].split(',')
            if int(weekBuqian[1]) == 1:
                weekSupplementarySignature = "0"  # 已经使用资格
            else:
                weekSupplementarySignature = "1" if int(weekBuqian[0]) >= 3 else "0"
                
        self.user.user_data["weekSupplementarySignature"] = weekSupplementarySignature

        # 周补签状态
        self.user.user_data["weekStatue"] = modRet['sOutValue2'].split(',')

        # 本月已签到天数
        monthSignIn = modRet['sOutValue4']
        if int(monthSignIn) > 25:
            monthSignIn = "25"
        self.user.user_data["monthSignIn"] = monthSignIn

        # 月签（资格剩余）
        self.user.user_data["monthStatue"] = modRet['sOutValue1'].split(',')

        return True

    def sign_in(self):
        """签到"""
        msg = ""
        try:
            ret = self.commit(['signIn', ''])
            log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(ret['flowRet']['sMsg'])
            if "网络故障" in log:
                log = f"❌今日{datetime.datetime.now().strftime('{}月%d日').format(datetime.datetime.now().month)} 星期{datetime.datetime.now().weekday() + 1} 已签到"
            elif "非常抱歉，请先登录！" in log:
                log = f"❌今日{datetime.datetime.now().strftime('{}月%d日').format(datetime.datetime.now().month)} 星期{datetime.datetime.now().weekday() + 1} 非常抱歉，请先登录！"
            else:
                log = f"✅今日{datetime.datetime.now().strftime('{}月%d日').format(datetime.datetime.now().month)} 星期{datetime.datetime.now().weekday() + 1} {log}"
        except Exception as err:
            log = f"❌签到失败~{err}"
        print(log)
        return log + "\n"

    def week_supplementary_signature(self):
        """补签"""
        msg = ""
        try:
            if self.user.user_data.get('weekSupplementarySignature') == "1":
                for index, value in enumerate(self.user.user_data.get('weekStatue')):
                    if value == "1":
                        if (datetime.datetime.now().weekday() + 1) < index + 1:
                            print(f"星期{index + 1} 未领取")
                        elif (datetime.datetime.now().weekday() + 1) > index + 1:
                            # 补签
                            ret = self.commit(['number', (index + 1)])
                            log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(ret['flowRet']['sMsg'])
                            msg += f"✅补签：{log}\n"
                            print(f"✅补签：{log}")
                    else:
                        print(f"星期{index + 1} 签到已领取")
            else:
                print("本周补签资格已用完")
        except Exception as err:
            msg = f"❌补签失败~{err}\n"
            print(msg)
        return msg

    def month_sign_in(self):
        """获取月签礼包"""
        msg = ""
        for index, day in enumerate([5, 10, 15, 20, 25]):
            if int(self.user.user_data.get('monthSignIn')) >= day:
                if int(self.user.user_data.get('monthStatue')[index]) == 0:
                    # 如果未设置，默认领取第一个礼包
                    giftPackId = self.user.user_data.get('giftPackId', '1')
                    # 领取礼包
                    ret = self.commit(['giftPackId', giftPackId, index])
                    log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(ret['flowRet']['sMsg'])
                    log = f"✅累计签到{day}天：{log}"
                    msg += log + '\n'
                    print(log)
                else:
                    print(f"本月签到已达到{day}天，已领取第{index + 1}个月签奖励")
            else:
                print(f"本月签到未达到{day}天，无法领取奖励")
        return msg

    def browse_backpack(self):
        """日常任务：浏览背包"""
        url = f"https://mwegame.qq.com/yoyo/dnf/phpgameproxypass"
        data = {
            "uin": self.user.user_data.get('roleId'),
            "userId": self.user.user_data.get('userId'),
            "areaId": self.user.user_data.get('areaId'),
            "token": self.user.user_data.get('token'),
            "service": "dnf_getspeedknapsack",
            "cGameId": "1003",
        }
        response = requests.post(url=url, data=data)
        response.encoding = "utf-8"
        return True if response.json()['returnMsg'] == '' else False

    def task_gift(self):
        """日常任务：领取奖励"""
        msg = ""
        for index in range(len(self.user.user_data.get('task_id'))):
            ret = self.commit(['task_id', index])
            if ret['ret'] == '0':
                log = str(ret['modRet']['sMsg'])
                log = f"✅日常任务{index + 1}：{log}"
                msg += log + '\n'
            else:
                log = str(ret['flowRet']['sMsg'])
                log = f"❌日常任务{index + 1}：{log}"
            print(log)
        return msg

    def execute(self):
        """执行签到任务"""
        msg = "签到\n"
        print(f"{self.user.get_account_info()} 开始执行签到任务...")
        
        # 获取签到信息
        if not self.get_sign_info():
            return msg + "❌获取签到信息失败\n"
            
        # 获取累计信息
        if not self.get_out_value():
            return msg + "❌获取累计信息失败\n"
            
        # 执行签到
        msg += self.sign_in()
        
        # 输出签到统计
        log = (f"本周签到{self.user.user_data.get('weekSignIn')}/7天，"
               f"本月签到{self.user.user_data.get('monthSignIn')}/25天，"
               f"有{self.user.user_data.get('weekSupplementarySignature')}天可补签")
        msg += log + "\n"
        print(log)
        
        # 补签
        week_msg = self.week_supplementary_signature()
        if week_msg:
            msg += week_msg
            
        # 领取月签奖励
        month_msg = self.month_sign_in()
        if month_msg:
            msg += month_msg
            
        # 日常任务：浏览背包
        if self.browse_backpack():
            msg += "✅日常任务：浏览背包成功\n"
            print("✅日常任务：浏览背包成功")
            
        # 日常任务：领取奖励
        task_msg = self.task_gift()
        if task_msg:
            msg += task_msg
            
        return msg

class Shopping:
    """购物功能类"""
    def __init__(self, user):
        self.user = user
        
    def get_pack_info(self):
        """获取点券、消费券信息"""
        url = f"https://bang.qq.com/app/speed/mall/main2"
        params = {
            'uin': self.user.user_data.get('roleId'),
            'userId': self.user.user_data.get('userId'),
            'areaId': self.user.user_data.get('areaId'),
            'token': self.user.user_data.get('token'),
        }
        response = requests.get(url, params=params)
        response.encoding = "utf-8"

        try:
            return {
                'money': re.findall(r'<b id="super_money">(\d+)<', response.text)[0],
                'coupons': re.findall(r'<b id="coupons">(\d+)<', response.text)[0]
            }
        except IndexError:
            print("❌获取点券、消费券信息失败")
            return None

    def process_data(self, input_dict):
        """格式化道具信息"""
        global isvip
        if isvip > 0:
            vip_discount = input_dict["iMemeberRebate"]
        else:
            vip_discount = input_dict["iCommonRebate"]

        output_dict = {}
        price_idx = {}
        item = input_dict["szItems"][0]

        # 准备工作：去除可能的逗号结尾
        if item.get("ItemNum") == "":
            item["ItemAvailPeriod"] = item["ItemAvailPeriod"][:-1]

        # 对每个项目数量或可用期限和价格执行逻辑
        item_array = item["ItemNum"].split(',') if item.get(
            "ItemNum") else item["ItemAvailPeriod"].split(',')

        # 构建 price_idx 词典信息
        for index, value in enumerate(item_array):
            if value:
                key = value if item.get(
                    "ItemNum") else "99999999" if value == "-1" else str(
                        int(value) / 24)
                item_price = input_dict["szPrices"][index]["SuperMoneyPrice"]
                price_idx[key] = {
                    "index": str(index),  # 价格索引
                    "price": str(int(item_price) * int(vip_discount) // 100)
                }

        # 构建最终结果对象，包括单位信息
        output_dict[input_dict["szName"]] = {
            "commodity_id": input_dict["iId"],
            "price_idx": sorted(price_idx.items(),
                           key=lambda x: int(x[0]) if item.get("ItemNum") else float(x[0]),
                           reverse=True),  # 道具可购买数量和价格由高到低排序
            "unit": "个" if item.get("ItemNum") else "天"  # 根据 ItemNum 存在与否确定单位
        }

        return output_dict

    def search_shop(self):
        """搜索商品信息"""
        url = f"https://bang.qq.com/app/speed/mall/search"
        params = {
            "uin": self.user.user_data.get('roleId'),
            "userId": self.user.user_data.get('userId'),
            "token": self.user.user_data.get('token'),
            "start": "0",
            "paytype": "1",  # 按点券筛选
            "order": "2",  # 按点券筛选
            "text": self.user.user_data.get('shopName')
        }
        headers = {"Referer": "https://bang.qq.com/app/speed/mall/main2"}

        response = requests.post(url, params=params, headers=headers)
        response.encoding = "utf-8"

        if len(response.json()['data']) == 1:
            return self.process_data(response.json()['data'][0])
        return None

    def get_shop_items(self, item_data, purse):
        """根据当前余额和道具价格生成购物列表"""
        # 判断是否是月末
        is_last_day = datetime.datetime.now().day == calendar.monthrange(
            datetime.datetime.now().year, datetime.datetime.now().month)[1]
        
        # 计算可用余额
        money = (int(purse['money']) + int(purse['coupons'])) if is_last_day else int(purse['coupons'])
        total = 0
        shop_array = []

        for item in item_data:
            i = 0
            while i < len(item_data[item]['price_idx']):
                # 商品数量索引
                shop_idx = item_data[item]['price_idx'][i][0]

                # 如果购买的商品可以购买永久且当前余额可以购买永久
                if (item_data[item]['price_idx'][i][0] == "99999999" and 
                    money > int(item_data[item]['price_idx'][i][1]['price'])):
                    shop_array.append({
                        "name": item,
                        "count": "99999999",
                        "commodity_id": item_data[item]['commodity_id'],
                        "price_idx": shop_idx
                    })
                    item_data[item]['unit'] = "永久"
                    break

                # 计算当前余额可以购买的最大道具数量
                max_counts = money // int(item_data[item]['price_idx'][i][1]['price'])
                if type(item_data[item]['price_idx'][i][0]) == str:
                    total += max_counts * int(float(item_data[item]['price_idx'][i][0]))
                else:
                    total += max_counts * int(item_data[item]['price_idx'][i][0])
                money -= max_counts * int(item_data[item]['price_idx'][i][1]['price'])

                if max_counts:
                    # 将可购买的道具添加到购物列表
                    for _ in range(max_counts):
                        shop_array.append({
                            "name": item,
                            "count": item_data[item]['price_idx'][i][0],
                            "commodity_id": item_data[item]['commodity_id'],
                            "price_idx": item_data[item]['price_idx'][i][1]['index']
                        })

                # 处理余额不足情况
                if (money < int(item_data[item]['price_idx'][-1][1]['price']) and 
                    not is_last_day and 
                    money / int(item_data[item]['price_idx'][-1][1]['price']) > 0.5):
                    price_diff = int(item_data[item]['price_idx'][-1][1]['price']) - money
                    if price_diff < int(purse['money']):
                        total += int(item_data[item]['price_idx'][-1][0])
                        money = 0
                        shop_array.append({
                            "name": item,
                            "count": item_data[item]['price_idx'][-1][0],
                            "commodity_id": item_data[item]['commodity_id'],
                            "price_idx": item_data[item]['price_idx'][-1][1]['index']
                        })

                i += 1

            return shop_array, total, item_data[item]['unit']

    def purchase(self, buy_info):
        """购买道具"""
        url = "https://bang.qq.com/app/speed/mall/getPurchase"
        headers = {"Referer": "https://bang.qq.com/app/speed/mall/detail2"}
        data = {
            "uin": self.user.user_data.get('roleId'),
            "userId": self.user.user_data.get('userId'),
            "areaId": self.user.user_data.get('areaId'),
            "token": self.user.user_data.get('token'),
            "pay_type": "1",
            "commodity_id": buy_info['commodity_id'],
            "price_idx": buy_info['price_idx']
        }
        # 延迟400毫秒执行，防止频繁
        time.sleep(0.4)
        response = requests.post(url, headers=headers, data=data)
        response.encoding = "utf-8"

        if "恭喜购买成功" in response.json()['msg']:
            return int(buy_info['count']) if buy_info['count'] != "99999999" else 99999999
        else:
            print(f"❌{response.json()['msg']}")
            return 0

    def execute(self):
        """执行购物任务"""
        msg = "购物\n"
        print(f"{self.user.get_account_info()} 开始执行购物任务...")
        
        # 检查是否设置了商品名称
        if not self.user.user_data.get('shopName'):
            return msg + "❌未设置shopName参数，请在cookie中添加shopName=商品名称\n"
            
        # 获取余额信息
        purse = self.get_pack_info()
        if not purse:
            return msg + "❌获取余额信息失败\n"
            
        log = f"💰当前余额: {purse['money']}点券 {purse['coupons']}消费券"
        msg += log + "\n"
        print(log)
        
        # 搜索商品信息
        item_data = self.search_shop()
        if not item_data:
            log = f"❌检测道具“{self.user.user_data.get('shopName')}”在商店中未售卖或不唯一"
            msg += log + "\n"
            print(log)
            return msg

        # 生成购物列表
        shop_array, total, unit = self.get_shop_items(item_data, purse)
        
        if shop_array:
            log = f"✅预计可购买 {'' if total == 0 else total} {unit} {self.user.user_data.get('shopName')}"
            msg += log + "\n"
            print(log)
            
            success_buy_counts = 0
            # 执行购买
            for buy_info in shop_array:
                success_buy_counts += self.purchase(buy_info)
                
            # 统计购买结果
            failed_buy_counts = total - (1 if success_buy_counts == 99999999 else success_buy_counts)
            
            if success_buy_counts > 0:
                success_buy_counts = "" if success_buy_counts == 99999999 else success_buy_counts
                log = f"✅成功购买 {success_buy_counts} {unit} {self.user.user_data.get('shopName')}"
                msg += log + "\n"
                print(log)
                if failed_buy_counts > 0:
                    log = f"❌未购买成功 {failed_buy_counts} {unit}"
                    msg += log + "\n"
                    print(log)
            else:
                log = f"❌全部购买失败，共计 {total} {unit}"
                msg += log + "\n"
                print(log)
        else:
            is_last_day = datetime.datetime.now().day == calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
            log = f"✅{'本月余额' if is_last_day else '今日消费券'}不足以购买 {self.user.user_data.get('shopName')}"
            msg += log + "\n"
            print(log)

        # 获取剩余余额
        purse = self.get_pack_info()
        log = f"💰剩余 {purse['money']}点券 {purse['coupons']}消费券"
        msg += log + "\n"
        print(log)
        
        return msg

class TreasureHunt:
    """寻宝功能类"""
    def __init__(self, user):
        self.user = user
        self.lock = threading.RLock()
        
    def get_treasure_info(self):
        """获取寻宝信息"""
        def extract(_html, _pattern):
            match = re.search(_pattern, _html)
            if match:
                return json.loads(re.sub(r'^\((.*)\)$', r'\1', match.group(1)))
            return None

        url = "https://bang.qq.com/app/speed/treasure/index"
        params = {
            "roleId": self.user.user_data.get('roleId'),
            "areaId": self.user.user_data.get('areaId'),
            "uin": self.user.user_data.get('roleId')
        }

        response = requests.get(url, params=params)
        response.encoding = 'utf-8'
        
        # 获取用户信息
        user_info = extract(response.text, r'window\.userInfo\s*=\s*eval\(\'([^\']+)\'\);')
        if not user_info:
            print("❌未找到用户信息")
            return None
            
        # 获取剩余寻宝次数
        left_times = re.search(r'id="leftTimes">(\d+)</i>', response.text)
        if not left_times:
            print("❌未找到剩余寻宝次数")
            return None
            
        # 获取地图信息
        map_info = extract(response.text, r'window\.mapInfo\s*=\s*eval\(\'([^\']+)\'\);')
        if not map_info:
            print("❌未找到地图信息")
            return None
            
        # 获取最高星级
        star_info = user_info.get('starInfo', {})
        star_keys = [key for key, value in star_info.items() if value == 1]
        if not star_keys:
            print("❌未找到已解锁的星级地图")
            return None
        star_id = max(star_keys)
            
        # 返回整理后的信息
        return {
            'vip_flag': bool(user_info.get('vip_flag')),
            'left_times': left_times.group(1),
            'star_id': star_id,
            'map_info': map_info
        }
        
    def get_treasure(self, iFlowId):
        """领取奖励"""
        url = "https://act.game.qq.com/ams/ame/amesvr?ameVersion=0.3&iActivityId=468228"
        headers = {
            "Cookie": f"access_token={self.user.user_data.get('accessToken')}; acctype=qc; appid={self.user.user_data.get('appid')}; openid={self.user.user_data.get('openid')}"
        }
        data = {
            'appid': self.user.user_data.get('appid'),
            'sArea': self.user.user_data.get('areaId'),
            'sRoleId': self.user.user_data.get('roleId'),
            'accessToken': self.user.user_data.get('accessToken'),
            'iActivityId': "468228",
            'iFlowId': iFlowId,
            'g_tk': '1842395457',
            'sServiceType': 'bb'
        }
        response = requests.post(url, headers=headers, data=data)
        response.encoding = "utf-8"
        
        if response.json()['ret'] == '0':
            return f"✅{response.json()['modRet']['sPackageName']}"
        return '❌非常抱歉，您还不满足参加该活动的条件！'

    def dig(self, status):
        """寻宝操作"""
        url = f"https://bang.qq.com/app/speed/treasure/ajax/{status}DigTreasure"
        headers = {
            "Referer": "https://bang.qq.com/app/speed/treasure/index",
            "Cookie": f"access_token={self.user.user_data.get('accessToken')}; acctype=qc; appid={self.user.user_data.get('appid')}; openid={self.user.user_data.get('openid')}"
        }
        data = {
            "mapId": self.user.user_data.get('mapId'),
            "starId": self.user.user_data.get('starId'),
            "areaId": self.user.user_data.get('areaId'),
            "type": self.user.user_data.get('type'),
            "roleId": self.user.user_data.get('roleId'),
            "userId": self.user.user_data.get('userId'),
            "uin": self.user.user_data.get('roleId'),
            "token": self.user.user_data.get('token')
        }
        response = requests.post(url, headers=headers, data=data)
        return False if response.json()['res'] == 0 else True

    def execute(self):
        """执行寻宝任务"""
        msg = "寻宝\n"
        print(f"{self.user.get_account_info()} 开始执行寻宝任务...")
        
        # 获取寻宝信息
        info = self.get_treasure_info()
        if not info:
            return msg + "❌获取寻宝信息失败\n"
            
        # 更新用户数据
        self.user.user_data.update({
            'type': 2 if info['vip_flag'] else 1,
            'starId': info['star_id']
        })
        
        # 获取今日大吉地图
        luck_maps = [item for item in info['map_info'][info['star_id']] if item.get('isdaji') == 1]
        if not luck_maps:
            return msg + "❌未找到今日大吉地图\n"
            
        self.user.user_data['mapId'] = luck_maps[0]['id']
        
        # 输出基本信息
        msg += f"💎紫钻用户：{'是' if info['vip_flag'] else '否'}\n"
        msg += f"⭐最高地图解锁星级：{info['star_id']}\n"
        msg += f"🌏今日大吉地图是[{luck_maps[0]['name']}]-地图ID是[{luck_maps[0]['id']}]\n"
        msg += f"⏰剩余寻宝次数：{info['left_times']}\n"
        
        print(f"💎紫钻用户：{'是' if info['vip_flag'] else '否'}")
        print(f"⭐最高地图解锁星级：{info['star_id']}")
        print(f"🌏今日大吉地图是[{luck_maps[0]['name']}]-地图ID是[{luck_maps[0]['id']}]")
        print(f"⏰剩余寻宝次数：{info['left_times']}")
        
        # 星级地图对应的iFlowId
        iFlowId_dict = {
            '1': ['856152', '856155'],
            '2': ['856156', '856157'],
            '3': ['856158', '856159'],
            '4': ['856160', '856161'],
            '5': ['856162', '856163'],
            '6': ['856164', '856165']
        }
        
        if info['left_times'] != "0":
            # 每日5次寻宝
            for n in range(5):
                with self.lock:
                    # 开始寻宝
                    if self.dig('start'):
                        msg += f"❌第{n+1}次寻宝...对不起，当天的寻宝次数已用完\n"
                        print(f"❌第{n+1}次寻宝...对不起，当天的寻宝次数已用完")
                        break
                        
                    print(f"✅第{n+1}次寻宝...")

                    # 寻宝倒计时
                    if self.user.user_data['type'] == 2:
                        print("🔎等待10秒寻宝时间...")
                        time.sleep(10)
                    else:
                        print("🔎等待十分钟寻宝时间...")
                        time.sleep(600)

                    # 结束寻宝
                    if not self.dig('end'):
                        print("✅结束寻宝...")

                    # 领取奖励
                    for iflowid in iFlowId_dict[info['star_id']]:
                        reward = self.get_treasure(iflowid)
                        msg += reward + "\n"
                        print(reward)
        else:
            msg += "❌对不起，当天的寻宝次数已用完\n"
            print("❌对不起，当天的寻宝次数已用完")
            
        return msg

def main():
    """主函数"""
    # 获取环境变量
    if "COOKIE_ZHANGFEI" not in os.environ:
        print('❌未添加COOKIE_ZHANGFEI变量')
        return
        
    cookie_list = re.split('\n|&&', os.environ.get('COOKIE_ZHANGFEI'))
    print(f"✅检测到共{len(cookie_list)}个飞车账号")
    
    all_msg = ""
    for i, cookie in enumerate(cookie_list, 1):
        print(f"\n开始处理第{i}个账号...")
        user = ZhangFeiUser(cookie)
        
        # 检查token
        if not user.check_token():
            continue
            
        account_msg = f"\n{user.get_account_info()}\n"
        all_msg += account_msg
        print(account_msg)
        
        # 检查功能启用状态
        enabled_features = []
        if user.is_feature_enabled('signin'):
            enabled_features.append('signin')
        if user.is_feature_enabled('shopping'):
            enabled_features.append('shopping')
        if user.is_feature_enabled('treasure'):
            enabled_features.append('treasure')
            
        if not enabled_features:
            msg = "❌未启用任何功能，请在cookie中添加以下参数之一：\n"
            msg += "enable_signin=true; - 签到功能\n"
            msg += "enable_shopping=true; - 购物功能\n"
            msg += "enable_treasure=true; - 寻宝功能\n"
            all_msg += msg
            print(msg)
            continue
        else:
            enabled_msg = "✅已启用功能："
            feature_names = {
                'signin': '签到',
                'shopping': '购物',
                'treasure': '寻宝'
            }
            enabled_msg += "、".join([feature_names[f] for f in enabled_features])
            print(enabled_msg)
        
        # 如果启用了购物功能，检查必需的参数
        if 'shopping' in enabled_features and not user.user_data.get('shopName'):
            msg = "❌已启用购物功能但未设置shopName参数\n"
            all_msg += msg
            print(msg)
            continue
        
        # 执行签到
        if 'signin' in enabled_features:
            sign_in = SignIn(user)
            sign_msg = sign_in.execute()
            all_msg += sign_msg
        
        # 执行购物
        if 'shopping' in enabled_features:
            shopping = Shopping(user)
            shop_msg = shopping.execute()
            all_msg += shop_msg
        
        # 执行寻宝
        if 'treasure' in enabled_features:
            treasure = TreasureHunt(user)
            treasure_msg = treasure.execute()
            all_msg += treasure_msg
        
        all_msg += "="*30 + "\n"
    
    # 发送通知
    try:
        send('掌上飞车全能版', all_msg)
    except Exception as err:
        print(f'❌发送通知失败: {err}')

if __name__ == "__main__":
    print("----------掌上飞车全能版开始运行----------")
    main()
    print("----------掌上飞车全能版运行完毕----------") 