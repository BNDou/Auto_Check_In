'''
new Env('掌上飞车扫码登陆-目前仅支持寻宝')
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
Date: 2024-04-11 22:20:35
LastEditTime: 2026-04-13 00:48:21
FilePath: \Auto_Check_In\checkIn_ZhangFei_getToken.py
Description: 
'''

import sys
import io
import re
import time

import qrcode
import requests
try:
    from PIL import Image
    from pyzbar.pyzbar import decode
except ModuleNotFoundError as e:
    if "PIL" in str(e):
        print(f"❌ {e}\n请到依赖管理中安装python环境的“pillow”")
    elif "pyzbar" in str(e):
        print(f"❌ {e}\n请到依赖管理中安装python环境的“pyzbar”")
    sys.exit()
except ImportError as e:
    print(f"❌ {e}\n请安装 zbar 库，安装指令：apk add zbar-dev")
    sys.exit()


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


if __name__ == "__main__":
    print("🔴 没事不要随便扫，防止token失效")
    print("🔴 获取的ck只能用于寻宝脚本，签到等其他功能缺少token参数")
    print("✌ 请使用手机QQ扫描二维码")
    # 1、获取需要扫码的图片并切获取qrsig
    url = "https://xui.ptlogin2.qq.com/ssl/ptqrshow?daid=381&appid=716027609&pt_3rd_aid=1105330667"
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
            "ptqrtoken": ptqrtoken,
            "u1": "http://connect.qq.com",
            "from_ui": "1",
            "daid": "381",
            "aid": "716027609",
            "pt_3rd_aid": "1105330667",
            "pt_openlogin_data": "refer_cgi%3Dm_authorize%26response_type%3Dtoken%26client_id%3D1105330667%26redirect_uri%3Dauth%253A%252F%252Ftauth.qq.com%252F%26",
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
            # 4、提取 openid appid access_token
            openid = re.search(r"openid=(\w+)", res_login.text).group(1)
            appid = re.search(r"appid=(\w+)", res_login.text).group(1)
            access_token = re.search(r"access_token=(\w+)",
                                     res_login.text).group(1)
            print(f"\nck获取成功\n请将下面一段复制到cookie中\n"
                f"👇👇👇👇👇👇\nroleId=QQ号; userId=掌飞社区ID号; accessToken={access_token}; appid={appid}; openid={openid}; areaId=电信一1联通2电信二3; enable_signin=false; enable_shopping=false; enable_treasure=true;\n👆👆👆👆👆👆"
            )
            break
        # 两秒循环检测
        time.sleep(2)
