'''
new Env('周末大乐透扫码登陆')
cron: 1 1 1 1 1
                       _oo0oo_
                      o8888888o
                      88" . "88
                      (| -_- |)
                      0\  =  /0
                    ___/`---'\___
                  .' \\|     |// '.
                 / \\|||  :  |||// \
                / _||||| -:- |||||- \
               |   | \\\  - /// |   |
               | \_|  ''\---/''  |_/ |
               \  .-\__  '-'  ___/-. /
             ___'. .'  /--.--\  `. .'___
          ."" '<  `.___\_<|>_/___.' >' "".
         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
         \  \ `_.   \_ __\ /__ _/   .-` /  /
     =====`-.____`.___ \_____/___.-`___.-'=====
                       `=---='


     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

           佛祖保佑     永不宕机     永无BUG

Author: BNDou
Date: 2024-08-04 22:33:43
LastEditTime: 2024-08-11 00:45:53
FilePath: \Auto_Check_In\checkIn_SpeedWeekendLottery_getCK.py
Description: 
'''

import sys
import io
import re
import time
from urllib.parse import unquote

import qrcode
import requests
try:
    from PIL import Image
    from pyzbar.pyzbar import decode
    from utils.notify import send  # 导入消息通知模块
except ModuleNotFoundError as e:
    if "PIL" in str(e):
        print(f"❌ {e}\n请到依赖管理中安装python环境的“pillow”")
    elif "pyzbar" in str(e):
        print(f"❌ {e}\n请到依赖管理中安装python环境的“pyzbar”")
    sys.exit()
except ImportError as e:
    print(f"❌ {e}\n请安装 zbar 库，安装指令：apk add zbar-dev")
    sys.exit()
except Exception as e:  # 异常捕捉
    print('%s\n加载通知服务失败~' % e)

# def get_auth_token(t):
#     """官方算法：根据supertoken计算auth_token"""
#     e, r = 0, len(t)
#     for n in range(r):
#         e = 33 * e + ord(t[n])
#     return e % 4294967296


def get_ptqrtoken(t):
    """官方算法：根据qrsig计算ptqrtoken"""
    e, r = 0, len(t)
    for n in range(r):
        e += (e << 5) + ord(t[n])
    return 2147483647 & e


def getG_tk(skey):
    """官方算法：根据skey计算g_tk"""
    hash = 5381
    for i in range(len(skey)):
        hash += (hash << 5) + ord(skey[i])
    return hash & 2147483647


def getUserData(p_uin, skey):
    """获取用户数据"""
    msg, area = "", 1
    while area <= 3:
        url = f"https://comm.aci.game.qq.com/main?game=speed&area={area}&sCloudApiName=ams.gameattr.role"
        headers = {
            "Referer": "https://speed.qq.com/",
            "Cookie": f"ptui_loginuin={p_uin}; uin={p_uin}; skey={skey};"
        }
        response = requests.get(url, headers=headers)
        userData = unquote(response.text)
        # 获取用户数据
        if re.search(r"_webplat_msg=(.*?)&", userData).group(1) != "norole":
            AchievePoint = re.search(r"AchievePoint=(.*?)&",
                                     userData).group(1)  # 成就点数
            Admiration = re.search(r"Admiration=(.*?)&",
                                   userData).group(1)  # 心动值
            Charm = re.search(r"Charm=(.*?)&", userData).group(1)  # 魅力值
            Money = re.search(r"Money=(.*?)&", userData).group(1)  # 酷币
            RegisterTime = re.search(r"RegisterTime=(.*?)&",
                                     userData).group(1)  # 飞车生日
            SuperMoney = re.search(r"SuperMoney=(.*?)&",
                                   userData).group(1)  # 点券
            country = re.search(r"country=(.*?)&", userData).group(1)  # 国家
            gamecount = re.search(r"gamecount=(.*?)&",
                                  userData).group(1)  # 参赛场次
            first = re.search(r"first=(.*?)&", userData).group(1)  # 冠军场次
            second = re.search(r"second=(.*?)&", userData).group(1)  # 亚军场次
            third = re.search(r"third=(.*?)&", userData).group(1)  # 季军场次
            honor = re.search(r"honor=(.*?)&", userData).group(1)  # 荣誉
            level = re.search(r"level=(.*?)&", userData).group(1)  # 等级
            name = re.search(r"name=(.*?)&", userData).group(1)  # 等级称号
            nick = re.search(r"nick=(.*?)&", userData).group(1)  # 昵称
            zone = re.search(r"zone=(.*?)&", userData).group(1)  # 大区
            msg += (f"昵称：{nick} 大区：{zone}\n"
                    f"等级：{level} ({name})\n"
                    f"👑 荣誉：{honor} ({country})\n"
                    f"🚗 参赛场次：{gamecount}\n"
                    f"🥇 冠军场次：{first}\n"
                    f"🥈 亚军场次：{second}\n"
                    f"🥉 季军场次：{third}\n"
                    f"⭐️ 成就点数：{AchievePoint}\n"
                    f"💗 心动值：{Admiration}\n"
                    f"💖 魅力：{Charm}\n"
                    f"💰️ 酷币：{Money}\n"
                    f"💸 点券：{SuperMoney}\n"
                    f"🎂 飞车生日：{RegisterTime}\n\n")
        area += 1
    try:
        send('周末大乐透扫码登陆', msg)
    except Exception as err:
        print('%s\n❌️错误，请查看运行日志！' % err)
    return msg


if __name__ == "__main__":
    print("✌ 请使用手机QQ扫描二维码")
    # 1、获取需要扫码的图片并切获取qrsig
    url = "https://ssl.ptlogin2.qq.com/ptqrshow?appid=21000118&daid=8&pt_3rd_aid=0"
    res_qr = requests.get(url)
    qrsig = res_qr.cookies.get('qrsig')
    # print("\nqrsig =", qrsig)

    # 打印二维码
    barcode_url = ''
    barcodes = decode(Image.open(io.BytesIO(res_qr.content)))
    for barcode in barcodes:
        barcode_url = barcode.data.decode("utf-8")

    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=2)
    qr.add_data(barcode_url)
    qr.make(fit=True)
    # invert=True白底黑块
    qr.print_ascii(invert=True)

    # 2、获取ptqrtoken
    ptqrtoken = get_ptqrtoken(qrsig)
    # print("ptqrtoken =", ptqrtoken)

    # 3、监控用户是否扫成功
    while (True):
        params = {
            "ptqrtoken":
            ptqrtoken,
            "u1":
            "https://speed.qq.com/act/a20210322dltn/index.html",
            "from_ui":
            "1",
            "daid":
            "8",
            "aid":
            "21000118",
            "login_sig":
            " uZtHa1fGAUJzEn4Xq1mr5sHCbfWWqw94Len2c-T1dfoIAhnQU3bnXp1ocFTo-mnD",
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        url = f"https://xui.ptlogin2.qq.com/ssl/ptqrlogin?{query_string}"
        res_login = requests.get(
            url=url,
            headers={
                'Cookie':
                '; '.join([
                    f'{key}={value}'
                    for key, value in res_qr.cookies.get_dict().items()
                ])
            })
        print(res_login.text)
        if "登录成功" in res_login.text:
            url = re.search(r"ptuiCB\('0','0','(.*?)','0','登录成功",
                            res_login.text).group(1)
            res = requests.get(
                url=url,
                headers={
                    'Cookie':
                    '; '.join([
                        f'{key}={value}'
                        for key, value in res_login.cookies.get_dict().items()
                    ])
                },
                allow_redirects=False)
            # 4、提取 skey p_uin pt4_token p_skey
            skey = res.cookies.get_dict().get('skey')
            p_uin = res.cookies.get_dict().get('uin')
            pt4_token = res.cookies.get_dict().get('pt4_token')
            p_skey = res.cookies.get_dict().get('p_skey')
            # g_tk = getG_tk(skey)
            # 5、获取用户数据
            getUserData(p_uin, skey)
            break
        # 两秒循环检测
        time.sleep(2)

    ck = f"skey={skey}; p_uin={p_uin}; pt4_token={pt4_token}; p_skey={p_skey};"
    print(f"\nck获取成功\n请将下面一段复制到cookie中\n"
          f"👇👇👇👇👇👇\n{ck} sArea=大区自行填写(1电信2联通);\n👆👆👆👆👆👆")
