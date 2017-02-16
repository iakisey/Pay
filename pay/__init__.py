from os.path import dirname, join
from configparser import ConfigParser

config = ConfigParser()
config.read(join(dirname(__file__), 'config'))

from .alipay import AliPay
from .wxpay import WxPay
alipay, wxpay = AliPay(), WxPay()
