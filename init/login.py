# -*- coding=utf-8 -*-
from time import sleep

from config.ticketConf import _get_yaml
from damatuCode.damatuWeb import DamatuApi
from inter.GetPassCodeNewOrderAndLogin import getPassCodeNewOrderAndLogin
from inter.GetRandCode import getRandCode
from myException.UserPasswordException import UserPasswordException
from myException.balanceException import balanceException


class GoLogin:
    def __init__(self, session, is_auto_code, auto_code_type):
        self.session = session
        self.randCode = ""  # 打码后，的识别结果就放在这里
        self.is_auto_code = is_auto_code  # 是否自动打码
        self.auto_code_type = auto_code_type  # 如果自动打码，选择哪个 打码平台

    def auth(self):
        """认证"""
        authUrl = self.session.urls["auth"]
        authData = {"appid": "otn"}
        tk = self.session.httpClint.send(authUrl, authData)
        return tk

    def codeCheck(self):
        """
        验证码校验
        :return:
        """
        codeCheck = self.session.urls["codeCheck"]
        codeCheckData = {
            "answer": self.randCode,
            "rand": "sjrand",
            "login_site": "E"
        }
        # 发送验证码进行： 验证码的校验
        fresult = self.session.httpClint.send(codeCheck, codeCheckData)
        if "result_code" in fresult and fresult["result_code"] == "4":
            print(u"验证码通过,开始登录..")
            return True
        else:
            if "result_message" in fresult:
                print(fresult["result_message"])
            sleep(1)
            self.session.httpClint.del_cookies()

    def baseLogin(self, user, passwd):
        """
        登录过程
        :param user:
        :param passwd:
        :return: 权限校验码
        """
        logurl = self.session.urls["login"]
        logData = {
            "username": user,
            "password": passwd,
            "appid": "otn"
        }
        tresult = self.session.httpClint.send(logurl, logData)
        if 'result_code' in tresult and tresult["result_code"] == 0:
            print(u"登录成功")
            tk = self.auth()
            if "newapptk" in tk and tk["newapptk"]:
                return tk["newapptk"]
            else:
                return False
        elif 'result_message' in tresult and tresult['result_message']:
            messages = tresult['result_message']
            if messages.find(u"密码输入错误") is not -1:
                raise UserPasswordException("{0}".format(messages))
            else:
                print(u"登录失败: {0}".format(messages))
                print(u"尝试重新登陆")
                return False
        else:
            return False

    def getUserName(self, uamtk):
        """
        登录成功后,显示用户名
        :return:
        """
        if not uamtk:
            return u"权限校验码不能为空"
        else:
            uamauthclientUrl = self.session.urls["uamauthclient"]
            data = {"tk": uamtk}
            uamauthclientResult = self.session.httpClint.send(uamauthclientUrl, data)
            if uamauthclientResult:
                if "result_code" in uamauthclientResult and uamauthclientResult["result_code"] == 0:
                    print(u"欢迎 {} 登录".format(uamauthclientResult["username"]))
                    return True
                else:
                    return False
            else:
                self.session.httpClint.send(uamauthclientUrl, data)
                url = self.session.urls["getUserInfo"]
                self.session.httpClint.send(url)

    def go_login(self):
        """
        登陆
        :param user: 账户名
        :param passwd: 密码
        :return:
        """
        if self.is_auto_code and self.auto_code_type == 1:
            # 打码兔平台
            balance = DamatuApi(_get_yaml()["auto_code_account"]["user"], _get_yaml()["auto_code_account"]["pwd"]).getBalance()
            if int(balance) < 40:
                raise balanceException(u'余额不足，当前余额为: {}'.format(balance))
        #
        user, passwd = _get_yaml()["set"]["12306account"][0]["user"], _get_yaml()["set"]["12306account"][1]["pwd"]
        if not user or not passwd:
            raise UserPasswordException(u"温馨提示: 用户名或者密码为空，请仔细检查")
        login_num = 0
        while True:  # 如果下载验证码失败，就会一直尝试下载
            result = getPassCodeNewOrderAndLogin(session=self.session, imgType="login")  # 现在验证码
            if not result:
                continue
            # 验证码识别
            self.randCode = getRandCode(self.is_auto_code, self.auto_code_type, result)
            login_num += 1
            self.auth()  #
            if self.codeCheck():  # 验证码 输入
                uamtk = self.baseLogin(user, passwd)  # 实际的登陆过程
                if uamtk:
                    self.getUserName(uamtk)
                    break


# if __name__ == "__main__":
#     # main()
#     # logout()
