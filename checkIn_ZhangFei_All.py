'''
new Env('掌上飞车全能版（多线程）')
cron: 10 0 * * *
Author       : BNDou
Date         : 2025-01-09 01:38:32
LastEditTime : 2025-03-22 21:46:19
FilePath     : /Auto_Check_In/checkIn_ZhangFei_All.py
Description  : 掌上飞车签到+购物+寻宝一体化脚本（多线程）

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
        self.progress = 0  # 添加进度属性
        self.status = ""   # 添加状态描述
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
        return log + "\n"

    def week_supplementary_signature(self):
        """补签"""
        msg = ""
        try:
            if self.user.user_data.get('weekSupplementarySignature') == "1":
                for index, value in enumerate(self.user.user_data.get('weekStatue')):
                    if value == "1":
                        if (datetime.datetime.now().weekday() + 1) > index + 1:
                            # 补签
                            ret = self.commit(['number', (index + 1)])
                            log = str(ret['modRet']['sMsg']) if ret['ret'] == '0' else str(ret['flowRet']['sMsg'])
                            msg += f"✅补签：{log}\n"
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
        return msg

    def execute(self):
        """执行签到任务"""
        msg = "签到\n"
        
        # 获取签到信息
        if not self.get_sign_info():
            return msg + "❌获取签到信息失败\n"
            
        # 获取累计信息
        if not self.get_out_value():
            return msg + "❌获取累计信息失败\n"
            
        # 执行签到
        msg += self.sign_in()
        
        # 输出签到统计
        msg += (f"本周签到{self.user.user_data.get('weekSignIn')}/7天，"
               f"本月签到{self.user.user_data.get('monthSignIn')}/25天，"
               f"有{self.user.user_data.get('weekSupplementarySignature')}天可补签\n")
        
        # 补签
        week_msg = self.week_supplementary_signature()
        if week_msg:
            msg += week_msg
            
        # 领取月签奖励
        month_msg = self.month_sign_in()
        if month_msg:
            msg += month_msg
            
        # 日常任务：浏览背包
        # if self.browse_backpack():
        #     msg += "✅日常任务：浏览背包成功\n"
            
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
        
        # 检查是否设置了商品名称
        if not self.user.user_data.get('shopName'):
            return msg + "❌未设置shopName参数，请在cookie中添加shopName=商品名称\n"
            
        # 获取余额信息
        purse = self.get_pack_info()
        if not purse:
            return msg + "❌获取余额信息失败\n"
            
        msg += f"💰当前余额: {purse['money']}点券 {purse['coupons']}消费券\n"
        
        # 搜索商品信息
        item_data = self.search_shop()
        if not item_data:
            msg += f"❌检测道具“{self.user.user_data.get('shopName')}”在商店中未售卖或不唯一\n"
            return msg

        # 生成购物列表
        shop_array, total, unit = self.get_shop_items(item_data, purse)
        
        if shop_array:
            msg += f"✅预计可购买 {'' if total == 0 else total} {unit} {self.user.user_data.get('shopName')}\n"
            
            success_buy_counts = 0
            # 执行购买
            for buy_info in shop_array:
                success_buy_counts += self.purchase(buy_info)
                
            # 统计购买结果
            failed_buy_counts = total - (1 if success_buy_counts == 99999999 else success_buy_counts)
            
            if success_buy_counts > 0:
                success_buy_counts = "" if success_buy_counts == 99999999 else success_buy_counts
                msg += f"✅成功购买 {success_buy_counts} {unit} {self.user.user_data.get('shopName')}\n"
                if failed_buy_counts > 0:
                    msg += f"❌未购买成功 {failed_buy_counts} {unit}\n"
            else:
                msg += f"❌全部购买失败，共计 {total} {unit}\n"
        else:
            is_last_day = datetime.datetime.now().day == calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]
            msg += f"✅{'本月余额' if is_last_day else '今日消费券'}不足以购买 {self.user.user_data.get('shopName')}\n"

        # 获取剩余余额
        purse = self.get_pack_info()
        msg += f"💰剩余 {purse['money']}点券 {purse['coupons']}消费券\n"
        
        return msg

class TreasureHunt:
    """寻宝功能类（重构版）"""
    def __init__(self, user):
        self.user = user
        self.lock = threading.RLock()
        # 从用户数据中提取核心参数
        self.access_token = self.user.user_data.get('accessToken')
        self.appid = self.user.user_data.get('appid')
        self.openid = self.user.user_data.get('openid')
        self.game_open_id = self.user.user_data.get('roleId')
        self.area_id = self.user.user_data.get('areaId')

    def get_treasure_info(self):
        """获取寻宝信息（新版接口）"""
        try:
            # 第一步：获取用户信息(nickName和face)
            url = f"https://ams.game.qq.com/ams/userLoginSvr?callback=jsonp86&acctype=qc&openid={self.openid}&access_token={self.access_token}&appid={self.appid}&game=act.xinyue"
            headers = {
                'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1003/3.16.0.2.2103160002",
                'sec-fetch-site': "same-site",
                'sec-fetch-dest': "script",
                'accept-language': "zh-CN,zh-Hans;q=0.9",
                'sec-fetch-mode': "no-cors",
                'referer': "https://act.xinyue.qq.com/",
                'Cookie': f"accessToken={self.access_token}; access_token={self.access_token}; acctype=qc; appId={self.appid}; appOpenid={self.openid}; appid={self.appid}; openid={self.openid}; uin=o0{self.game_open_id}; actxinyueqqcomrouteLine=a20250417speed"
            }
            response = requests.get(url, headers=headers)
            json_str = re.search(r'jsonp86\((\{.*?\})\)', response.text).group(1)
            user_info = json.loads(json_str)
            
            # 第二步：获取角色信息确认
            url = "https://agw.xinyue.qq.com/amp2.RoleSrv/GetBindRole"
            payload = {
                "game_code": "speed",
                "device": "ios",
                "scene": "ceiba"
            }
            headers = {
                'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1003/3.16.0.2.2103160002",
                'Accept': "application/json, text/plain, */*",
                'Content-Type': "application/json",
                'T-APPID': self.appid,
                'T-ACCOUNT-TYPE': "qc",
                'Sec-Fetch-Site': "same-site",
                'T-ACCESS-TOKEN': self.access_token,
                'T-MODE': "true",
                'T-OPENID': self.openid,
                'Sec-Fetch-Mode': "cors",
                'Accept-Language': "zh-CN,zh-Hans;q=0.9",
                'Origin': "https://act.xinyue.qq.com",
                'Referer': "https://act.xinyue.qq.com/"
            }
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            role_data = response.json()
            if not role_data.get('roles'):
                return None
            role_info = role_data['roles'][0]
            
            # 第三步：获取循环次数和相关ID
            url = "https://agw.xinyue.qq.com/amp2.WPESrv/WPEIndex?flowId=307069&actId=22799"
            payload = {
                "biz_id": "bb",
                "act_id": "22799",
                "flow_id": 307069,
                "role": {
                    "game_open_id": self.game_open_id,
                    "game_app_id": "",
                    "area_id": int(self.area_id),
                    "plat_id": 2,
                    "partition_id": 1,
                    "partition_name": role_info.get('partition_name', ""),
                    "role_id": self.game_open_id,
                    "role_name": role_info.get('role_name', ""),
                    "device": "pc",
                    "flag": 0
                },
                "data": f"{{\"user_attach\":\"{{\\\"nickName\\\":\\\"{user_info.get('nickName')}\\\",\\\"avatar\\\":\\\"{user_info.get('face')}\\\"}}\",\"ceiba_plat_id\":\"ios\",\"cExtData\":{{}}}}"
            }
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            loop_data = response.json()
            inner_data = json.loads(loop_data['data'])
            hold_list_key = next(iter(inner_data['holdList'].keys()))
            left_times = inner_data['holdList'][hold_list_key]['remain']
            
            # 第四步：获取地图信息
            url = "https://agw.xinyue.qq.com/amp2.WPESrv/WPEIndex?flowId=307086&actId=22799"
            payload = {
                "biz_id": "bb",
                "act_id": "22799",
                "flow_id": 307086,
                "role": {
                    "game_open_id": self.game_open_id,
                    "game_app_id": "",
                    "area_id": int(self.area_id),
                    "plat_id": 2,
                    "partition_id": 1,
                    "partition_name": role_info.get('partition_name', ""),
                    "role_id": self.game_open_id,
                    "role_name": role_info.get('role_name', ""),
                    "device": "pc",
                    "flag": 0
                },
                "data": f"{{\"user_attach\":\"{{\\\"nickName\\\":\\\"{user_info.get('nickName')}\\\",\\\"avatar\\\":\\\"{user_info.get('face')}\\\"}}\",\"ceiba_plat_id\":\"ios\",\"cExtData\":{{}}}}"
            }
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            map_data = response.json()
            inner_map_data = json.loads(map_data['data'])
            max_star_level = max(item['star_level'] for item in inner_map_data['mapList'])
            target_map_id = None
            max_star_maps = [item for item in inner_map_data['mapList'] if item['star_level'] == max_star_level]
            if max_star_maps:
                for map_info in max_star_maps[0]['map_info']:
                    if map_info['daji'] == 1:
                        target_map_id = map_info['map_id']
                        break

            if not target_map_id:
                print(f"❌最高星级{max_star_level}下未找到daji=1的地图")
            
            
            return {
                'left_times': left_times,
                'star_id': str(max_star_level),
                'map_info': inner_map_data['mapList'],
                'target_map_id': target_map_id,
                'flow_id': hold_list_key,
                'user_info': user_info,
                'role_info': role_info
            }
        except Exception as e:
            print(f"❌获取寻宝信息失败: {str(e)}")
            return None

    def start_game(self, star_level, map_id, role_info, user_info):
        """开始游戏"""
        url = "https://agw.xinyue.qq.com/amp2.WPESrv/WPEIndex?flowId=307070&actId=22799"
        game_open_id = self.game_open_id
        role_name = role_info.get('role_name', "")
        partition_name = role_info.get('partition_name', "")
        nick_name = user_info.get('nickName', "")
        face = user_info.get('face', "")
        
        payload = {
            "biz_id": "bb",
            "act_id": "22799",
            "flow_id": "307070",
            "role": {
                "game_open_id": game_open_id,
                "game_app_id": "",
                "area_id": int(self.area_id),
                "plat_id": 2,
                "partition_id": 1,
                "partition_name": partition_name,
                "role_id": game_open_id,
                "role_name": role_name,
                "device": "pc",
                "flag": 0
            },
            "data": f"{{\"user_attach\":\"{{\\\"nickName\\\":\\\"{nick_name}\\\",\\\"avatar\\\":\\\"{face}\\\"}}\",\"starLevel\":{star_level},\"mapId\":\"{map_id}\",\"StarLevel\":{star_level},\"MapID\":\"{map_id}\",\"ceiba_plat_id\":\"ios\",\"cExtData\":{{}}}}",
            "starLevel": star_level,
            "mapId": map_id,
            "StarLevel": star_level,
            "MapID": map_id
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1003/3.16.0.2.2103160002",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json",
            'T-APPID': self.appid,
            'T-ACCOUNT-TYPE': "qc",
            'Sec-Fetch-Site': "same-site",
            'T-ACCESS-TOKEN': self.access_token,
            'T-MODE': "true",
            'T-OPENID': self.openid,
            'Sec-Fetch-Mode': "cors",
            'Accept-Language': "zh-CN,zh-Hans;q=0.9",
            'Origin': "https://act.xinyue.qq.com",
            'Referer': "https://act.xinyue.qq.com/"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response.json()

    def claim_reward(self, flow_id, role_info, user_info):
        """领取奖励"""
        url = f"https://agw.xinyue.qq.com/amp2.WPESrv/WPEIndex?flowId={flow_id}&actId=22799"
        game_open_id = self.game_open_id
        role_name = role_info.get('role_name', "")
        partition_name = role_info.get('partition_name', "")
        nick_name = user_info.get('nickName', "")
        face = user_info.get('face', "")
        
        payload = {
            "biz_id": "bb",
            "act_id": "22799",
            "flow_id": flow_id,
            "role": {
                "game_open_id": game_open_id,
                "game_app_id": "",
                "area_id": int(self.area_id),
                "plat_id": 2,
                "partition_id": 1,
                "partition_name": partition_name,
                "role_id": game_open_id,
                "role_name": role_name,
                "device": "pc",
                "flag": 0
            },
            "data": f"{{\"user_attach\":\"{{\\\"nickName\\\":\\\"{nick_name}\\\",\\\"avatar\\\":\\\"{face}\\\"}}\",\"ceiba_plat_id\":\"ios\",\"cExtData\":{{}}}}"
        }
        headers = {
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 GH_QQConnect GameHelper_1003/3.16.0.2.2103160002",
            'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json",
            'T-APPID': self.appid,
            'T-ACCOUNT-TYPE': "qc",
            'Sec-Fetch-Site': "same-site",
            'T-ACCESS-TOKEN': self.access_token,
            'T-MODE': "true",
            'T-OPENID': self.openid,
            'Sec-Fetch-Mode': "cors",
            'Accept-Language': "zh-CN,zh-Hans;q=0.9",
            'Origin': "https://act.xinyue.qq.com",
            'Referer': "https://act.xinyue.qq.com/"
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        result = response.json()
        
        # 整理奖励信息
        reward_msg = []
        if result.get('ret') == 0:
            reward_msg.append(f"✅{result.get('msg', '领取奖励成功')}")
            if 'data' in result:
                data_json = json.loads(result['data'])
                reward_msg.append(f"   {data_json.get('msg', '')}")
        else:
            reward_msg.append(f"❌领取奖励失败: {result.get('msg', '未知错误')}")
            
        return "\n".join(reward_msg)

    def execute(self):
        """执行寻宝任务"""
        msg = "寻宝\n"
        
        # 获取寻宝信息
        info = self.get_treasure_info()
        if not info:
            return msg + "❌获取寻宝信息失败\n"
        
        msg += f"⭐最高地图解锁星级：{info['star_id']}\n"
        msg += f"🌏今日大吉地图ID：{info['target_map_id']}\n"
        msg += f"⏰剩余寻宝次数：{info['left_times']}\n"
        
        # 执行寻宝循环
        if int(info['left_times']) > 0:
            for n in range(int(info['left_times'])):
                with self.lock:
                    msg += f"\n第{n+1}次寻宝：\n"
                    
                    # 开始游戏
                    start_result = self.start_game(
                        info['star_id'], 
                        info['target_map_id'],
                        info['role_info'],
                        info['user_info']
                    )
                    
                    if start_result.get('ret') != 0:
                        msg += f"❌开始游戏失败：{start_result.get('msg', '未知错误')}\n"
                        break
                    
                    msg += "✅开始游戏成功，等待完成...\n"
                    time.sleep(10)
                    
                    # 领取奖励
                    reward_msg = self.claim_reward(
                        info['flow_id'],
                        info['role_info'],
                        info['user_info']
                    )
                    msg += reward_msg + "\n"
        else:
            msg += "❌今日寻宝次数已用完\n"
            
        return msg

def update_progress(users):
    """更新并显示所有账号的进度"""
    # 用于跟踪哪些账号已经显示过完成状态
    shown_completed = set()
    
    while True:
        # 清除控制台
        os.system('cls' if os.name == 'nt' else 'clear')
        
        all_completed = True
        any_output = False
        
        for user in users:
            if user.progress < 100:
                # 显示未完成的账号
                account_info = user.get_account_info()
                progress_bar = '=' * int(user.progress / 2) + '>' + ' ' * (50 - int(user.progress / 2))
                print(f"{account_info}")
                print(f"[{progress_bar}] {user.progress}% {user.status}")
                # print()
                all_completed = False
                any_output = True
            elif user.progress == 100 and user not in shown_completed:
                # 显示刚完成的账号（仅一次）
                account_info = user.get_account_info()
                progress_bar = '=' * 50
                print(f"{account_info}")
                print(f"[{progress_bar}] 100% {user.status}")
                # print()
                shown_completed.add(user)
                any_output = True
        
        # 如果没有任何输出，显示完成信息
        if not any_output:
            print("所有账号任务已完成！")
            
        if all_completed:
            break
            
        time.sleep(1)

def process_account(user, msg_dict, user_index):
    """处理单个账号的任务"""
    try:
        # 初始化账号消息
        account_msg = f"\n{user.get_account_info()}\n"
        msg_dict[user_index] = [account_msg]  # 使用列表存储当前账号的所有消息
        
        # 检查token
        if not user.check_token():
            user.progress = 100
            user.status = "登录失效"
            msg_dict[user_index].append("❌登录失效，请重新获取token\n")
            return
            
        # 检查功能启用状态
        enabled_features = []
        
        # 检查签到功能
        if user.is_feature_enabled('signin'):
            enabled_features.append('signin')
        else:
            msg_dict[user_index].append("❌未启用签到功能，请在cookie中添加enable_signin=true;\n")
            
        # 检查购物功能
        if user.is_feature_enabled('shopping'):
            enabled_features.append('shopping')
        else:
            msg_dict[user_index].append("❌未启用购物功能，请在cookie中添加enable_shopping=true;\n")
            
        # 检查寻宝功能
        if user.is_feature_enabled('treasure'):
            enabled_features.append('treasure')
        else:
            msg_dict[user_index].append("❌未启用寻宝功能，请在cookie中添加enable_treasure=true;\n")
            
        if not enabled_features:
            user.progress = 100
            user.status = "未启用功能"
            return
            
        # 显示已启用的功能
        feature_names = {
            'signin': '签到',
            'shopping': '购物',
            'treasure': '寻宝'
        }
        enabled_msg = "✅已启用功能：" + "、".join([feature_names[f] for f in enabled_features])
        print(f"{user.get_account_info()}\n{enabled_msg}\n")
            
        # 如果启用了购物功能，检查必需的参数
        if 'shopping' in enabled_features and not user.user_data.get('shopName'):
            msg = "❌已启用购物功能但未设置shopName参数\n"
            msg_dict[user_index].append(msg)
            user.progress = 100
            user.status = "购物参数缺失"
            return
        
        total_features = len(enabled_features)
        progress_per_feature = 100 / total_features
        
        # 执行签到
        if 'signin' in enabled_features:
            user.status = "正在签到..."
            sign_in = SignIn(user)
            sign_msg = sign_in.execute()
            msg_dict[user_index].append(sign_msg)
            user.progress += progress_per_feature
        
        # 执行购物
        if 'shopping' in enabled_features:
            user.status = "正在购物..."
            shopping = Shopping(user)
            shop_msg = shopping.execute()
            msg_dict[user_index].append(shop_msg)
            user.progress += progress_per_feature
        
        # 执行寻宝
        if 'treasure' in enabled_features:
            user.status = "正在寻宝..."
            treasure = TreasureHunt(user)
            treasure_msg = treasure.execute()
            msg_dict[user_index].append(treasure_msg)
            user.progress = 100
            
        user.status = "任务完成"
        msg_dict[user_index].append("="*30 + "\n")
        
    except Exception as e:
        if user_index not in msg_dict:
            msg_dict[user_index] = [account_msg]
        msg_dict[user_index].append(f"❌执行出错: {str(e)}\n")
        user.status = f"执行出错: {str(e)}"
        user.progress = 100

def main():
    """主函数"""
    # 获取环境变量
    if "COOKIE_ZHANGFEI" not in os.environ:
        print('❌未添加COOKIE_ZHANGFEI变量')
        return
        
    cookie_list = re.split('\n|&&', os.environ.get('COOKIE_ZHANGFEI'))
    print(f"✅检测到共{len(cookie_list)}个飞车账号")
    
    # 创建用户对象列表
    users = [ZhangFeiUser(cookie) for cookie in cookie_list]
    
    # 创建线程安全的消息字典
    msg_dict = {}
    
    # 创建并启动进度显示线程
    progress_thread = threading.Thread(target=update_progress, args=(users,))
    progress_thread.daemon = True
    progress_thread.start()
    
    # 创建并启动账号处理线程
    threads = []
    for i, user in enumerate(users):
        t = threading.Thread(target=process_account, args=(user, msg_dict, i))
        threads.append(t)
        t.start()
    
    # 等待所有线程完成
    for t in threads:
        t.join()
    
    # 等待进度显示线程完成最后一次更新
    time.sleep(1)
    
    # 按账号顺序合并消息
    all_msg = ""
    for i in range(len(users)):
        if i in msg_dict:
            all_msg += "".join(msg_dict[i])
    
    # 发送通知
    try:
        send('掌上飞车全能版', all_msg)
    except Exception as err:
        print(f'❌发送通知失败: {err}')

if __name__ == "__main__":
    print("----------掌上飞车全能版开始运行----------")
    main()
    print("----------掌上飞车全能版运行完毕----------") 
