# 场景介绍
- 前端：
    - 基于apicloud开发平台的H5

- 后端：
    - 基于tornado的python后端框架


开发资料：[alipay](https://doc.open.alipay.com/docs/doc.htm?treeId=204&articleId=105051&docType=1)


缘由：支付宝没有提供基于Python的SDK，也没有提供类似的接口调试工具，开发过程中踩过好几个坑，特别是在==SHA1withRSA==签名与验签部分。

# 具体过程

## 准备

生成一对公钥、密钥

公钥保存在支付宝应用公钥中

![](https://github.com/iakisey/Pay/raw/master/pic/1.png)

![](https://github.com/iakisey/Pay/raw/master/pic/2.png)

私钥保存在服务器中


## 请求参数

文档：[App支付请求参数说明](https://doc.open.alipay.com/docs/doc.htm?spm=a219a.7629140.0.0.VpgOc2&treeId=204&articleId=105465&docType=1)

代码：

```

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
                'subject': subject,  # 主题
                'out_trade_no': out_trade_no,  # 订单编号
                'total_amount': total_amount,  # 总金额
                'product_code': 'QUICK_MSECURITY_PAY'},
            sort_keys=True).replace(' ', '')
    }
```

其中`biz_content`字段需要注意：这个是具体业务参数的集合，类型是字符串，各个具体参数需要按字母排序，还要去除掉空字符。


## 未签名原始字符串

请求参数按照key=value&key=value方式拼接的未签名原始字符串


```
unsigned_str = '&'.join('{}={}'.format(k, v) for k, v in sorted(self.__parameters.items()))
```
需要注意的是：排序前要对参数字典进行按字母顺序排序

## 签名

支付宝采取SHA1withRSA签名方式，而python标准库没有提供相应的库来支持，所以这里采用第三方库`pycrypto`

安装：`pip install pycrypto`

引用：
```
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
```

注：这里还需要一对rsa的公、密钥，公钥需要上传到支付宝的应用公钥，私钥保存在服务器上，待会要引用私钥地址。

具体实现：

```
from base64 import b64encode
    
def __ali_sign(self, unsigned_str):
    with open(self.__private_key, 'r') as f:
        private_key = RSA.importKey(f.read())
    signer = PKCS1_v1_5.new(private_key)
    digest = SHA.new()
    digest.update(unsigned_str.encode())
    sign = signer.sign(digest)
    return b64encode(sign).decode()
```

## 获得最终的请求字符串

支付宝给出的方式：

> 最后对请求字符串的所有一级value（biz_content作为一个value）进行encode，编码格式按请求串中的charset为准，没传charset按UTF-8处理，获得最终的请求字符串

我的建议的：
先对构建的参数字典的每个value指进行quote，最后再拼接sign字段

```
from urllib.parse import quote_plus

self.__parameters = {k: quote_plus(v) for k, v in self.__parameters.items()}
signed_str = '{}={}'.format(k, v) for k, v in sorted(self.__parameters.items()))

signed_str += '&sign=' += quote_plus(sign)
```

最后讲`signed_str`传给前端


[代码地址](https://github.com/iakisey/Pay/blob/master/alipay/__init__.py)
