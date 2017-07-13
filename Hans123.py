# -*- coding: utf-8 -*-

from gmsdk.api import StrategyBase
from gmsdk import md
from gmsdk.enums import *
import arrow
import time

# 每次开仓量
OPEN_VOL = 1

# 最大开仓次数
MAX_TRADING_TIMES = 10

class Hans123(StrategyBase):
    def __init__(self, *args, **kwargs):

        super(Hans123, self).__init__(*args, **kwargs)

    #          是否获得当天时间标示
        self.time_flag = False

    #     是否获取当天上、下轨数据
        self.data_flag = False

    # 持仓量
        self.long_holding = 0
        self.short_holding = 0

    #     当天交易次数
        self.trading_times = 0

        self.__get_param()


    def __get_param(self):
        """
        获取配置参数
        """
        #     交易证券代码
        self.trade_symbol = self.config.get('para','trade_symbol')
        pos = self.trade_symbol.find('.')
        self.exchange = self.trade_symbol[:pos]
        self.sec_id = self.trade_symbol[pos + 1:]

        print 'exchange: %s' %self.exchange
        print 'sec_id: %s' %self.sec_id

        #     开盘时间
        self.open_time = self.config.get('para', 'open_time')
        print 'open_time: %s' %self.open_time

        #     hans时间
        self.hans_time = self.config.get('para', 'hans_time')
        print 'hans_time: %s' %self.hans_time

        #     强制平仓时间
        self.ex_time = self.config.get('para', 'ex_time')
        print 'ex_time: %s' %self.ex_time

    def __get_time(self, cur_utc):
        """
        获取当天的重要时间参数
        """
        utc = arrow.get(cur_utc).replace(tzinfo='local')
        cur_date = utc.format('YYYY-MM-DD')
        FMT = '%s %s'
        self.today_open_time = FMT %(cur_date, self.open_time)
        print  'today open time: %s' %self.today_open_time

        self.today_hans_time = FMT %(cur_date, self.hans_time)
        print 'today hans time: %s' %self.today_hans_time

        today_ex_time = FMT %(cur_date, self.ex_time)
        print 'today exit time: %s' %today_ex_time

        self.ex_time_utc = arrow.get(today_ex_time).replace(tzinfo='local').timestamp
        self.hans_time_utc = arrow.get(self.today_hans_time).replace(tzinfo='local').timestamp

    def __init_band_data(self, bar_type):
        """
        获取上下轨数据
        """
        # 获取开盘后hans时间的数据
        bars = self.get_bars(self.trade_symbol, bar_type, self.today_open_time, self.today_hans_time)
        close_list = [bar.close for bar in bars]

        #     上轨
        self.upr_band = max(close_list)
        print "upper band: %f" %self.upr_band

        #     下轨
        self.dwn_band = min(close_list)
        print "down band: %f" %self.dwn_band

    def on_tick(self, tick):
    #     获取最新价
        print "on tick"
        self.last_price = tick.last_price


    def on_bar(self, bar):

        print "on bar @ %s" % bar.strtime
        print "trading times: %d" %self.trading_times
        print "time_flag: ", self.time_flag
        print "data_flag: ", self.data_flag

        self.last_price = bar.close

            #     获取当天的时间参数
        if self.time_flag == False:
            self.__get_time(bar.utc_time)
            self.time_flag = True

                #     计算上下轨
        if bar.utc_time < self.ex_time_utc and bar.utc_time > self.hans_time_utc:
            if self.time_flag == True and self.data_flag == False:
                self.__init_band_data(bar.bar_type)
                self.data_flag = True

    # 休市前强平当天仓位
        if bar.utc_time > self.ex_time_utc:
            if self.long_holding > 0:
        #             持有多仓,市价单平仓
                self.close_long(self.exchange, self.sec_id, 0, self.long_holding)
                print 'exit time close long: %s, vol: %f' %(self.trade_symbol, self.long_holding)
                self.long_holding = 0


            elif self.short_holding >0:
                # 持有空仓，市价单平仓
                self.close_short(self.exchange, self.sec_id, 0, self.short_holding)
                print 'exit time close short: %s, vol: %f' % (self.trade_symbol, self.short_holding)
                self.short_holding = 0

            self.trading_times = 0
            self.data_flag = False
            self.time_flag = False
            return



    #     检查当天交易次数
        if self.trading_times > MAX_TRADING_TIMES:
            print 'trading times more than max trading times, stop trading'

            return

    #     交易时段处理
        if bar.utc_time > self.hans_time_utc and bar.utc_time < self.ex_time_utc:
            if bar.close > self.upr_band:
                if self.short_holding > 0:
                    #                 有空仓，先平空
                    self.close_short(self.exchange, self.sec_id, 0, self.short_holding)
                    print 'close short: %s, vol: %f' % (self.trade_symbol, self.short_holding)
                    self.short_holding = 0
    #             开多,市价
                self.open_long(self.exchange, self.sec_id, self.last_price, OPEN_VOL)
                print 'open long: %s, vol: %f' %(self.trade_symbol, OPEN_VOL)
                self.long_holding += OPEN_VOL
    #             开仓次数+1
                self.trading_times += 1

            elif bar.close < self.dwn_band:
                if self.long_holding > 0:
    #                 有多仓，先平多仓
                    self.close_long(self.exchange, self.sec_id, 0 , self.long_holding)
                    print 'close long: %s, vol: %f' %(self.trade_symbol, self.long_holding)
                    self.long_holding = 0

    #             开空，市价
                self.open_short(self.exchange, self.sec_id, self.last_price , OPEN_VOL)
                print 'open short: %s, vol: %f' %(self.trade_symbol, OPEN_VOL)
                self.short_holding += OPEN_VOL
                #             开仓次数+1
                self.trading_times += 1

    def on_order_filled(self, res):
        pass

    def on_order_partiall_filled(self, res):
        pass

    def on_order_canceled(self, res):
        pass


if __name__ == '__main__':

    hans123 = Hans123(config_file='Hans123.ini')
    ret = hans123.run()
    print hans123.get_strerror(ret)

    # myStrategy = Hans123(
    #     username='yesheng1984@139.com',
    #     password='jj1234',
    #     strategy_id='3643e7fa-66d8-11e7-a981-bcee7b96f2dc',
    #     subscribe_symbols='CFFEX.IF1601.tick,CFFEX.IF1601.bar.60',
    #     mode=4,
    #     td_addr='127.0.0.1:8001'
    # )
    # myStrategy.backtest_config(
    #     start_time='2015-12-15 09:15:00',
    #     end_time='2015-12-15 15:15:00',
    #     initial_cash=1000000,
    #     transaction_ratio=1,
    #     commission_ratio=0,
    #     slippage_ratio=0,
    #     price_type=0)
    # ret = myStrategy.run()
    # print('exit code: ', ret)