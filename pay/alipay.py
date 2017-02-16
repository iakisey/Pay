from os.path import join, dirname
from json import loads, dumps
from datetime import datetime
from urllib.parse import quote_plus
from base64 import b64encode, b64decode

from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5


from . import config


class AliPay(object):
    """docstring for AliPay"""
    def __init__(self):
        self.__appid = config['alipay']['appid']
        self.__ali_url = config['alipay']['ali_url']
        self.__notify_url = config['alipay']['notify_url']
        self.__private_key = join(dirname(__file__), config['alipay']['private_key'])
        self.__ali_public_key = join(dirname(__file__), config['alipay']['ali_public_key'])

        self.__parameters = {}

    def gen_parameters(self, method, biz_content):
        """生成支付宝所需参数

        :method:      str
        :biz_content: dict 请求参数的集合
        :returns:     None

        """
        self.__parameters.update({
            'app_id': self.__appid,
            'method': method,
            'charset': 'utf-8',
            'sign_type': 'RSA',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': dumps(biz_content, sort_keys=True).replace(
                ' ', '')
        })

    def gen_str(self, quoted=0):
        """生成字符串参数集

        :quoted:  bool 是否对字符串编码
        :returns: str  排序后参数集

        """
        self.__parameters = {
            k: quote_plus(v) for k, v in self.__parameters.items()} \
            if quoted else self.__parameters
        return '&'.join(
            '{}={}'.format(k, v) for k, v in sorted(self.__parameters.items()))

    def __ali_sign(self, unsigned_str):
        """签名

        :unsigned_str: str  未签名字符串
        :returns:      str  签名字符串

        """
        with open(self.__private_key, 'r') as f:
            private_key = RSA.importKey(f.read())
        signer = PKCS1_v1_5.new(private_key)
        digest = SHA.new()
        digest.update(unsigned_str.encode())
        sign = signer.sign(digest)
        return b64encode(sign).decode()

    def sync_check_sign(self, msg, signature):
        """同步验签

        :msg:       str 待验签信息
        :signature: str 签名
        :returns:   bool

        """
        with open(self.__ali_public_key) as f:
            rsakey = RSA.importKey(f.read())
        verifier = PKCS1_v1_5.new(rsakey)
        digest = SHA.new()
        digest.update(msg.encode())
        return verifier.verify(digest, b64decode(signature))

    def trade_app_pay(self, out_trade_no, total_amount, subject):
        """APP支付

        :out_trade_no: str  唯一订单号
        :total_amount: str  总金额
        :subject:      str  主题
        :returns:      str  最终的请求字符串

        """
        self.__parameters['notify_url'] = self.__notify_url
        self.gen_parameters(
            'alipay.trade.app.pay',
            {
                'subject': subject,
                'out_trade_no': out_trade_no,
                'total_amount': total_amount,
                'product_code': 'QUICK_MSECURITY_PAY'
            }
        )
        sign = self.__ali_sign(self.gen_str())
        return self.gen_str(1) + '&sign=' + quote_plus(sign)

    def trade_query(self, out_trade_no):
        """统一收单线下交易查询

        :out_trade_no: str    唯一订单号
        :returns:      tuple  (url, data, method)

        """
        self.gen_parameters(
            'alipay.trade.query',
            {'out_trade_no': out_trade_no}
        )
        sign = self.__ali_sign(self.gen_str())
        data = self.gen_str(1) + '&sign=' + quote_plus(sign)
        return self.__ali_url, data, 'GET'

    def trade_refund(self, out_trade_no, refund_amount):
        """统一收单交易退款接口

        :out_trade_no:  str    唯一订单号
        :refund_amount: str    退款金额
        :returns:       tuple  (url, data, method)

        """
        self.gen_parameters(
            'alipay.trade.refund',
            {
                'out_trade_no': out_trade_no,
                'refund_amount': refund_amount,
                # 'refund_reason': refund_reason,
            }
        )
        sign = self.__ali_sign(self.gen_str())
        data = self.gen_str(1) + '&sign=' + quote_plus(sign)
        return self.__ali_url, data, 'GET'

    def trade_cancel(self, out_trade_no):
        """统一收单交易撤销接口

        :out_trade_no:  str    唯一订单号
        :returns:       tuple  (url, data, method)

        """
        self.gen_parameters(
            'alipay.trade.cancel',
            {'out_trade_no': out_trade_no}
        )
        sign = self.__ali_sign(self.gen_str())
        data = self.gen_str(1) + '&sign=' + quote_plus(sign)
        return self.__ali_url, data, 'GET'

    def trade_refund_query(self, out_trade_no):
        """统一收单交易退款查询: 商户可使用该接口查询自已通过alipay.trade.refund提交的退款请求是否执行成功。

        :out_trade_no:  str    唯一订单号
        :returns:       tuple  (url, data, method)

        """
        self.gen_parameters(
            'alipay.trade.fastpay.refund.query',
            {
                'out_trade_no': out_trade_no,
                'out_request_no': out_trade_no,
            }
        )
        sign = self.__ali_sign(self.gen_str())
        data = self.gen_str(1) + '&sign=' + quote_plus(sign)
        return self.__ali_url, data, 'GET'

    def trade_close(self, out_trade_no):
        """统一收单交易关闭接口: 用于交易创建后，用户在一定时间内未进行支付，可调用该接口直接将未付款的交易进行关闭。

        :out_trade_no:  str    唯一订单号
        :returns:       tuple  (url, data, method)

        """
        self.gen_parameters(
            'alipay.trade.close',
            {'out_trade_no': out_trade_no}
        )
        sign = self.__ali_sign(self.gen_str())
        data = self.gen_str(1) + '&sign=' + quote_plus(sign)
        return self.__ali_url, data, 'GET'

    def parse_response(self, resp, tag):
        """解析支付宝各接口返回的字符串，包括验签

        :resp:    str 'the response of http request'
        :tag:     str 'query|refund|cancel|refund_query|close'
        :returns: dict

        """
        TAG = {
            'query': 'alipay_trade_query_response',
            'refund': 'alipay_trade_refund_response',
            'cancel': 'alipay_trade_cancel_response',
            'refund_query': 'alipay_trade_fastpay_refund_query_response',
            'close': 'alipay_trade_close_response',
        }
        try:
            msg = resp[resp.index('{', 1):resp.index('}')+1]
            signature = loads(resp)['sign']
        except Exception as e:
            print('Exception:', e)
        return loads(resp)[TAG[tag]] if self.sync_check_sign(
            msg, signature) else 'something wrong'
