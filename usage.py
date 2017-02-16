def wx_main():
    """TODO: Docstring for wx_main.
    :returns: TODO

    """
    from pay import wxpay
    wxpay.wx_app()


def alipay_main():
    """TODO: Docstring for alipay_main.
    :returns: TODO

    """
    from pay import alipay
    # print(alipay.trade_app_pay('1', 0.01, 'test'))

    print(alipay.parse_response(
        get(
            alipay.trade_query('20161112111')[0],
            alipay.trade_query('20161112111')[1]).text,
        'query'))

    print(alipay.parse_response(
        get(
            alipay.trade_refund('20161112111', '2.00')[0],
            alipay.trade_refund('20161112111', '2.00')[1]).text,
        'refund'))

    print(alipay.parse_response(
        get(
            alipay.trade_cancel('20161112111')[0],
            alipay.trade_cancel('20161112111')[1]).text,
        'cancel'))

    print(alipay.parse_response(
        get(
            alipay.trade_refund_query('20161112111')[0],
            alipay.trade_refund_query('20161112111')[1]).text,
        'refund_query'))

    print(alipay.parse_response(
        get(
            alipay.trade_close('201611121111')[0],
            alipay.trade_close('201611121111')[1]).text,
        'close'))


if __name__ == "__main__":
    from requests import get
    alipay_main()
