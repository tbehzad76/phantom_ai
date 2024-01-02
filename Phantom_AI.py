#!/usr/bin/env python3
import ccxt
import config
import asyncio
import os
from datetime import datetime
import pytz

os.makedirs("/tmp/tradingBot/", exist_ok=True)


def log(msg):
    tehran_tz = pytz.timezone("Asia/Tehran")
    datetime_in_tehran = datetime.now(tehran_tz)
    t = datetime_in_tehran.strftime("%Y/%m/%d %H:%M:%S")
    d = datetime_in_tehran.strftime("%Y-%m-%d")
    log_msg = str(msg)
    with open(f"/tmp/tradingBot/phantom_ai-{d}.log", 'a+') as file:
        file.write(f'{t}    {log_msg}' + "\n")


bingx = ccxt.bingx({
    'apiKey': config.BINGX_API_KEY,
    'secret': config.BINGX_SECRET_KEY,
})

trade_symbol = config.SYMBOL
leverage = config.LEVERAGE

bingx.set_leverage(leverage=leverage, symbol=trade_symbol, params={"marginMode": "cross", 'side': 'LONG'})
bingx.set_leverage(leverage=leverage, symbol=trade_symbol, params={"marginMode": "cross", 'side': 'SHORT'})


def get_market_price(symbol):
    ticker = bingx.fetch_ticker(symbol)
    market_price = ticker['ask']
    return market_price


def calc_amount():
    return config.FIRST_POSITION_AMOUNT


def fetch_balance():
    balances = bingx.fetch_balance()
    free_balance = balances['USDT']['free']
    if free_balance >= 5:
        return free_balance
    else:
        return 0


def take_profit(position, symbol, side, amount, position_amount):
    market_price = get_market_price(symbol)
    percentage = {
        'LONG': ((float(market_price) * 100 / float(position['info']['avgPrice'])) - 100) * leverage,
        'SHORT': ((float(position['info']['avgPrice']) * 100 / float(market_price)) - 100) * leverage
    }
    if side == 'LONG':
        if percentage['LONG'] >= config.TAKE_PROFIT:
            bingx.create_market_order(symbol=symbol, side='sell', amount=position_amount, params={'reduceOnly': True})
            open_order(symbol, amount, 'buy')
        return percentage['LONG']
    else:
        if percentage['SHORT'] >= config.TAKE_PROFIT:
            bingx.create_market_order(symbol=symbol, side='buy', amount=position_amount, params={'reduceOnly': True})
            open_order(symbol, amount, 'sell')
        return percentage['SHORT']


def open_order(symbol, amount, side):
    bingx.create_market_order(symbol=symbol, side=side, amount=amount)


def add_order(symbol, position, side):
    amount = (position['notional'] * 4) + calc_amount() - position['notional']
    market_price = get_market_price(symbol)
    percentage = {}
    if side == 'buy':
        percentage['LONG'] = ((float(market_price) * 100 / float(position['info']['avgPrice'])) - 100) * leverage
        if percentage['LONG'] <= -40:
            bingx.create_market_order(symbol=symbol, side=side, amount=amount)
    else:
        percentage['SHORT'] = ((float(position['info']['avgPrice']) * 100 / float(market_price)) - 100) * leverage
        if percentage['SHORT'] <= -40:
            bingx.create_market_order(symbol=symbol, side=side, amount=amount)


async def main():
    try:
        while True:
            amount = calc_amount()
            if amount != 0:
                positions = bingx.fetch_positions(symbols=[config.SYMBOL], params={})
                if positions:
                    for position in positions:
                        position_amount = position['notional']
                        if position['info']['positionSide'] == 'LONG':
                            tp = take_profit(position, trade_symbol, 'LONG', amount, position_amount)
                            add_order(trade_symbol, position, 'buy')
                            log(f'LONG:{tp}')
                        else:
                            tp = take_profit(position, trade_symbol, 'SHORT', amount, position_amount)
                            add_order(trade_symbol, position, 'sell')
                            log(f'SHORT:{tp}')
                else:
                    open_order(trade_symbol, amount, 'buy')
                    open_order(trade_symbol, amount, 'sell')
            else:
                log('Amount is zero')
                break
            await asyncio.sleep(1)
    except Exception as e:
        log(f'Error: {e}')


loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()
