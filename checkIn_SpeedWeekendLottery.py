'''
new Env('周末大乐透')
cron: 0 0 * * 7
Author: BNDou
Date: 2024-08-04 16:35:13
LastEditTime: 2024-08-05 03:08:40
FilePath: \Auto_Check_In\checkIn_SpeedWeekendLottery.py
Description  :
飞车PC端活动-周末大乐透
默认 每周日 0 点执行
配合 checkIn_SpeedWeekendLottery_getCK.py 使用
先运行 checkIn_SpeedWeekendLottery_getCK.py 复制返回值粘贴到环境变量 COOKIE_DALETOU 中即可
'''
import os
import re
import sys
import threading
import requests

# 测试用环境变量
# os.environ['COOKIE_DALETOU'] = ''

try:  # 异常捕捉
    from utils.notify import send  # 导入消息通知模块
except Exception as err:  # 异常捕捉
    print('%s\n❌加载通知服务失败~' % err)


def get_env():
    '''
    获取环境变量
    :return: 环境变量
    '''
    # 判断 COOKIE_DALETOU 是否存在于环境变量
    if "COOKIE_DALETOU" in os.environ:
        # 读取系统变量以 \n 或 && 分割变量
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_DALETOU'))
    else:
        # 标准日志输出
        print('❌未添加 COOKIE_DALETOU 变量')
        send('周末大乐透', '❌未添加 COOKIE_DALETOU 变量')
        # 脚本退出
        sys.exit(0)

    return cookie_list


class WeekendLottery(threading.Thread):
    def __init__(self, cookie):
        super().__init__()
        self.cookie = cookie
        self.p_uin = re.search(r'p_uin=(\S+);', cookie).group(1)
        self.sArea = re.search(r'sArea=(\S+);', cookie).group(1)
        self.g_tk = self.getG_tk(re.search(r'skey=(\S+);', cookie).group(1))

    def getG_tk(self, skey):
        """官方算法：根据skey计算g_tk"""
        hash = 5381
        for i in range(len(skey)):
            hash += (hash << 5) + ord(skey[i])
        return hash & 2147483647

    def getRemainingLotteryCount(self):
        '''
        查询剩余抽奖次数
        '''
        url = f"https://comm.ams.game.qq.com/ams/ame/amesvr?iActivityId=369402"
        headers = {'Cookie': self.cookie}
        data = {
            "sArea": self.sArea,
            "sServiceType": "speed",
            "iActivityId": "369402",
            "iFlowId": "750956",
            "g_tk": self.g_tk
        }
        response = requests.post(url, headers=headers, data=data).json()
        if response["flowRet"]["iRet"] == "0":
            count = int(response['modRet']['sOutValue1']) // 50 - int(
                response['modRet']['sOutValue2'])
            return f"本周活跃度：{response['modRet']['sOutValue1']}\n剩余抽奖次数：{count}\n", count
        else:
            return response["flowRet"]["sMsg"] + "\n", None

    def lottery(self):
        '''
        抽奖
        '''
        url = f"https://comm.ams.game.qq.com/ams/ame/amesvr?iActivityId=369402"
        headers = {'Cookie': self.cookie}
        data = {
            "sArea": self.sArea,
            "sServiceType": "speed",
            "iActivityId": "369402",
            "iFlowId": "750765",
            "g_tk": self.g_tk
        }
        response = requests.post(url, headers=headers, data=data).json()
        if response["flowRet"]["iRet"] == "0":
            return response["modRet"]["sMsg"] + "\n"
        else:
            return response["flowRet"]["sMsg"] + "\n"

    def run(self):
        '''
        主函数
        '''
        msg = f"🚗账号 {self.p_uin} {'电信区' if self.sArea == '1' else '联通区' if self.sArea == '2' else '电信2区'}\n"
        # 查询次数
        log, count = self.getRemainingLotteryCount()
        msg += log

        # 抽奖
        if count is not None and count > 0 and count < 8:
            msg += "🎉开始抽奖\n"
            while count > 0:
                msg += self.lottery()
                count -= 1
        return msg


def main():
    msg = ""
    threads = []
    global cookie_daletou
    cookie_daletou = get_env()

    print("✅检测到共", len(cookie_daletou), "个飞车账号")

    i = 0
    while i < len(cookie_daletou):
        # 执行任务
        threads.append(WeekendLottery(cookie_daletou[i]))
        i += 1

    # 启动线程
    for t in threads:
        t.start()
    # 关闭线程
    for t in threads:
        t.join()
    # 获取返回值
    for t in threads:
        msg += t.run() + "\n"

    return msg


if __name__ == "__main__":
    print("----------周末大乐透开始抽奖----------")
    msg = main()
    print("----------周末大乐透执行完毕----------")

    try:
        send('周末大乐透', msg)
    except Exception as err:
        print('%s\n❌错误，请查看运行日志！' % err)
