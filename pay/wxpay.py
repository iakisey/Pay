from hashlib import md5
from random import sample
from urllib.request import urlopen
from string import ascii_letters, digits
from xml.etree.ElementTree import fromstring

from . import config


class WxPay:
    '''支付类'''
    def __init__(self):
        self.__nonce_len = 32
        self.__parameters = {}
        self.wx_url = 'https://api.mch.weixin.qq.com/pay/unifiedorder'

    def nonce_str(self):
        '''产生随机字符串，不长于32位'''
        return ''.join(sample(ascii_letters + digits, self.__nonce_len))

    @staticmethod
    def dict2xml(diction):
        '''dict转xml'''
        xml = ['<xml>']
        [xml.append('<{0}>{1}</{0}>'.format(k, v)) for k, v in diction.items()]
        xml.append('</xml>')
        return ''.join(xml)

    @staticmethod
    def xml2dict(xml):
        '''将xml转为dict'''
        data = {}
        [data.setdefault(child.tag, child.text) for child in fromstring(xml)]
        return data

    def gen_wx_app_parameters(self):
        '''微信app支付所需参数集'''
        parameters = {
            'appid': config['wx.app']['appid'],  # 应用ID
            'mch_id': config['wx.app']['mch_id'],  # 商户号
            'nonce_str': '1234567890',  # 随机字符串
            'body': 'test',  # 商品描述
            'out_trade_no': '1234567890',  # 商户订单号
            'total_fee': '1',  # 总金额
            'spbill_create_ip': config['wx.app']['spbill_create_ip'],  # 终端IP
            'notify_url': config['wx.app']['notify_url'],  # 通知地址
            'trade_type': 'APP'  # 交易类型
        }
        extra_parameters = {
            'device_info': '',  # 设备号
            'sign_type': '',  # 签名类型
            'detail': '',  # 商品详情 CDATA
            'attach': '',  # 附加数据
            'fee_type': '',  # 货币类型
            'time_start': '',  # 交易起始时间
            'time_expire': '',  # 交易结束时间
            'goods_tag': '',  # 商品标记
            'limit_pay': '',  # 指定支付方式
        }
        parameters.update(
            {k: extra_parameters[k] for k in extra_parameters.keys()
                if extra_parameters[k]}
        )
        self.__parameters = parameters

    def gen_wx_mp_parameters(self):
        '''微信公众号支付所需参数集'''
        parameters = {
            'appid': config['wx.mp']['appid'],  # 应用ID
            'mch_id': config['wx.mp']['mch_id'],  # 商户号
            'nonce_str': '1234567890',  # 随机字符串
            'body': 'test',  # 商品描述
            'out_trade_no': '1234567890',  # 商户订单号
            'total_fee': '1',  # 总金额
            'spbill_create_ip': config['wx.mp']['spbill_create_ip'],  # 终端IP
            'notify_url': config['wx.mp']['notify_url'],  # 通知地址
            'trade_type': 'JSAPI',  # 交易类型
            'openid': 'opY6KuLmqHTHJC7JKV-TxS3cblJI',  # 用户标识
        }
        extra_parameters = {
            'device_info': '',  # 设备号
            'sign_type': '',  # 签名类型
            'detail': '',  # 商品详情 CDATA
            'attach': '',  # 附加数据
            'fee_type': '',  # 货币类型
            'time_start': '',  # 交易起始时间
            'time_expire': '',  # 交易结束时间
            'goods_tag': '',  # 商品标记
            'product_id': '',  # 商品ID
            'limit_pay': '',  # 指定支付方式
        }
        parameters.update(
            {k: extra_parameters[k] for k in extra_parameters.keys()
                if extra_parameters[k]}
        )
        self.__parameters = parameters

    def __wx_sign(self, key):
        '''微信签名'''
        stringA = '&'.join(
            ['{}={}'.format(a, self.__parameters[a]) for a in sorted(
                self.__parameters.keys())])
        stringA += '&{}={}'.format('key', key)
        hash_md5 = md5()
        hash_md5.update(stringA.encode())
        return hash_md5.hexdigest().upper()

    def wx_app(self):
        '''微信支付'''
        self.gen_wx_app_parameters()
        self.__parameters['sign'] = self.__wx_sign(config['wx.app']['key'])
        xml = self.dict2xml(self.__parameters)
        a = urlopen(self.wx_url, xml.encode()).read().decode()
        print(self.xml2dict(a))

    def wx_mp(self):
        '''微信公众号支付'''
        self.gen_wx_mp_parameters()
        self.__parameters['sign'] = self.__wx_sign(config['wx.mp']['key'])
        xml = self.dict2xml(self.__parameters)
        a = urlopen(self.wx_url, xml.encode()).read().decode()
        print(self.xml2dict(a))
