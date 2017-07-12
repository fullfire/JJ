#coding=utf-8
# author: Y.Raul
# date : 2017/7/12
# 系统包导入
import pandas as pd
import numpy as np

# 绘图包导入
import matplotlib.pyplot as plt
import seaborn as sns

#分析包导入
import talib as ta

#数据包导入
import tushare as ts

from gmsdk.api import StrategyBase

class MyStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(MyStrategy, self).__init__(*args, **kwargs)

    def on_tick(self, tick):
        self.open_long(tick.exchange, tick.sec_id, tick.last_price, 100)
        print("OpenLong: exchange %s, sec_id %s, price %s" %
                (tick.exchange, tick.sec_id, tick.last_price))

if __name__ == '__main__':
    ret = MyStrategy(
        username='yesheng1984@139.com',
        password='jj1234',
        strategy_id='strategy_2',
        subscribe_symbols='SHSE.600000.tick',
        mode=2
    ).run()
    print(('exit code: ', ret))