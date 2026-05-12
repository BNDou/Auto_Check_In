'''
Author: BNDou
Date: 2023-10-18 20:55:31
LastEditTime: 2024-06-05 05:21:57
FilePath: /Auto_Check_In/utils/sendNotify.py
Description: 
'''

import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.parse

import requests

cur_path = os.path.abspath(os.path.dirname(__file__))
root_path = os.path.split(cur_path)[0]
sys.path.append(root_path)

# 通知服务
HITOKOTO = 'true'  # 启用一言（随机句子）; 为空即关闭
BARK = ''  # bark服务,自行搜索; secrets可填;
BARK_PUSH = ''  # bark自建服务器，要填完整链接，结尾的/不要
PUSH_KEY = ''  # Server酱的PUSH_KEY; secrets可填
TG_BOT_TOKEN = ''  # tg机器人的TG_BOT_TOKEN; secrets可填1407203283:AAG9rt-6RDaaX0HBLZQq0laNOh898iFYaRQ
TG_USER_ID = ''  # tg机器人的TG_USER_ID; secrets可填 1434078534
TG_API_HOST = ''  # tg 代理api
TG_PROXY_IP = ''  # tg机器人的TG_PROXY_IP; secrets可填
TG_PROXY_PORT = ''  # tg机器人的TG_PROXY_PORT; secrets可填
DD_BOT_TOKEN = ''  # 钉钉机器人的DD_BOT_TOKEN; secrets可填
DD_BOT_SECRET = ''  # 钉钉机器人的DD_BOT_SECRET; secrets可填
QQ_SKEY = ''  # qq机器人的QQ_SKEY; secrets可填
QQ_MODE = ''  # qq机器人的QQ_MODE; secrets可填
QYWX_AM = ''  # 企业微信
QYWX_KEY = ''  # 企业微信BOT
PUSH_PLUS_TOKEN = ''  # 微信推送Plus+
FS_KEY = ''  # 飞书群BOT

message_info = ''''''

# GitHub action运行需要填写对应的secrets
if "HITOKOTO" in os.environ:
    HITOKOTO = os.environ["HITOKOTO"]
if "BARK" in os.environ and os.environ["BARK"]:
    BARK = os.environ["BARK"]
if "BARK_PUSH" in os.environ and os.environ["BARK_PUSH"]:
    BARK_PUSH = os.environ["BARK_PUSH"]
if "PUSH_KEY" in os.environ and os.environ["PUSH_KEY"]:
    PUSH_KEY = os.environ["PUSH_KEY"]
if "TG_BOT_TOKEN" in os.environ and os.environ[
        "TG_BOT_TOKEN"] and "TG_USER_ID" in os.environ and os.environ[
            "TG_USER_ID"]:
    TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
    TG_USER_ID = os.environ["TG_USER_ID"]
if "TG_API_HOST" in os.environ and os.environ["TG_API_HOST"]:
    TG_API_HOST = os.environ["TG_API_HOST"]
if "DD_BOT_TOKEN" in os.environ and os.environ[
        "DD_BOT_TOKEN"] and "DD_BOT_SECRET" in os.environ and os.environ[
            "DD_BOT_SECRET"]:
    DD_BOT_TOKEN = os.environ["DD_BOT_TOKEN"]
    DD_BOT_SECRET = os.environ["DD_BOT_SECRET"]
if "QQ_SKEY" in os.environ and os.environ[
        "QQ_SKEY"] and "QQ_MODE" in os.environ and os.environ["QQ_MODE"]:
    QQ_SKEY = os.environ["QQ_SKEY"]
    QQ_MODE = os.environ["QQ_MODE"]
# 获取pushplus+ PUSH_PLUS_TOKEN
if "PUSH_PLUS_TOKEN" in os.environ:
    if len(os.environ["PUSH_PLUS_TOKEN"]) > 1:
        PUSH_PLUS_TOKEN = os.environ["PUSH_PLUS_TOKEN"]
        # print("已获取并使用Env环境 PUSH_PLUS_TOKEN")
# 获取企业微信应用推送 QYWX_AM
if "QYWX_AM" in os.environ:
    if len(os.environ["QYWX_AM"]) > 1:
        QYWX_AM = os.environ["QYWX_AM"]

if "QYWX_KEY" in os.environ:
    if len(os.environ["QYWX_KEY"]) > 1:
        QYWX_KEY = os.environ["QYWX_KEY"]
        # print("已获取并使用Env环境 QYWX_AM")

# 接入飞书webhook推送
if "FS_KEY" in os.environ:
    if len(os.environ["FS_KEY"]) > 1:
        FS_KEY = os.environ["FS_KEY"]


def message(str_msg):
    global message_info
    print(str_msg)
    message_info = "{}\n{}".format(message_info, str_msg)
    sys.stdout.flush()


def bark(title, content):
    print("bark服务启动")
    try:
        response = requests.get(
            f"""https://api.day.app/{BARK}/{title}/{urllib.parse.quote_plus(content)}"""
        ).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


def bark_push(title, content):
    print("bark自建服务启动")
    try:
        response = requests.get(
            f"""{BARK_PUSH}/{title}/{urllib.parse.quote_plus(content)}"""
        ).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


def serverJ(title, content):
    print("serverJ服务启动")
    try:
        data = {"text": title, "desp": content.replace("\n", "\n\n")}
        response = requests.post(f"https://sc.ftqq.com/{PUSH_KEY}.send",
                                 data=data).json()
        if response['errno'] == 0:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


# tg通知
def telegram_bot(title, content):
    print("tg服务启动")
    # bot_token = TG_BOT_TOKEN
    # user_id = TG_USER_ID
    try:
        if TG_API_HOST:
            if 'http' in TG_API_HOST:
                url = f"{TG_API_HOST}/bot{TG_BOT_TOKEN}/sendMessage"
            else:
                url = f"https://{TG_API_HOST}/bot{TG_BOT_TOKEN}/sendMessage"
        else:
            url = f"https://api.telegram.org/bot{TG_BOT_TOKEN}/sendMessage"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {
            'chat_id': str(TG_USER_ID),
            'text': f'{title}\n\n{content}',
            'disable_web_page_preview': 'true'
        }
        proxies = None
        if TG_PROXY_IP and TG_PROXY_PORT:
            proxyStr = "http://{}:{}".format(TG_PROXY_IP, TG_PROXY_PORT)
            proxies = {"http": proxyStr, "https": proxyStr}
            response = requests.post(url=url,
                                     headers=headers,
                                     params=payload,
                                     proxies=proxies).json()
            if response['ok']:
                print('推送成功！')
            else:
                print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


def dingding_bot(title, content):
    print("钉钉机器人服务启动")
    try:
        timestamp = str(round(time.time() * 1000))  # 时间戳
        secret_enc = DD_BOT_SECRET.encode('utf-8')
        string_to_sign = '{}\n{}'.format(timestamp, DD_BOT_SECRET)
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc,
                             string_to_sign_enc,
                             digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
        url = f'https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_TOKEN}&timestamp={timestamp}&sign={sign}'
        headers = {'Content-Type': 'application/json;charset=utf-8'}
        data = {
            'msgtype': 'text',
            'text': {
                'content': f'{title}\n\n{content}'
            }
        }
        response = requests.post(url=url,
                                 data=json.dumps(data),
                                 headers=headers,
                                 timeout=15).json()
        if not response['errcode']:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


def coolpush_bot(title, content):
    print("qq服务启动")
    try:
        url = f"https://qmsg.zendee.cn/{QQ_MODE}/{QQ_SKEY}"
        payload = {'msg': f"{title}\n\n{content}".encode('utf-8')}
        response = requests.post(url=url, params=payload).json()
        if response['code'] == 0:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


# push推送
def pushplus_bot(title, content):
    print("PUSHPLUS服务启动")
    try:
        url = 'http://www.pushplus.plus/send'
        data = {"token": PUSH_PLUS_TOKEN, "title": title, "content": content}
        body = json.dumps(data).encode(encoding='utf-8')
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, data=body, headers=headers).json()
        if response['code'] == 200:
            print('推送成功！')
        else:
            print('推送失败！')
    except Exception as e:
        print(f"报错信息:{e}")
        print('推送失败！')


def wecom_key(title, content):
    print("QYWX_KEY服务启动")
    try:
        # print("content" + content)
        headers = {'Content-Type': 'application/json'}
        data = {
            "msgtype": "text",
            "text": {
                "content": title + "\n" + content.replace("\n", "\n\n")
            }
        }
        # print(f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}")
        response = requests.post(
            f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={QYWX_KEY}",
            json=data,
            headers=headers).json()
        print(response)
        # todo 不知道怎么判断是否成功
    except Exception as e:
        print(f"报错信息:{e}")
        print("推送失败")


# 飞书机器人推送
def fs_key(title, content):
    print("FS_KEY服务启动")
    try:
        # print("content" + content)
        headers = {'Content-Type': 'application/json'}
        data = {
            "msg_type": "text",
            "content": {
                "text": title + "\n" + content.replace("\n", "\n\n")
            }
        }
        # print(f"https://open.feishu.cn/open-apis/bot/v2/hook/{FS_KEY}")
        response = requests.post(
            f"https://open.feishu.cn/open-apis/bot/v2/hook/{FS_KEY}",
            json=data,
            headers=headers).json()
        print(response)
        # todo 不知道怎么判断是否成功
    except Exception as e:
        print(f"报错信息:{e}")
        print("推送失败")


# 企业微信 APP 推送
def wecom_app(title, content):
    QYWX_AM_AY = re.split(',', QYWX_AM)
    if 4 < len(QYWX_AM_AY) > 5:
        print("QYWX_AM 设置错误！！\n取消推送")
        return
    print("QYWX_APP服务启动")
    try:

        corpid = QYWX_AM_AY[0]
        corpsecret = QYWX_AM_AY[1]
        touser = QYWX_AM_AY[2]
        agentid = QYWX_AM_AY[3]
        try:
            media_id = QYWX_AM_AY[4]
        except:
            media_id = ''
        wx = WeCom(corpid, corpsecret, agentid)
        # 如果没有配置 media_id 默认就以 text 方式发送
        if not media_id:
            message = title + '\n\n' + content
            response = wx.send_text(message, touser)
        else:
            response = wx.send_mpnews(title, content, media_id, touser)
        if response == 'ok':
            print('推送成功！')
        else:
            print('推送失败！错误信息如下：\n', response)
    except Exception as e:
        print(f"报错信息:{e}")
        print("推送失败")


class WeCom:
    def __init__(self, corpid, corpsecret, agentid):
        self.CORPID = corpid
        self.CORPSECRET = corpsecret
        self.AGENTID = agentid

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {
            'corpid': self.CORPID,
            'corpsecret': self.CORPSECRET,
        }
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def send_text(self, message, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token(
        )
        send_values = {
            "touser": touser,
            "msgtype": "text",
            "agentid": self.AGENTID,
            "text": {
                "content": message
            },
            "safe": "0"
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]

    def send_mpnews(self, title, message, media_id, touser="@all"):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token(
        )
        send_values = {
            "touser": touser,
            "msgtype": "mpnews",
            "agentid": self.AGENTID,
            "mpnews": {
                "articles": [{
                    "title": title,
                    "thumb_media_id": media_id,
                    "author": "Author",
                    "content_source_url": "",
                    "content": message.replace('\n', '<br/>'),
                    "digest": message
                }]
            }
        }
        send_msges = (bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()
        return respone["errmsg"]


def one() -> str:
    """
    获取一条一言。
    :return:
    """
    url = "https://v1.hitokoto.cn/"
    res = requests.get(url).json()
    return res["hitokoto"] + "\n————" + res["from"]


def send(title, content):
    """
    使用 bark, telegram bot, dingding bot, server, feishuJ 发送手机推送
    :param title:
    :param content:
    :return:
    """
    # 获取一条一言
    content += f"\n\n{one()}" if HITOKOTO else ""
    if BARK:
        bark(title=title, content=content)
    if BARK_PUSH:
        bark_push(title=title, content=content)
    if PUSH_KEY:
        serverJ(title=title, content=content)
    if DD_BOT_TOKEN and DD_BOT_TOKEN:
        dingding_bot(title=title, content=content)
    if TG_BOT_TOKEN and TG_USER_ID:
        telegram_bot(title=title, content=content)
    if QQ_SKEY and QQ_MODE:
        coolpush_bot(title=title, content=content)
    if PUSH_PLUS_TOKEN:
        pushplus_bot(title=title, content=content)
    if QYWX_AM:
        wecom_app(title=title, content=content)
    if QYWX_KEY:
        for i in range(int(len(content) / 2000) + 1):
            wecom_key(title=title, content=content[i * 2000:(i + 1) * 2000])
    if FS_KEY:
        fs_key(title=title, content=content)


def main():
    send('title', 'content')


if __name__ == '__main__':
    main()
