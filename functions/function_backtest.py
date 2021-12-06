from functions.functions_indicator import *
from functions.functions_processing_data import *
from functions.functions_performance import *
from functions.functions_trend_factors import *

import talib as ta


def f_ema_bt(df, FastMALen, SlowMALen):
    index_performance = "ema, " +  str(FastMALen) + ", " + str(SlowMALen)

    fast_ma = ta.EMA(df.close, FastMALen)
    slow_ma = ta.EMA(df.close, SlowMALen)

    con_open_long, con_open_short, con_close_long, con_close_short = f_factor_ma_v0_0(fast_ma, slow_ma)

    return index_performance, con_open_long, con_open_short, con_close_long, con_close_short


def f_ma_bt(df, FastMALen, SlowMALen):
    index_performance = "ma, " + str(FastMALen) + ", " + str(SlowMALen)

    fast_ma = ta.MA(df.close, FastMALen)
    slow_ma = ta.MA(df.close, SlowMALen)

    con_open_long, con_open_short, con_close_long, con_close_short = f_factor_ma_v0_0(fast_ma, slow_ma)

    return index_performance, con_open_long, con_open_short, con_close_long, con_close_short


def f_ama_bt(df, FastMALen, SlowMALen):
    index_performance = "ama, " + str(FastMALen) + ", " + str(SlowMALen)

    fast_ma = ta.KAMA(df.close, FastMALen)
    slow_ma = ta.KAMA(df.close, SlowMALen)

    con_open_long, con_open_short, con_close_long, con_close_short = f_factor_ma_v0_0(fast_ma, slow_ma)

    return index_performance, con_open_long, con_open_short, con_close_long, con_close_short


def f_backtest(df, df_5min_avg_price_open, freq, transaction_cost, index_performance,
               con_open_long, con_open_short, con_close_long, con_close_short,
               get_returns=False):
    # 信号处理
    signals = processing_signal_withstop(con_open_long, con_open_short, con_close_long, con_close_short, freq, df.close,
                                         set_stoploss=False, set_stopprofit=False, stop_loss=0.5, stop_profit=1,
                                         reverse_trading=True)

    portf = portfolio(signals, df_5min_avg_price_open, transaction_cost, 1,
                      deal_type="next_open", return_type="accumulation")

    if get_returns:
        return portf.portfolio_returns
    else:
        df_performance = pd.DataFrame()
        df_performance.loc[index_performance, "年化收益"] = portf.f_AnnualReturn()
        df_performance.loc[index_performance, "夏普比率"] = portf.f_SharpeRatio(rf=0.04, k=365)
        df_performance.loc[index_performance, "卡玛比率"] = portf.f_CalmarRatio()
        df_performance.loc[index_performance, "最大回撤"] = portf.f_MaxDrawDown()
        df_performance.loc[index_performance, "总手数"] = portf.n_transactions
        df_performance.loc[index_performance, "多空比"] = portf.f_LongRatio()
        df_performance.loc[index_performance, "平均持仓时间"] = portf.f_AvgHoldingTime()
        df_performance.loc[index_performance, "单笔净利%"] = portf.f_AvgProfitPerTranscation()
        df_performance.loc[index_performance, "胜率"] = portf.f_WinningRatio()

        df_performance = df_performance.round(2)

        return df_performance


