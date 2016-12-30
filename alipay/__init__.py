import json
from base64 import b64encode
from datetime import datetime
from urllib.parse import quote_plus

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from configparser import ConfigParser
config = ConfigParser()
config.read('config')


class AliPay:
    def __init__(self):
        self.__appid = config['alipay']['appid']
        self.__notify_url = config['alipay']['notify_url']
        self.__private_key = config['alipay']['private_key']

        self.__parameters = {}

    def gen_parameters(self, out_trade_no, total_amount, subject):
        self.__parameters = {
            'app_id': self.__appid,
            'method': 'alipay.trade.app.pay',
            'charset': 'utf-8',
            'sign_type': 'RSA',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'notify_url': self.__notify_url,
            'biz_content': json.dumps(
                {
                    'subject': subject,
                    'out_trade_no': out_trade_no,
                    'total_amount': total_amount,
                    'product_code': 'QUICK_MSECURITY_PAY'},
                sort_keys=True).replace(' ', '')
        }

    def get_str(self, quoted=0):
        self.__parameters = {
            k: quote_plus(v) for k, v in self.__parameters.items()} \
            if quoted else self.__parameters
        return '&'.join(
            '{}={}'.format(k, v) for k, v in sorted(self.__parameters.items()))

    def __ali_sign(self, unsigned_str):
        with open(self.__private_key, 'r') as f:
            private_key = RSA.importKey(f.read())
        signer = PKCS1_v1_5.new(private_key)
        digest = SHA.new()
        digest.update(unsigned_str.encode())
        sign = signer.sign(digest)
        return b64encode(sign).decode()

    def create_order(self, out_trade_no, total_amount, subject):
        self.gen_parameters(out_trade_no, total_amount, subject)
        sign = self.__ali_sign(self.get_str())
        return self.get_str(1) + '&sign=' + quote_plus(sign)
