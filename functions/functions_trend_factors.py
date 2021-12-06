"""
趋势策略因子研究
"""


def f_factor_ma_v0_0(fast_ma, slow_ma):
    """
    MACD 金叉做多，死叉做空
    :param fast_ma:
    :param slow_ma:
    :return:
    """

    # 快线穿过慢线
    cross_ma = fast_ma - slow_ma

    # 快线上穿慢线
    con_DNcrossUP = (cross_ma.shift(1) < 0) & (cross_ma > 0)
    # 快线下穿慢线
    con_UPcrossDN = (cross_ma.shift(1) > 0) & (cross_ma < 0)

    """
    入场条件
    """

    # 快线上穿慢线， 短期买入意愿 > 长期买入意愿，金叉做多
    con_open_long = con_DNcrossUP
    # 快线下穿慢线， 短期卖出意愿 > 长期卖出意愿，死叉做空
    con_open_short = con_UPcrossDN

    """
    出场条件
    """
    # 反向出场
    con_close_long = con_UPcrossDN
    con_close_short = con_DNcrossUP

    return con_open_long, con_open_short, con_close_long, con_close_short


def f_factor_ma_v0_1(fast_ma, slow_ma, df_close):
    """
    MACD 金叉做多，死叉做空
    持多单时，向下突破慢均线止损；持空单时，向上突破慢均线止损
    :param fast_ma:
    :param slow_ma:
    :return:
    """

    # 快线穿过慢线
    cross_ma = fast_ma - slow_ma

    # 价格穿过慢线
    cross_ma_price = df_close - slow_ma

    # 快线上穿慢线
    con_DNcrossUP = (cross_ma.shift(1) < 0) & (cross_ma > 0)
    # 快线下穿慢线
    con_UPcrossDN = (cross_ma.shift(1) > 0) & (cross_ma < 0)

    # 价格上穿慢线
    con_PricecrossUP = (cross_ma_price.shift(1) < 0) & (cross_ma_price > 0)
    # 价格下穿慢线
    con_PricecrossDN = (cross_ma_price.shift(1) > 0) & (cross_ma_price < 0)

    """
    入场条件
    """

    # 快线上穿慢线， 短期买入意愿 > 长期买入意愿，金叉做多
    con_open_long = con_DNcrossUP
    # 快线下穿慢线， 短期卖出意愿 > 长期卖出意愿，死叉做空
    con_open_short = con_UPcrossDN

    """
    出场条件
    """
    # 反向出场
    con_close_long = con_PricecrossDN
    con_close_short = con_PricecrossUP

    return con_open_long, con_open_short, con_close_long, con_close_short


def f_factor_macd_v0_0(Result):
    """
    MACD 金叉做多，死叉做空
    :param Result:
    :return:
    """

    # DIF 从下往上穿过 DEA
    con_DNcrossUP = (Result.shift(1) < 0) & (Result > 0)
    # DIF 从上往下穿过 DEA
    con_UPcrossDN = (Result.shift(1) > 0) & (Result < 0)

    """
    入场条件
    """

    # DIF 从下往上穿过 DEA， 短期买入意愿 > 长期买入意愿，金叉做多
    # 增加一个主力买入值的辅助
    con_open_long = con_DNcrossUP
    # DIF 从上往下穿过 DEA， 短期卖出意愿 > 长期卖出意愿，死叉做空
    con_open_short = con_UPcrossDN

    """
    出场条件
    """
    # 反向出场
    con_close_long = con_UPcrossDN
    con_close_short = con_DNcrossUP

    return con_open_long, con_open_short, con_close_long, con_close_short


def f_factor_macd_v0_1(Result, Result_close):
    """
    金叉死叉出场太慢，考虑出场用更快的MACD
    - 本质上还是MACD，参数变多了，拟合程度变高了，可能出现过拟合现象
    """

    # DIF 从下往上穿过 DEA
    con_DNcrossUP = (Result.shift(1) < 0) & (Result > 0)
    con_DNcrossUP_close = (Result_close.shift(1) < 0) & (Result_close > 0)
    # DIF 从上往下穿过 DEA
    con_UPcrossDN = (Result.shift(1) > 0) & (Result < 0)
    con_UPcrossDN_close = (Result_close.shift(1) > 0) & (Result_close < 0)

    """
    入场条件
    """
    # DIF 从下往上穿过 DEA， 短期买入意愿 > 长期买入意愿，金叉做多
    # 增加一个主力买入值的辅助
    con_open_long = con_DNcrossUP
    # DIF 从上往下穿过 DEA， 短期卖出意愿 > 长期卖出意愿，死叉做空
    con_open_short = con_UPcrossDN

    """
    出场条件
    """
    # 反向出场
    con_close_long = con_UPcrossDN_close
    con_close_short = con_DNcrossUP_close

    return con_open_long, con_open_short, con_close_long, con_close_short


def f_factor_macd_bollinger_v0_0(Result, df, dnband, upband):
    """
    MACD 入场，布林带止损出场，或者MACD反方向出场
    """

    # MACD
    # DIF 从下往上穿过 DEA
    con_DNcrossUP = (Result.shift(1) < 0) & (Result > 0)
    # DIF 从上往下穿过 DEA
    con_UPcrossDN = (Result.shift(1) > 0) & (Result < 0)

    # Bollinger bands
    con_upbreak = (df.shift(1) < upband) & (df > upband)
    con_dnbreak = (df.shift(1) > dnband) & (df < dnband)

    """
    入场条件
    """
    # DIF 从下往上穿过 DEA， 短期买入意愿 > 长期买入意愿，金叉做多
    # 增加一个主力买入值的辅助
    con_open_long = con_DNcrossUP
    # DIF 从上往下穿过 DEA， 短期卖出意愿 > 长期卖出意愿，死叉做空
    con_open_short = con_UPcrossDN

    """
    出场条件
    """
    # 反向出场
    # 增加布林带止损
    # con_close_long = con_dnbreak
    # con_close_short = con_upbreak
    con_close_long = con_UPcrossDN | con_dnbreak
    con_close_short = con_DNcrossUP | con_upbreak

    return con_open_long, con_open_short, con_close_long, con_close_short


def f_factor_macd_bollinger_v0_1(Result, df, dnband, upband):
    """
    """

    # MACD
    # DIF 从下往上穿过 DEA
    con_DNcrossUP = (Result.shift(1) < 0) & (Result > 0)
    # DIF 从上往下穿过 DEA
    con_UPcrossDN = (Result.shift(1) > 0) & (Result < 0)

    # Bollinger bands
    con_upbreak = (df.shift(1) < upband) & (df > upband)
    con_dnbreak = (df.shift(1) > dnband) & (df < dnband)

    """
    入场条件
    """
    # DIF 从下往上穿过 DEA， 短期买入意愿 > 长期买入意愿，金叉做多
    # 增加一个主力买入值的辅助
    con_open_long = con_DNcrossUP
    # DIF 从上往下穿过 DEA， 短期卖出意愿 > 长期卖出意愿，死叉做空
    con_open_short = con_UPcrossDN

    """
    出场条件
    """
    # 反向出场
    # 增加布林带止损
    con_close_long = con_dnbreak
    con_close_short = con_upbreak
    # con_close_long = con_UPcrossDN | con_dnbreak
    # con_close_short = con_DNcrossUP | con_upbreak

    return con_open_long, con_open_short, con_close_long, con_close_short
