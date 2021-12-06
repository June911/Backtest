"""
画图函数
"""

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# from pylab import mpl
# mpl.rcParams['font.sans-serif'] = ['SimHei']    # 指定默认字体：解决plot不能显示中文问题
# mpl.rcParams['axes.unicode_minus'] = False           # 解决保存图像是负号'-'显示为方块的问题

def plot_correlation_matrix(df):

    mask = np.zeros_like(df.corr(), dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    plt.figure(figsize=(15, 10))
    sns.heatmap(df.corr()*100, mask=mask, annot=True)


def plot_heatmap(df):
    # plt.figure(figsize=(15, 10))
    sns.heatmap(df)
    # sns.heatmap(df, annot=True)
    # plt.title(title)




# fig, axs = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
# axs[0].plot(df.open)
# axs[1].plot(portf.portfolio_wealth)
# plt.gcf().autofmt_xdate()
# plt.savefig(f"{file_name}.png")

