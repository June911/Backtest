"""
Functions to handle data
"""

import os
import pandas as pd
import numpy as np


def get_data(file_name, from_database=False, from_params=False):
    """
    获取数据
    """
    project_path = os.getcwd()
    data_path = project_path + "/data"

    # 读取文件
    if from_database:
        df = pd.read_csv(os.path.join(data_path, file_name), header=[0, 1], index_col=[0])
        if df.columns.nlevels == 2:
            df = df.droplevel(0, 1)
            df = df[["open", "high", "low", "close", "volume"]]
            df.index = pd.to_datetime(df.index)

    elif from_params:
        df = pd.read_excel(os.path.join(data_path, file_name), index_col=0)

    else:
        df = pd.read_csv(os.path.join(data_path, file_name), index_col=0)
        df.index = pd.to_datetime(df.index)
        if "Open" in df.columns:
            df.rename(columns={"Open": "open", "High": "high", "Close": "close", "Low": "low", "Volume": "volume"},
                      inplace=True)

    # handle missing data
    # for i in range(len(df)-1):
    #     next_m = df.index[i] +  pd.Timedelta(minutes=1)
    #     if next_m != btc_current.index[i+1]:
    #         print('-'*80)
    #         print(i)
    #         print("预测值  ", next_m)
    #         print("实际值  ", btc_current.index[i+1])
    #         next_m = btc_current.index[i+1]
    #

    return df


def f_change_barperiod(df, freq):
    """
    K线转换
    eg: from

    :param df:
    :param freq: Y, Q, M, W, D, H, T(min), S
    :return: 新周期的K线图
    """

    group_c = df.groupby(pd.Grouper(freq=freq))

    index = group_c.nth(0).index
    open = group_c.nth(0)['open']
    high = group_c["high"].max()
    low = group_c["low"].min()
    close = group_c.tail(1)['close']
    volume = group_c["volume"].sum()
    avg_price = group_c["open"].mean()

    df_new = pd.DataFrame()
    df_new["open"] = open
    df_new["high"] = high
    df_new["low"] = low
    df_new["close"] = close.values
    df_new["volume"] = volume
    df_new["avg_price"] = avg_price
    df_new.index = index

    # groupby 可能 创造新的 index, 本身数据不存在，导致右面索引出现问题
    # 只取交集的部分
    df_new = df_new.loc[df.index.intersection(df_new.index), :]

    return df_new


def f_change_to_time(df, freq):
    """
    标记这个时间段，属于每天中的哪些时间区间

    :param df:
    :return:
    """

    # 先换算成想要的时间评率
    df = f_change_barperiod(df, freq)

    df_new = df.copy()
    df_new["timeofday"] = df.groupby(lambda x: x.time).grouper.group_info[0]

    # if box_plot:
    #     df_new.boxplot(column=["volume"], by=["timeofday"])

    return df_new


def f_drop_timezone(df):
    """
    Set timezome to None
    :param df:
    :return:
    """
    df.index = df.index.tz_convert(None)
    df.index = df.index.astype(str)
    return df


def f_get_returns_from_specific_time_range(df, lst_time):
    """

    :param df:
    :param lst_time: eg. [22, 0, 7]
    :return:
    """
    df_timeofday = f_change_to_time(df, "1H")

    bool = df_timeofday["timeofday"].apply(lambda x: x in lst_time)
    df_close_inrange = df_timeofday.close[bool]
    df_rets_inrange = df_close_inrange.pct_change().shift(-1)
    df_rets_inrange = df_rets_inrange.to_frame()

    df_rets_inrange["timeofday"] = df_rets_inrange.groupby(lambda x: x.time).grouper.group_info[0]

    x = df_rets_inrange[(df_rets_inrange["timeofday"] == 2)]["close"]
    y = df_rets_inrange[(df_rets_inrange["timeofday"] == 0)]["close"]
    lst = []
    for i in range(392):
        next_rets_index = x.index[i] + pd.Timedelta("2H")
        try:
            next_rets = y.loc[next_rets_index]
            lst.append(next_rets)
        except:
            print(next_rets_index)
            lst.append(np.nan)

    df_results = pd.DataFrame(data=np.transpose([x.to_list(), lst]), index=x.index, columns= ["x", "y"])
    return df_results


"""
信号处理
"""

def processing_signal(con_open_long, con_open_short, con_close_long, con_close_short, freq):
    """
    获取开平仓信号
        # 信号 ==> [000001111100000-1-1-100000...]
        # 1  ==> 持有多仓
        # 0  ==> 无仓位
        # -1 ==> 持有空仓
    """
    print("-"*20 + " processing signals started" + "-"*20)
    signal_long = 1 * con_open_long
    signal_short = -1 * con_open_short
    signals = signal_long + signal_short

    # 开平仓信号
    for idx in range(1, len(signals)):
        # enter trade and not the time to close position
        # 上一个是开仓信号，当前没有平仓信号，继续持仓
        con_holding_long = (signals[idx - 1] >= 1) & (con_close_long[idx] != 1)
        con_holding_short = (signals[idx - 1] <= -1) & (con_close_short[idx] != 1)
        if con_holding_long | con_holding_short:
            # print(signals.index[idx], signals[idx-1], signals[idx])
            signals[idx] = signals[idx - 1]

        # 如果出现平仓信号且持有对应仓位, 平仓
        con_holding_close_long = (signals[idx - 1] >= 1) & (con_close_long[idx] == 1)
        con_holding_close_short = (signals[idx - 1] <= -1) & (con_close_short[idx] == 1)
        # 总平仓条件
        con_holding_close = con_holding_close_long | con_holding_close_short
        if con_holding_close:
            signals[idx] = 0

        # 止盈止损

        # 如果时间出现跳跃，平仓
        con_time_jump = (signals.index[idx] - signals.index[idx - 1]) > 10 * pd.Timedelta(freq)
        if con_time_jump:
            print(signals.index[idx])
            signals[idx - 1] = 0
            signals[idx] = 0

    print("-"*20 + " processing signals finished" + "-"*20)

    return signals


def processing_signal_withstop(con_open_long, con_open_short, con_close_long, con_close_short, freq, df_price,
                               set_stoploss=False, set_stopprofit=False, stop_loss=0.2, stop_profit=0.2,
                               reverse_trading=False):
    """
    获取开平仓信号
        # 信号 ==> [000001111100000-1-1-100000...]
        # 1  ==> 持有多仓
        # 0  ==> 无仓位
        # -1 ==> 持有空仓

    增加止盈，止损情况
    """

    # market position, 记录持仓情况
    mp = 0

    print("-" * 20 + " processing signals started" + "-" * 20)
    signal_long = 1 * con_open_long
    signal_short = -1 * con_open_short
    signals = signal_long + signal_short

    lst_mp = [0]
    open_price = 0
    # 开平仓信号
    for idx in range(1, len(signals)):
        if mp == 0:
            if signals[idx] != 0:
                mp = signals[idx]
                open_price = df_price[idx]
                # print(signals.index[idx], "open ---", mp)

            # 如果没有开仓条件, mp 不变

        else: # 持有仓位
            current_price = df_price[idx]
            current_profit = mp * (current_price/open_price - 1)

            # 止损平仓
            if set_stoploss:
                con_stop_loss = current_profit < - stop_loss
                if con_stop_loss:
                    mp = 0
                    # print(signals.index[idx], "stop loss")

            # 止盈平仓
            if set_stopprofit:
                con_stop_profit = current_profit > stop_profit
                if con_stop_profit:
                    mp = 0
                    # print(signals.index[idx], "stop profit]")

            # 平仓条件时平仓
            signal_close_long = con_close_long[idx]
            signal_close_short = con_close_short[idx]

            close_current_long = (mp > 0) and signal_close_long
            close_current_short = (mp < 0) and signal_close_short
            if close_current_long | close_current_short:
                # print(signals.index[idx], "close ---", mp)
                mp = 0
                # 考虑反向开仓
                if reverse_trading:
                    mp = signals[idx]
                    # print(signals.index[idx], "close and reverse open ---", mp)

        # 如果时间出现跳跃，平仓
        con_time_jump = (signals.index[idx] - signals.index[idx - 1]) > 10 * pd.Timedelta(freq)
        if con_time_jump:
            # print(signals.index[idx - 1], signals.index[idx], "时间间隔太长，跳过")
            # 时间间隔出现的上一个点平仓，且当前点不开仓
            lst_mp.pop()
            lst_mp.append(0)
            mp = 0

        # 记录当前持仓
        lst_mp.append(mp)

    print("-"*20 + " processing signals finished" + "-"*20)

    return pd.Series(lst_mp, index=signals.index)
