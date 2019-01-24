# encoding=utf8
import collections
import json
import os
import re
import sys
import csv
import requests
UP_FOLDER = os.path.dirname(os.path.split(os.path.realpath(__file__))[0])  # 这样你就获得了本文件所在目录的上一层
sys.path.append(UP_FOLDER)
from config import urlConf


try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError:
    pass


class CDNProxy:
    def __init__(self, host=None):
        self.host = host
        self.urlConf = urlConf.urls  # 获取12306的各种接口URL
        self.httpClint = requests  # 使用request来进行HTTP发送
        self.city_list = []
        self.timeout = 5

    @staticmethod
    def _set_header():
        """设置header"""
        return {
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Requested-With": "xmlHttpRequest",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
            "Referer": "https://kyfw.12306.cn/otn/login/init",
            "Accept": "*/*",
        }

    def get_city_id(self):
        """
        获取所有城市md5参数  #！！！ 照我看，这个函数是获取所有的 快速CDN列表 的
        相当于 获取 最新的CDN列表
        :return:
        """
        try:
            if self.host:
                while True:
                    url = self.urlConf["cdn_host"]["req_url"]  # http://ping.chinaz.com/kyfw.12306.cn
                    data = {"host": self.host, "lintType": "电信,多线,联通,移动"}
                    rep = self.httpClint.post(url, data, headers=self._set_header(), timeout=self.timeout)
                    city_re = re.compile(r"<li id=\"(\S+)\" class=\"PingListCent PingRLlist")
                    self.city_list = re.findall(city_re, rep.content)
                    if self.city_list:
                        print(self.city_list)
                        break
            else:
                pass
        except:
            pass

    @staticmethod
    def open_cdn_file():  # 返回CDN IP列表(这个文件中写了一部分的CDN列表)
        cdn = []
        path = os.path.join(os.path.dirname(__file__), '../cdn_list')  # 读取CDN IP列表
        with open(path, "r") as f:
            for i in f.readlines():
                # print(i.replace("\n", ""))
                if i and "kyfw.12306.cn:443" not in i:
                    cdn.append(i.replace("\n", ""))
            return cdn


if __name__ == '__main__':
    cdn = CDNProxy(True)
    # print(cdn.open_cdn_file())
    cdn.get_city_id()
