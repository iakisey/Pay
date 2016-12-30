from alipay import AliPay

alipay = AliPay()

order = alipay.create_order('1', 0.01, 'test')

print(order)
