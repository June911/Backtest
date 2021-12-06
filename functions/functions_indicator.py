"""
Functions for all indicators
Can also be done with TA-LIB
"""

import numpy as np
import pandas as pd


def f_get_macd(df, FastMALen, SlowMALen, MACDLength):
    """
    计算 MACD
    """
    # 快均线
    FastEMA = f_ema(df, FastMALen)
    # 慢均线
    SlowEMA = f_ema(df, SlowMALen)
    # 离差值
    Dif = FastEMA - SlowEMA
    # 离差值平均
    Dea = f_ema(Dif, MACDLength)
    Result = Dif - Dea

    return Dif, Dea, Result


def f_get_bollinger_bands(df, bbLen, bbCoef):
    """
    计算 布林带
    :param df:
    :param bbLen: K lines period
    :param bbCoef: coefficient of standard deviation
    :return:
    """

    rolling_std = df.rolling(bbLen).std()
    rolling_avg = df.rolling(bbLen).mean()

    up_band = rolling_avg + bbCoef * rolling_std
    dn_band = rolling_avg - bbCoef * rolling_std

    return dn_band, rolling_avg, up_band


def f_get_rsi(df, rsiLen):
    """
    计算相对强弱指标，只用了 close, previous close

    :param df:
    :param rsiLen:
    :return:
    """
    up = np.maximum((df - df.shift(1)), 0)
    dn = np.maximum((df.shift(1) - df), 0)

    avg_up = f_ema(up, rsiLen)
    avg_dn = f_ema(dn, rsiLen)

    rs = avg_up / avg_dn
    rsi = 100 - 100 / (1+rs)

    # import matplotlib.pyplot as plt
    # plt.figure()
    # rsi.plot()
    # avg_dn.plot()

    return rsi


def f_get_truerange(df_high, df_low, df_close):
    """
    计算 真实波幅
    """
    high_minus_low = df_high - df_low
    abs_high_minus_close_y = (df_high - df_close.shift(1)).abs()
    abs_low_minus_close_y = (df_low - df_close.shift(1)).abs()

    true_range = pd.concat([high_minus_low, abs_high_minus_close_y, abs_low_minus_close_y], axis=1).max(axis=1)

    return true_range


def f_get_avg_truerange(df_high, df_low, df_close, ATRlength):
    """
    计算 atr
    """
    true_range = f_get_truerange(df_high, df_low, df_close)

    return true_range.rolling(ATRlength).mean()


def f_get_adx(df_high, df_low, df_close, adxLength):
    """
    计算 平均趋向指标[Average directional indicator]

    lagging indicator, meaning a trend must have established itself before the ADX will generate a signal that a trend
    is under way

    ADX readings below 20 indicate trend weakness, and readings above 40 indicate trend strength
    An extremely strong trend is indicated by readings above 50
    """
    up_move = df_high - df_high.shift(1)
    dn_move = df_low.shift(1) - df_low

    # 只有突破了前高或前低，才考虑
    con_dm_plus = (up_move > dn_move) & (up_move > 0)
    dm_plus = [up_move[idx] if con_dm_plus[idx] else 0 for idx in range(len(up_move))]
    dm_plus = pd.Series(dm_plus, index=up_move.index)

    con_dm_minus = (up_move < dn_move) & (dn_move > 0)
    dm_minus = [dn_move[idx] if con_dm_minus[idx] else 0 for idx in range(len(dn_move))]
    dm_minus = pd.Series(dm_minus, index=dn_move.index)

    # 取均值
    average_dm_plus = dm_plus.rolling(adxLength).mean()
    average_dm_minus = dm_minus.rolling(adxLength).mean()

    # 除以atr, 变成相对强弱,
    # 波动率修正后上涨和下跌趋势
    atr = f_get_avg_truerange(df_high, df_low, df_close, adxLength)
    di_plus = average_dm_plus / atr * 100
    di_minus = average_dm_minus / atr * 100

    # 只要有趋势行情，di_plus 和 di_minus 中就会有一个比较大
    dx = (di_plus - di_minus).abs() / (di_plus + di_minus) * 100
    adx = dx.rolling(adxLength).mean()

    return adx


def f_adaptive_moving_average(df_close, amaLen, n1=2, n2=30):

    direction = (df_close - df_close.shift(amaLen)).abs()

    abs_price_dif = df_close.diff().abs()
    volatility = abs_price_dif.rolling(amaLen).sum()

    efficiency_ratio = direction / volatility
    efficiency_ratio.fillna(method="ffill", inplace=True)

    fast = 2 / (n1+1)
    slow = 2 / (n2+1)

    scalar_constant = (efficiency_ratio * (fast - slow) + slow)**2

    ama = pd.Series(np.nan, index=df_close.index)
    ama[amaLen] = np.mean(df_close[:amaLen])
    for i in range(amaLen+1, len(ama)):
        if df_close[i] == np.nan:
            print(df_close[i])
        ama[i] = scalar_constant[i] * (df_close[i] - ama[i-1]) + ama[i-1]
    return ama


def f_ema(df, LenEMA):
    ema = df.iloc[:LenEMA].rolling(window=LenEMA, min_periods=LenEMA).mean()
    ema = pd.concat([ema, df[LenEMA:]]).ewm(span=LenEMA, min_periods=LenEMA).mean()
    return ema


def f_mma(df, LenMMA):
    mma = df.iloc[:LenMMA].rolling(window=LenMMA, min_periods=LenMMA).mean()
    mma = pd.concat([mma, df[LenMMA:]]).ewm(alpha=1/LenMMA, min_periods=LenMMA).mean()
    return mma


def f_ma(df, LenMA):
    ma = df.rolling(LenMA).mean()
    return ma