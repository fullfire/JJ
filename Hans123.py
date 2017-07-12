# -*- coding: utf-8 -*-

from gmsdk.api import StrategyBase

class Mystrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(Mystrategy, self).__init__(*args, **kwargs)


    def on_tick(self, tick):
        pass

    def on_bar(self, bar):
        pass

    def on_order_filled(self, res):
        pass

    def on_order_partiall_filled(self, res):
        pass

    def on_order_canceled(self, res):
        pass


if __name__ == '__main__':
    myStrategy = Mystrategy(
        username='yesheng1984@139.com',
        password='jj1234',
        strategy_id='3643e7fa-66d8-11e7-a981-bcee7b96f2dc',
        subscribe_symbols='CFFEX.IF1601.tick,CFFEX.IF1601.bar.60',
        mode=4,
        td_addr='127.0.0.1:8001'
    )
    myStrategy.backtest_config(
        start_time='2015-12-15 09:15:00',
        end_time='2015-12-15 15:15:00',
        initial_cash=1000000,
        transaction_ratio=1,
        commission_ratio=0,
        slippage_ratio=0,
        price_type=0)
    ret = myStrategy.run()
    print('exit code: ', ret)