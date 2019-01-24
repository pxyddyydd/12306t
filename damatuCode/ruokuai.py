# coding:utf-8
import requests
from hashlib import md5


class RClient(object):  # 验证码识别类

    def __init__(self, username, password):
        self.username = username
        try:
            self.password = md5(password).hexdigest()
        except TypeError:
            self.password = md5(password.encode('utf-8')).hexdigest()
        self.soft_id = '121207'
        self.soft_key = 'd2c669b2a76d4443a18e187409161f65'
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):  # 调用打码接口，获取打码结果
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        print(r)
        res = r.json()
        img_path = "./image/{a}-{b}.png".format(a=res["Id"], b=res["Result"])
        with open(img_path, 'wb') as fp:
            fp.write(im)  # 图片字节 写入  变量
        return res

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()


if __name__ == '__main__':
    rc = RClient('wa', '16')
    im = open('test.png', 'rb').read()
    print(rc.rk_create(im, 6113))  # 这是本次打码的返回结果
    # {'Result': '18', 'Id': '55b84614-2326-4b6a-9dbe-0d385c903411'}

