import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['STZhongsong']    # 指定默认字体：解决plot不能显示中文问题
mpl.rcParams['axes.unicode_minus'] = False           # 解决保存图像是负号'-'显示为方块的问题

from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Category20
from bokeh.layouts import column
from bokeh.models import BooleanFilter, CDSView, BoxAnnotation, Band, Span, Select, LinearAxis, DataRange1d, Range1d, ColumnDataSource
from bokeh.models.formatters import PrintfTickFormatter, NumeralTickFormatter


WIDTH_PLOT = 1200

RED = Category20[7][6]
GREEN = Category20[5][4]

BLUE = Category20[3][0]
BLUE_LIGHT = Category20[3][1]

ORANGE = Category20[3][2]
PURPLE = Category20[9][8]
BROWN = Category20[11][10]

TOOLS = 'pan,wheel_zoom,box_zoom,reset'


def performance_plot_MACD(file_name, df, signal_start, signal_end, signals, Dif, Dea, Result, portfolio_wealth):
    result_path = os.getcwd() + "/results"
    output_file(os.path.join(result_path,file_name), title=file_name)

    # 行情
    p0 = plot_market(df, signal_start, signal_end, signals)
    # 信号
    p1 = plot_macd(Dif, Dea, Result)
    p1.x_range = p0.x_range

    # 收益曲线
    p2 = plot_performance(portfolio_wealth)
    p2.x_range = p0.x_range

    show(column(p0, p1, p2))


def plot_performance(portfolio_wealth):
    # 收益曲线
    p2 = figure(plot_width=WIDTH_PLOT, plot_height=200, x_axis_type="datetime", tools=TOOLS)
    p2.line(portfolio_wealth.index, portfolio_wealth, color="#d62728", line_width=2, legend_label="资金曲线")
    p2.legend.location = "top_left"
    return p2


# def plot_market(df, signal_start, signal_end, signal_start_long, signal_end_long, signal_start_short, signal_end_short):
def plot_market(df, signal_start, signal_end, signals):
    # 行情
    p0 = figure(plot_width=WIDTH_PLOT, plot_height=400, x_axis_type="datetime", tools=TOOLS)
    # p0.line(df.index, df.open, color="darkgrey", legend_label="永续价格")
    # p0.legend.location = "top_left"

    inc = df.close > df.open
    dec = df.open> df.close

    # bar 的宽度，根据时间决定
    w = int((df.index[1] - df.index[0]).total_seconds() * 1000) * 0.5

    p0.segment(df.index, df.high, df.index, df.low, color="black")
    p0.vbar(df.index[inc], w, df.open[inc], df.close[inc], fill_color= RED, line_color="black")
    p0.vbar(df.index[dec], w, df.open[dec], df.close[dec], fill_color= GREEN, line_color="black")
    # p0.legend.location = "top_left"

    # # 开平仓点位 -- 做多
    # start_points_long = df["open"][signal_start_long]
    # end_points_long = df["open"][signal_end_long]
    #
    # # 开平仓点位 -- 做空
    # start_points_short = df["open"][signal_start_short]
    # end_points_short = df["open"][signal_end_short]
    #
    # xs_long = [[x,y] for (x,y) in zip(start_points_long.index, end_points_long.index)]
    # ys_long = [[x,y] for (x,y) in zip(start_points_long.values, end_points_long.values)]
    #
    # xs_short = [[x,y] for (x,y) in zip(start_points_short.index, end_points_short.index)]
    # ys_short = [[x,y] for (x,y) in zip(start_points_short.values, end_points_short.values)]
    #
    # # 红色点为开仓，蓝色点为平仓
    # p0.multi_line(xs_long,ys_long, color=RED, line_width=2)
    # p0.circle(start_points_long.index, start_points_long, color=RED, size=5)
    # p0.circle(end_points_long.index, end_points_long, color=GREEN, size=5)

    # 开平仓点位以及方向
    start_points = df["open"][signal_start]
    end_points = df["open"][signal_end]
    mp_start = signals[signal_start]

    # 判断是否盈利
    con_is_profit_long = ((end_points.values - start_points.values) > 0) & (mp_start.values > 0)
    con_is_profit_short = ((end_points.values - start_points.values) < 0) & (mp_start.values < 0)
    con_is_profit = con_is_profit_long | con_is_profit_short

    # 盈利的交易单
    start_points_in_profit = start_points[con_is_profit]
    end_points_in_profit = end_points[con_is_profit]
    # 亏损的交易单
    start_points_in_loss = start_points[~con_is_profit]
    end_points_in_loss = end_points[~con_is_profit]

    xs_in_profit = [[x,y] for (x,y) in zip(start_points_in_profit.index, end_points_in_profit.index)]
    ys_in_profit = [[x,y] for (x,y) in zip(start_points_in_profit.values, end_points_in_profit.values)]

    xs_in_loss = [[x,y] for (x,y) in zip(start_points_in_loss.index, end_points_in_loss.index)]
    ys_in_loss = [[x,y] for (x,y) in zip(start_points_in_loss.values, end_points_in_loss.values)]

    # 红色点为开仓，蓝色点为平仓
    p0.multi_line(xs_in_profit,ys_in_profit, color=RED, line_width=2, line_dash="dashed")
    p0.circle(start_points_in_profit.index, start_points_in_profit, color=RED, size=5)
    p0.circle(end_points_in_profit.index, end_points_in_profit, color=GREEN, size=5)

    # 红色点为开仓，蓝色点为平仓
    p0.multi_line(xs_in_loss,ys_in_loss, color=GREEN, line_width=2, line_dash="dashed")
    p0.circle(start_points_in_loss.index, start_points_in_loss, color=RED, size=5)
    p0.circle(end_points_in_loss.index, end_points_in_loss, color=GREEN, size=5)


    # xs = [[x,y] for (x,y) in zip(start_points.index, end_points.index)]
    # ys = [[x,y] for (x,y) in zip(start_points.values, end_points.values)]
    #
    # # 红色点为开仓，蓝色点为平仓
    # p0.multi_line(xs,ys, line_width=2)
    # p0.circle(start_points.index, start_points, color="red", size=5)
    # p0.circle(end_points.index, end_points, color="green", size=5)

    return p0

def plot_add_line():
    pass


def plot_volume(df, window=50):
    w = int((df.index[1] - df.index[0]).total_seconds() * 1000) * 0.5

    p = figure(x_axis_type="datetime", plot_width=WIDTH_PLOT, plot_height=200, title="Volume", tools=TOOLS)
    p.vbar(df.index, w, df.volume, [0] * df.shape[0])
    p.line(x=df.index, y=df.volume.rolling(window=window).mean(), line_width=2, color=ORANGE)

    return p


def plot_macd(Dif, Dea, Result):
    p = figure(x_axis_type="datetime", plot_width=WIDTH_PLOT, plot_height=200, title="MACD (line + histogram)", tools=TOOLS)

    up = Result[[True if val > 0 else False for val in Result]]
    down = Result[[True if val < 0 else False for val in Result]]

    w = int((Dif.index[1] - Dif.index[0]).total_seconds() * 1000) * 0.7
    p.vbar(x=up.index, top=up, bottom=np.zeros_like(up), width=w, color=GREEN)
    p.vbar(x=down.index, top=np.zeros_like(down), bottom=down, width=w, color=RED)

    p.extra_y_ranges = {'macd': DataRange1d()}
    p.add_layout(LinearAxis(y_range_name='macd'), 'right')

    p.line(Dif.index, Dif, line_width=2, color=BLUE, legend_label='MACD', muted_color=BLUE,
           muted_alpha=0, y_range_name='macd')
    p.line(Dif.index, Dea, line_width=2, color=BLUE_LIGHT, legend_label='Signal',
           muted_color=BLUE_LIGHT, muted_alpha=0, y_range_name='macd')

    p.legend.location = "top_left"
    return p


def plot_bollinger(p, dn_band, up_band):
    df = pd.concat([dn_band, up_band], axis=1)
    df = df.reset_index()
    df.columns = ["datetime", "dn_band", "up_band"]

    source = ColumnDataSource(df)
    band = Band(base="datetime", lower="dn_band", upper="up_band", source=source, level='underlay',
                fill_alpha=0.5, line_width=1, line_color='black', fill_color=BLUE_LIGHT)
    p.add_layout(band)

    return p

# def plot_rsi(df):
#
#     up =


def plot_adx(adx):
    p = figure(plot_width=WIDTH_PLOT, plot_height=200, x_axis_type="datetime", tools=TOOLS)
    p.line(adx.index, adx, color=BLUE, line_width=2, legend_label="资金曲线")

    low_box = BoxAnnotation(top=20, fill_alpha=0.1, fill_color=RED)
    p.add_layout(low_box)
    high_box = BoxAnnotation(bottom=70, fill_alpha=0.1, fill_color=GREEN)
    p.add_layout(high_box)

    # Horizontal line
    hline = Span(location=40, dimension='width', line_color='black', line_width=0.5)
    p.renderers.extend([hline])

    p.y_range = Range1d(0, 100)
    # p.yaxis.ticker = [20, 50]
    # p.yaxis.formatter = PrintfTickFormatter(format="%f%")
    p.grid.grid_line_alpha = 0.3

    return p


#
# def performance_plot(file_name, df, FastEMA, SlowEMA,
#                      Dif_standardized, Lines_Thr_DIF_up, Lines_Thr_DIF_dn,
#                      signal_start, signal_end, portfolio_wealth):
#     result_path = os.getcwd() + "/results"
#     output_file(os.path.join(result_path,file_name), title=file_name)
#
#     # 行情
#     p0 = figure(plot_width=1200, plot_height=400, x_axis_type="datetime")
#     p0.line(df.index, df.close, color="darkgrey", legend_label="永续价格")
#     p0.line(df.index, FastEMA, color="blue", legend_label="FastEMA")
#     p0.line(df.index, SlowEMA, color="yellow", legend_label="SlowEMA")
#
#     # 开平仓点位
#     start_points = df["close"][signal_start]
#     end_points = df["close"][signal_end]
#
#     xs = [[x,y] for (x,y) in zip(start_points.index, end_points.index)]
#     ys = [[x,y] for (x,y) in zip(start_points.values, end_points.values)]
#
#     p0.multi_line(xs,ys, line_width=2)
#     p0.circle(start_points.index, start_points, color="red", size=5)
#     p0.circle(end_points.index, end_points, color="green", size=5)
#
#     # 信号
#     p1 = figure(plot_width=1200, plot_height=200, x_axis_type="datetime", x_range=p0.x_range)
#     p1.line(df.index, Dif_standardized, color="#33A02C")
#     p1.line(df.index, Lines_Thr_DIF_up, color="#d62728")
#     p1.line(df.index, Lines_Thr_DIF_dn, color="#d62728")
#
#     p2 = figure(plot_width=1200, plot_height=200, x_axis_type="datetime", x_range=p0.x_range)
#     p2.line(df.index, portfolio_wealth, color= "#d62728")
#
#     show(column(p0,p1,p2))
#



# def f_plot(file_name,df,Dif,DEA,Lines_Thr_DIF_up,Lines_Thr_DIF_dn,
#            signal_start,signal_end):
#     result_path = os.getcwd() + "/results"
#     output_file(os.path.join(result_path,file_name), title=file_name)
#
#     inc = df.close > df.open
#     dec = df.open> df.close
#     w = 30*1000 # 0.5minutes in ms
#
#
#     p0 = figure(plot_width=1400, plot_height=400, x_axis_type="datetime")
#     p0.segment(
#         df.index, df.high, df.index, df.low,
#         color="black")
#     p0.vbar(df.index[inc], w, df.open[inc],df.close[inc],
#             fill_color="#D5E1DD", line_color="black")
#     p0.vbar(df.index[dec], w, df.open[dec],df.close[dec],
#             fill_color="#F2583E", line_color="black")
#
#     # 开仓点位
#     start_points = df["close"][signal_start]
#     end_points = df["close"][signal_end]
#
#     xs = [[x,y] for (x,y) in zip(start_points.index, end_points.index)]
#     ys = [[x,y] for (x,y) in zip(start_points.values, end_points.values)]
#
#     p0.multi_line(xs,ys, line_width=2)
#     p0.circle(start_points.index, start_points, color="red", size=5)
#     p0.circle(end_points.index, end_points, color="green", size=5)
#
#     p0.title.text = f"DEFI 永续价格"
#     p0.grid.grid_line_alpha = 0
#     p0.xaxis.axis_label = 'Date'
#     p0.yaxis.axis_label = 'Price'
#     p0.xaxis.visible = False
#
#     p1 = figure(plot_width=1400, plot_height=200, x_axis_type="datetime", x_range=p0.x_range)
#     p1.line(df.index, Dif.values, color= "#33A02C")
#     p1.line(df.index, DEA.values, color= "#FB9A99")
#     p1.line(df.index, Lines_Thr_DIF_up.values, color= "#d62728", line_width=0.5)
#     p1.line(df.index, Lines_Thr_DIF_dn.values, color= "#d62728", line_width=0.5)
#
#
#
#     p4 = figure(x_axis_type="datetime", tools="", toolbar_location=None, plot_width=1400, plot_height=200,
#                 x_range=p0.x_range)
#     p4.xaxis.major_label_orientation = np.pi / 4
#     p4.grid.grid_line_alpha = 0.3
#     p4.vbar(df.index,w, df["Volume"], [0]*df.shape[0])
#
#
#     show(column(p0,p1,p4))
#


def plot_fund_performance(df_base, df_wealth, st_time=pd.to_datetime("2021/01/01")):

    plt.figure(figsize=(16, 8), dpi=80)
    # plt.plot(df_base, color="grey", linestyle="--", linewidth=2)
    # plt.plot(df_base.loc[st_time:], color="blue", linestyle="-", linewidth=3)

    plt.plot(df_wealth, color="orange", linestyle="-", linewidth=2)
    # plt.plot(df_wealth.loc[st_time:], color="red", linestyle="-", linewidth=3)

    plt.gcf().autofmt_xdate()
    plt.grid(axis='both', alpha=.3)


