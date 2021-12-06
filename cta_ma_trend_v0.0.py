"""
DEFI CTA 策略 --- 趋势跟踪
current close signal, next open enter/out

策略逻辑：
中长期趋势跟踪


开仓条件
- 开多：DIF上穿DEA
- 开空：DIF下穿DEA

平仓条件
- 平多：DIF下穿DEA 或者
- 平空：DIF上穿DEA


"""

############################## 包读取  ######################################
from functions.functions_indicator import *
from functions.functions_processing_data import *
from functions.functions_performance import *
from functions.functions_plot_bokeh import *
from functions.functions_trend_factors import *

import matplotlib.pyplot as plt

############################## 模型输入 #####################################

"""
指标输入
"""
# EMA
FastMALen = 40
SlowMALen = 60
# FastMALen = 20
# SlowMALen = 100

"""
其他参数
"""
# 手续费
transaction_cost = 2 * 0.06 * 0.01

# contract name
contract = "BNBUSDT"
# start years
st_year = 2021

# K线周期
freq = "15T"
freq_perf = "1T"

# 文件名
file_name = contract + "_" + "cta_ma_0_1_" + str(FastMALen) + "_" + str(SlowMALen) + "_" + freq

# 数据文件
file_data_name = "binance_futures_BNBUSDT_202171_20211126.csv"

############################## 数据调整 #####################################

# 获取数据
df = get_data(file_data_name, from_database=False)
df.dropna(inplace=True)

# 转换K线
df_perf = f_change_barperiod(df, freq_perf)
df = f_change_barperiod(df, freq)

# 以开仓点5分钟open的平均价格为入场和出场价格
df_perf_avg_price_open = df_perf["avg_price"]
df_perf_avg_price_open = df_perf_avg_price_open.loc[df_perf_avg_price_open.index.intersection(df.index)]

############################## 指标计算 #####################################

# calculate
fast_ma = f_ma(df.close, FastMALen)
slow_ma = f_ma(df.close, SlowMALen)
cross_ma = fast_ma - slow_ma

# directly get MA from package talib
# import talib as ta
# fast_ma = ta.MA(df.close, FastMALen)
# slow_ma = ta.MA(df.close, SlowMALen)

############################## 开平条件 #####################################

con_open_long, con_open_short, con_close_long, con_close_short = f_factor_ma_v0_0(fast_ma, slow_ma)
# con_open_long.mean()
# con_open_short.mean()
# con_close_long.mean()
# con_close_short.mean()

############################## 绩效指标 #####################################

"""
获取开平仓信号
    # 信号 ==> [000001111100000-1-1-100000...]
    # 1  ==> 持有多仓
    # 0  ==> 无仓位
    # -1 ==> 持有空仓
"""

# 信号处理
signals = processing_signal_withstop(con_open_long, con_open_short, con_close_long, con_close_short, freq, df.close,
                                     set_stoploss=False, set_stopprofit=False, stop_loss=0.5, stop_profit=1,
                                     reverse_trading=True)

# signals = signals[((signals > 0) & (signals.shift(1) <= 0)) | ((signals < 0) & (signals.shift(1) >= 0))]


# 获取收益和其他绩效
# current close 触发信号， next open 成交
# portf = portfolio(signals, df.open, transaction_cost, 1, deal_type="next_open", return_type="multiplication")
portf = portfolio(signals, df.open, transaction_cost, 1, deal_type="next_open", return_type="accumulation")
# portf = portfolio(signals, df_perf_avg_price_open, transaction_cost, 1, deal_type="next_open", return_type= "accumulation")

df_performance = pd.DataFrame(index=[file_name])
df_performance["年化收益"] = portf.f_AnnualReturn()
df_performance["夏普比率"] = portf.f_SharpeRatio(rf=0.04, k=365)
df_performance["最大回撤"] = portf.f_MaxDrawDown()
df_performance["总手数"] = portf.n_transactions
df_performance["多空比"] = portf.f_LongRatio()
df_performance["平均持仓时间"] = portf.f_AvgHoldingTime()
df_performance["单笔净利"] = portf.f_AvgProfitPerTranscation()
df_performance["胜率"] = portf.f_WinningRatio()

df_performance = df_performance.round(2)

print("-" * 80)
print("年化收益, ", df_performance["年化收益"].values[0])
print("夏普比率, ", df_performance["夏普比率"].values[0])
print("最大回撤, ", df_performance["最大回撤"].values[0])
print("总手数, ", df_performance["总手数"].values[0])
print("多空比, ", df_performance["多空比"].values[0])
print("平均持仓时间, ", df_performance["平均持仓时间"].values[0])
print("单笔净利, ", df_performance["单笔净利"].values[0])
print("胜率, ", df_performance["胜率"].values[0])
print("-" * 80)

############################## 画图    #####################################

# set results_path to save the results
# if not exist, create one
if not os.path.isdir("results"):
    os.mkdir("results")

result_path = os.path.join(os.getcwd(), "results")
output_file(os.path.join(result_path, f"{file_name}.html"), title=file_name)

# 行情
p0 = plot_market(df, portf.signal_start, portf.signal_end, portf.signals)
p0.line(x=df.index, y=fast_ma, line_width=2, color=BLUE)
p0.line(x=df.index, y=slow_ma, line_width=2, color=ORANGE)

# 收益曲线
p3 = plot_performance(portf.portfolio_wealth)
p3.x_range = p0.x_range

show(column(p0, p3))
