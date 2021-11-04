"""
CUSTOM_LIST: False
TIME_DIFFERENCE: 1
RECHECK_INTERVAL: 4
CHANGE_IN_PRICE: 100
STOP_LOSS: 100
TAKE_PROFIT: 1.5
USE_TRAILING_STOP_LOSS: True
TRAILING_STOP_LOSS: .5
TRAILING_TAKE_PROFIT: .1
SIGNALLING_MODULES:
- os_signals_buy_3st
"""
from binance.client import Client
import numpy as np
import threading
import os
import pandas_ta as pta
import pandas as pd
from datetime import date, datetime, timedelta
import time

client = Client("", "")
TIME_TO_WAIT = 3  # Minutes to wait between analysis
DEBUG = False  # List analysis result to console
TICKERS = 'TICKERLISTS/tickers_all.txt'  # 'signalsample.txt'
SIGNAL_NAME = 'os_signalbuys_3st'
SIGNAL_FILE_BUY = 'signals/' + SIGNAL_NAME + '.buy'


# for colourful logging to the console
class txcolors:
    BUY = '\033[92m'
    WARNING = '\033[93m'
    SELL_LOSS = '\033[91m'
    SELL_PROFIT = '\033[32m'
    DIM = '\033[2m\033[35m'
    DEFAULT = '\033[39m'


def get_symbols():
    response = client.get_ticker()
    PAIRS_WITH = 'USDT'
    ignore = ['UP', 'DOWN', 'AGLD', 'AUD', 'BRL', 'BVND', 'BCC', 'CVP', 'BCHABC', 'BCHSV', 'BEAR', 'BNBBEAR', 'BNBBULL',
              'BULL', 'BKRW', 'DAI', 'ERD', 'EUR', 'FRONT', 'USDS', 'HC', 'LEND', 'MCO', 'GBP', 'RUB',
              'TRY', 'NPXS', 'PAX', 'STORM', 'VEN', 'UAH', 'NGN', 'VAI', 'STRAT','SUSD', 'XZC', 'RAD']
    symbols = []

    for symbol in response:
        if PAIRS_WITH in symbol['symbol'] and all(item not in symbol['symbol'] for item in ignore):
            if symbol['symbol'][-len(PAIRS_WITH):] == PAIRS_WITH:
                symbols.append(symbol['symbol'])
            symbols.sort()
    return symbols


trading_pairs = []
selected_pair = []
selected_pairCMO = []


def tripple_st(filtered_pairs3):
    interval = '15m'
    symbol = filtered_pairs3
    start_str = '7 days ago UTC'
    end_str = f'{datetime.now()}'
    # print(f"Fetching new bars for {datetime.now().isoformat()}")
    df = pd.DataFrame(client.get_historical_klines(symbol, interval, start_str, end_str)[:-1]).astype(float)
    df = df.iloc[:, :6]
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    df = df.set_index('timestamp')
    df.index = pd.to_datetime(df.index, unit='ms')

    # print("on 15m timeframe " + symbol)

    sup1 = pta.supertrend(df.high, df.low, df.close, 10, 1.0)['SUPERT_10_1.0']
    sup2 = pta.supertrend(df.high, df.low, df.close, 11, 2.0)['SUPERT_11_2.0']
    sup3 = pta.supertrend(df.high, df.low, df.close, 12, 3.0)['SUPERT_12_3.0']
    ema = pta.ema(df.close, 550)
    stoch_rsi_k = pta.stochrsi(df.close)['STOCHRSIk_14_14_3_3']
    stoch_rsi_d = pta.stochrsi(df.close)['STOCHRSId_14_14_3_3']

    if ema is None or sup1 is None or sup2 is None or sup3 is None or stoch_rsi_k is None or stoch_rsi_d is None:
        print(f"Not enough data to calculate ema for {symbol}.")
        return selected_pair

    if ema.iat[-1] < df.close.iat[-1] and 20 > stoch_rsi_k.iat[-1] > stoch_rsi_d.iat[-1] \
            and ((sup1.iat[-1] < df.close.iat[-1] and sup2.iat[-1] < df.close.iat[-1])
                 or (sup1.iat[-1] < df.close.iat[-1] and sup3.iat[-1] < df.close.iat[-1])
                 or (sup2.iat[-1] < df.close.iat[-1] and sup3.iat[-1] < df.close.iat[-1])):
        print(f'{symbol}'
              f' EMA 550:{ema.iat[-1]}'
              f', ST 1: {sup1.iat[-1]}'
              f', ST 2: {sup2.iat[-1]}'
              f', ST 3: {sup3.iat[-1]}'
              f', stochrsi_k:{stoch_rsi_k.iat[-1]}'
              f' | CLOSE: {df.close.iat[-1]}')
        selected_pair.append(symbol)

        with open(SIGNAL_FILE_BUY, 'a+') as f:
            f.writelines(symbol + '\n')

    # else:
    #     print('searching')
    return selected_pair


def analyze(trading_pairs):
    signal_coins = {}
    selected_pair.clear()
    if os.path.exists(SIGNAL_FILE_BUY):
        os.remove(SIGNAL_FILE_BUY)
    for i in trading_pairs:
        output = tripple_st(i)

    for pair in selected_pair:
        signal_coins[pair] = pair
        # with open(SIGNAL_FILE_BUY, 'a+') as f:
        #     f.writelines(pair + '\n')

    if selected_pair:
        print(f'{txcolors.BUY}{SIGNAL_NAME}: {selected_pair} - Buy Signal Detected{txcolors.DEFAULT}')
    else:
        print(f'{txcolors.DEFAULT}{SIGNAL_NAME}: - not enough signal to buy')
    return signal_coins


def do_work():
    while True:
        try:
            if not os.path.exists(TICKERS):
                time.sleep((TIME_TO_WAIT * 60))
                continue

            signal_coins = {}
            pairs = {}
            # uncomment line 130,131 if you want use some .txt list from TICKERS
            # with open(TICKERS) as f:
            #     pairs = f.read()

            pairs = get_symbols()

            if not threading.main_thread().is_alive(): exit()
            print(f'{SIGNAL_NAME}: Analyzing {len(pairs)} coins')
            signal_coins = analyze(pairs)
            print(
                f'{SIGNAL_NAME}: {len(signal_coins)} coins with Buy Signals. Waiting {TIME_TO_WAIT} minutes for next analysis.')

            time.sleep((TIME_TO_WAIT * 60))
        except Exception as e:
            print(f'{SIGNAL_NAME}: Exception do_work() 1: {e}')
            continue
        except KeyboardInterrupt as ki:
            continue
