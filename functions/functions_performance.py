
"""
Functions for performance calculations
Class object for performance calculations
"""

import numpy as np
import pandas as pd


def f_AnnualReturn(portfolio_wealth):
    """
    Calculate AnnualReturn
    :param portfolio_wealth: series of wealth
    :return:
    """
    n_days = (portfolio_wealth.index[-1] - portfolio_wealth.index[0]).days
    final_wealth = portfolio_wealth.iloc[-1]
    initial_wealth = portfolio_wealth.iloc[0]

    # 年化收益率
    annual_return = (final_wealth / initial_wealth - 1) / n_days * 365
    return annual_return


def f_SharpeRatio(portfolio_returns, portfolio_wealth, rf, n_transactions=1, k=365):
    """
    calculate sharpe ratio

    :param portfolio_returns:
    :param portfolio_wealth:
    :param rf: risk free rate
    :param n_transactions:
    :param k:
    :return:
    """

    if n_transactions > 0:  # 有交易
        annual_return = f_AnnualReturn(portfolio_wealth)
        anuual_standard_deviation = portfolio_returns.std(axis=0) * np.sqrt(k)
        sharpe_ratio = (annual_return - rf) / anuual_standard_deviation
    else:  # 无交易
        sharpe_ratio = 0
    return sharpe_ratio


def f_MaxDrawDown(portfolio_wealth):
    """
    Calculate Maximum drawdown
    :param portfolio_wealth:
    :return:
    """
    n = len(portfolio_wealth)
    rolling_max = portfolio_wealth.rolling(n, min_periods=1).max()
    drawdown = portfolio_wealth / rolling_max - 1
    max_drawdown = drawdown.min()
    return max_drawdown


def f_CalmarRatio(portfolio_wealth):
    """
    Calculate Calmar ratio
    Annual return / maximum drawdown
    :param portfolio_wealth:
    :return:
    """
    max_drawdown = f_MaxDrawDown(portfolio_wealth)

    # calmar ratio = 年化收益率 / Maximum drawdown
    if max_drawdown != 0:
        portfolio_Calmar = - f_AnnualReturn(portfolio_wealth) / max_drawdown
    else:
        portfolio_Calmar = 0

    return portfolio_Calmar


def f_ValueAtRisk(portfolio_returns, level=0.95):
    """
    Calculate Value at Risk in %
    :param portfolio_returns:
    :param level:
    :return:
    """
    value_at_risk = portfolio_returns[portfolio_returns != 0].quantile(level) * 100
    return value_at_risk


class portfolio:
    def __init__(self, signals, stock_prices, transaction_cost, initial_wealth,
                 deal_type="next_open", return_type="accumulation"):
        """

        :param signals:
            - pandas series of -1,0,1;
            - -1 means short position; 0 means no position; 1 means long position

        :param stock_prices:
            - stock_prices to calculate performance,
            - can be 5min moving average or simply current stock_prices series

        :param transaction_cost: eg. 0.02 * 0.06
        :param initial_wealth: float, how much money we have at T0
        :param deal_type:
        :param return_type:
        """

        self.stock_prices = stock_prices
        self.stock_returns = stock_prices.pct_change()
        self.transaction_cost = transaction_cost
        self.initial_wealth = initial_wealth
        self.transaction_cost = transaction_cost
        # bar interval
        self.freq = stock_prices.index[1] - stock_prices.index[0]

        if deal_type == "next_open":
            # generate signal at current close
            # trade at next open
            # so trade signal should be move forward by 1 timesteps
            # 交易信号往后挪一个
            self.signals = signals.shift(1, fill_value=0)
            # performance should be calculated as next next open/next_open - 1
            # so performance should be move forward by 2 timesteps
            # 收益信号往后挪两个
            self.signals_perf = signals.shift(2, fill_value=0)

        # 最后平仓
        # close position at last time
        self.signals.iloc[-1] = 0

        # 找到开仓和平仓点位
        # 开仓点位和关仓点位 -- 做多
        # signals when open long positions
        self.signal_start_long = (self.signals > 0) & (self.signals.shift(1) <= 0)
        # signals when close long positions
        self.signal_end_long = (self.signals <= 0) & (self.signals.shift(1) > 0)
        if self.signal_start_long.sum() - self.signal_end_long.sum() == 1:
            print("最后持有多仓，平掉")
            self.signal_end_long.iloc[-1] = True

        # 开仓点位和关仓点位 -- 做空
        # signals when open short positions
        self.signal_start_short = (self.signals < 0) & (self.signals.shift(1) >= 0)
        # signals when close short positions
        self.signal_end_short = (self.signals >= 0) & (self.signals.shift(1) < 0)
        if self.signal_start_short.sum() - self.signal_end_short.sum() == 1:
            print("最后持有空仓，平掉")
            self.signal_end_short.iloc[-1] = True

        # Combine signals when open
        self.signal_start = self.signal_start_long | self.signal_start_short
        # Combine signals when close
        self.signal_end = self.signal_end_long | self.signal_end_short

        # find price when we open the positions
        open_position_price = self.stock_prices[self.signal_start != 0]
        # find price when we close the positions
        close_position_price = self.stock_prices[self.signal_end != 0]

        # stock_return 出现缺失数据
        # compare the index the signals and stock_prices
        # there might be missing data
        index_signal = self.signals[self.signal_start].index
        index_price = open_position_price.index
        index_dif = index_signal.difference(index_price)
        if len(index_dif) > 0:
            print("缺失")

        # Calculate performance
        if return_type == "accumulation":
            # open position price should be at signal_start
            # portfolio returns from signal_start+1 to signal_end
            # 开仓成本，应该是 signal_start
            # 计算收益，从signal_start+1 到 signal_end

            # find all open positions price
            portfolio_open_position_price = pd.Series(data=np.nan, index=self.signals.index)
            for i in range(len(open_position_price)):
                # 找到开仓时间和平仓时间
                # find date when open position
                date_WhenOpen = open_position_price.index[i]
                # find date when close position
                date_WhenClose = close_position_price.index[i]
                # from open to close date, the open position price is always the same
                portfolio_open_position_price.loc[date_WhenOpen:date_WhenClose] = open_position_price.loc[date_WhenOpen]

            # calculate returns
            # there is no return when open position
            portfolio_returns = self.stock_prices.diff() / portfolio_open_position_price.shift(1) * self.signals_perf
            portfolio_returns[portfolio_returns.isna()] = 0
            # portfolio_returns[portfolio_returns == -1] = 0

            self.portfolio_open_position_price = portfolio_open_position_price

            # include transaction fees
            portfolio_returns = portfolio_returns - self.transaction_cost * (self.signal_start | self.signal_end)

            self.portfolio_returns = portfolio_returns
            self.portfolio_wealth = self.initial_wealth * (1 + self.portfolio_returns.cumsum())
            self.portfolio_wealth.iloc[0] = initial_wealth
            self.final_wealth = np.round(self.portfolio_wealth.iloc[-1], 2)

        elif return_type == "multiplication":

            # 持多仓 正常
            # 持空仓, 收益计算方式改变，不能用累乘
            # 应该正向累乘后，变为负的，再计算收益
            # 保证 多空收益平衡
            # 盈亏比率不一样，赚100% = 亏 50%

            portfolio_returns = self.stock_returns.copy() * self.signals_perf
            for i in range(len(open_position_price)):
                # 找到开仓时间和平仓时间
                # find date when open position
                date_WhenOpen = open_position_price.index[i]
                # find date when close position
                date_WhenClose = close_position_price.index[i]

                # 截取开仓到平仓的收益
                portfolio_rets_in_period = self.stock_returns.loc[date_WhenOpen:date_WhenClose]
                # 开仓不算收益
                portfolio_rets_in_period.iloc[0] = 0

                # 持空仓, 收益计算方式改变，不能用累乘
                # 应该正向累乘后，变为负的，再计算
                if self.signals_perf.loc[date_WhenClose] < 0:
                    # print(date_WhenOpen)
                    # 累乘积
                    portfolio_wealth_in_period = (1 + portfolio_rets_in_period).cumprod()
                    # 收益要反向
                    portfolio_wealth_in_period = 2 - portfolio_wealth_in_period
                    # 持仓期间内收益
                    portfolio_rets_in_period = portfolio_wealth_in_period.pct_change().dropna()
                    # calculate returns
                    portfolio_returns.loc[portfolio_rets_in_period.index] = portfolio_rets_in_period

            # include transaction fees
            portfolio_returns = portfolio_returns - self.transaction_cost * (self.signal_start | self.signal_end)

            # 记录
            self.portfolio_returns = portfolio_returns
            self.portfolio_wealth = self.initial_wealth * (1 + self.portfolio_returns).cumprod()
            self.portfolio_wealth.iloc[0] = initial_wealth
            self.final_wealth = np.round(self.portfolio_wealth.iloc[-1], 2)

        else:
            portfolio_returns = 0

        # 每笔交易盈亏
        self.open_position_price = open_position_price
        self.close_position_price = close_position_price

        # 每笔收益率
        self.profit = (close_position_price.values/open_position_price - 1) * self.signals[self.signal_start].values

        # 交易时长
        self.n_days = (stock_prices.index[-1] - stock_prices.index[0]).days
        self.n = len(stock_prices)
        # 交易总数
        self.n_transactions = self.signal_start.sum()

    def f_AnnualReturn(self):
        """
        AnnualReturn
        :return:
        """
        # 年化收益率
        annual_return = f_AnnualReturn(self.portfolio_wealth)
        return annual_return

    def f_SharpeRatio(self, rf, k=365):
        """
        calculate sharpe ratio
        :param rf: risk_free rate
        :param k:
        :return:
        """
        sharpe_ratio = f_SharpeRatio(self.portfolio_returns, self.portfolio_wealth, rf,
                                     n_transactions=self.n_transactions, k=k)
        return sharpe_ratio

    def f_MaxDrawDown(self):
        """
        calculate maximum drawdown
        :return:
        """
        max_drawdown = f_MaxDrawDown(self.portfolio_wealth)
        return max_drawdown

    def f_CalmarRatio(self):
        """
        Calculate Calmar ratio
        Annual return / maximum drawdown
        :return:
        """
        portfolio_Calmar = f_CalmarRatio(self.portfolio_wealth)
        return portfolio_Calmar

    def f_ValueAtRisk(self, level=0.95):
        """
        Calculate value at risk
        :param level:
        :return:
        """
        # 现在VAR %
        value_at_risk = f_ValueAtRisk(self.portfolio_returns, level=level)
        return value_at_risk

    def f_DailyTransactions(self):
        """
        Calculate average transations per day
        :return:
        """
        # 日均交易笔数
        daily_transactions = self.n_transactions / self.n_days
        return daily_transactions

    def f_LongRatio(self):
        """
        Calculate percentage of long open in total transactions
        :return:
        """
        signal_start_long = (self.signals == 1) & (self.signals.shift(1) <= 0)
        # 做多次数 / 总次数
        if self.n_transactions > 0:
            longshort_ratio = signal_start_long.sum() / self.n_transactions
            return longshort_ratio
        else:
            return None

    def f_AvgProfitPerTranscation(self):
        """
        Calculate average profit per transaction

        :return:
        """
        if self.n_transactions > 0: # 有交易
            avg_profit_per_transaction = self.profit.mean() * 100
        else:
            avg_profit_per_transaction = 0
        return avg_profit_per_transaction

    def f_WinningRatio(self):
        """
        Calculate percentage of winning
        :return:
        """
        winning_ratio = (self.profit > 0).mean()

        return winning_ratio

    def f_AvgHoldingTime(self):
        """
        Calculate average holding time (number of bars) of transactions
        :return:
        """
        if self.n_transactions > 0:
            total_holding_time_in_bars = self.signals[(self.signals != 0)].count() - self.n_transactions
            avg_holding_time_in_bars = total_holding_time_in_bars / self.n_transactions
            return avg_holding_time_in_bars
        else:
            return None
