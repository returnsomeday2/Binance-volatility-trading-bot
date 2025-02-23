from tradingview_ta import TA_Handler, Interval, Exchange
import os
import time
import threading

SIGNAL_NAME = 'os_pausebot_MAOSC'
SIGNAL_FILE = 'signals/pausebot.pause'

INTERVAL = Interval.INTERVAL_5_MINUTES #Timeframe for analysis
TIME_TO_WAIT = 5

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SYMBOLS = ['BTCUSDT', 'ETHUSDT']

DEBUG = True

def analyze():

    analysis = {}
    handler = {}
    ma_analysis_sell = {}
    ma_analysis_buy = {}
    ma_analysis_neutral = {}
    osc_analysis_sell = {}
    osc_analysis_buy = {}
    osc_analysis_neutral = {}

    paused = 0
    retPaused = False

    for symbol in SYMBOLS:
        handler[symbol] = TA_Handler(
            symbol=symbol,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout= 10)

    for symbol in SYMBOLS:
        try:
            analysis = handler[symbol].get_analysis()

        except Exception as e:
            print(f'{SIGNAL_NAME}:')
            print(f'Handler {handler[symbol]} Exception:')
            print(e)
            return

        ma_analysis_sell[symbol] = analysis.moving_averages['SELL']
        ma_analysis_buy[symbol] = analysis.moving_averages['BUY']
        ma_analysis_neutral[symbol] = analysis.moving_averages['NEUTRAL']

        osc_analysis_sell[symbol] = analysis.oscillators['SELL']
        osc_analysis_buy[symbol] = analysis.oscillators['BUY']
        osc_analysis_neutral[symbol] = analysis.oscillators['NEUTRAL']

        # Does MA say to sell?     
        if ma_analysis_sell[symbol] >= ma_analysis_buy[symbol]:       
            paused = paused + 1

        # Does OSC say to sell?     
        if osc_analysis_sell[symbol] >= osc_analysis_buy[symbol]:       
            paused = paused + 1

        if DEBUG:
            print(f'{SIGNAL_NAME}: {symbol} - MA SELL indicators: {ma_analysis_sell[symbol]} | MA BUY indicators: {ma_analysis_buy[symbol]} |  MA NEUTRAL indicators: {ma_analysis_neutral[symbol]}.')
            print(f'{SIGNAL_NAME}: {symbol} - OSC SELL indicators: {osc_analysis_sell[symbol]} | OSC BUY indicators: {osc_analysis_buy[symbol]} |  OSC NEUTRAL indicators: {osc_analysis_neutral[symbol]}.')


    # at least one of the Symbols have value pause
    if paused > 0:
        print(f'{SIGNAL_NAME}: Market not looking too good, bot paused from buying. Waiting {TIME_TO_WAIT} minutes for next market checkup.')
        retPaused = True
    else:
        print(f'{SIGNAL_NAME}: Market looks ok, bot is running. Waiting {TIME_TO_WAIT} minutes for next market checkup.')
        retPaused = False
    
    return retPaused

def do_work():

    while True:
        try:
            if not threading.main_thread().is_alive(): exit()
            # print(f'pausebotmod: Fetching market state')
            paused = analyze()
            if paused:
                with open(SIGNAL_FILE,'a+') as f:
                    f.write('yes')
            else:
                if os.path.isfile(SIGNAL_FILE):
                    os.remove(SIGNAL_FILE)

            # print(f'pausebotmod: Waiting {TIME_TO_WAIT} minutes for next market checkup')
            time.sleep((TIME_TO_WAIT*60))
        except Exception as e:
            print(f'{SIGNAL_NAME}: Exception do_work() 1: {e}')
            continue
        except KeyboardInterrupt as ki:
            continue
