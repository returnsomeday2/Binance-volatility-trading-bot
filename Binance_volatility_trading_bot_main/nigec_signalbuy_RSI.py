# Available indicators here: https://python-tradingview-ta.readthedocs.io/en/latest/usage.html#retrieving-the-analysis

# NigeC v1.01 - June 9 2021 - Credit to @DJcommie and @Firewatch for the inspiration and initial code
# No future support offered, use this script at own risk - test before using real funds
# If you lose money using this MOD (and you will at some point) you've only got yourself to blame!
# FILENAME: rsi-mod.py

from tradingview_ta import TA_Handler, Interval, Exchange
# use for environment variables
import os
# use if needed to pass args to external modules
import sys
# used for directory handling
import glob
import time
import threading

# used for dates
from datetime import date, datetime, timedelta
import time

# my helper utils
from helpers.os_utils import(rchop)

########################################################
# These are the TradingView Oscillator signals available
########################################################

#{'Recommend.Other': 0.09090909, 'Recommend.All': 0.17878788, 'Recommend.MA': 0.26666667, 'RSI': 51.35657473, 'RSI[1]': 56.0809039, 'Stoch.K': 40.83410422, 'Stoch.D': 36.71946441, 'Stoch.K[1]': 31.67255276, 'Stoch.D[1]': 39.57313164, 'CCI20': -52.17234223, 'CCI20[1]': 4.5072255, 'ADX': 35.60476973, 'ADX+DI': 28.49583595, 'ADX-DI': 25.60684839, 'ADX+DI[1]': 29.85479333, 'ADX-DI[1]': 26.11840839, 'AO': 8.26394676, 'AO[1]': 12.62397794, 'Mom': -15.22, 'Mom[1]': -2.67, 'MACD.macd': 7.00976885, 'MACD.signal': 10.30480624, 'Rec.Stoch.RSI': 0, 'Stoch.RSI.K': 9.72185595, 'Rec.WR': 0, 'W.R': -62.00277521, 'Rec.BBPower': 1, 'BBPower': -6.09964786, 'Rec.UO': 0, 'UO': 50.27359668}

#############################################################
# Settings - edit below to change analysis buy & sell signals
# Default settings in brackets at end of comments
#############################################################

INTERVAL = Interval.INTERVAL_1_DAY # Main Timeframe for analysis on Oscillators and Moving Averages (15 mins)
INTERVAL2 = Interval.INTERVAL_1_MINUTE # Secondary Timeframe for analysis on BUY signals for next lowest timescale | Check Entry Point (5)

OSC_INDICATORS = ['RSI', 'STOCH.K', 'CCI', 'ADX', 'AO', 'W%R', 'Stoch.RSI', 'Mom', 'MACD', 'UO', 'BBP'] # Indicators to use in Oscillator analysis
OSC_THRESHOLD = 0 # Must be less or equal to number of items in OSC_INDICATORS (5)
MA_INDICATORS = ['EMA10', 'EMA20', 'SMA10', 'SMA20', 'EMA30', 'SMA30', 'EMA50', 'SMA50', 'EMA100', 'SMA100',
                 'EMA200', 'SMA200', 'Ichimoku', 'VWMA', 'HullMA'] # Indicators to use in Moving Averages analysis
MA_THRESHOLD = 0 # Must be less or equal to number of items in MA_INDICATORS (3)
MA_SUMMARY = 0 # Buy indicators out of 26 to use in Moving Averages INTERVAL analysis (13)
MA_SUMMARY2 = 0 # Buy indicators out of 26 to use in Moving Averages INTERVAL2 analysis (13)
OSC_SUMMARY = 0 # Sell indicators out of 11 to use in Oscillators analysis (2)

RSI_MIN = 1 # Min RSI Level for Buy Signal - Under 25 considered oversold (12)
RSI_MAX = 99 # Max RSI Level for Buy Signal - Over 80 considered overbought (55)
STOCH_MIN = 0 # Min Stoch %K Level for Buy Signal - Under 15 considered bearish until it crosses %D line (12)
STOCH_MAX = 99 # Max Stoch %K Level for Buy Signal - Over 80 ok as long as %D line doesn't cross %K (99)

RSI_BUY = 0.3 # Difference in RSI levels over last 2 timescales for value Buy Signal (-0.3)
STOCH_BUY = 10 # Difference between the Stoch K&D levels for value Buy Signal (10)

SELL_COINS = True # Set to true if you want the module to sell coins immediately upon bearish signals (False)
RSI_SELL = -5 # Difference in RSI levels over last 2 timescales for value Sell Signal (-5)
STOCH_SELL = -10 # Difference between the Stoch D&K levels for value Sell Signal (-10)
SIGNALS_SELL = 7 # Max number of buy signals on both INTERVALs to add coin to sell list (7)

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
PAIR_WITH = 'USDT'
TICKERS = 'tickerlists/tickers.txt' #'signalsample.txt'
TICKERS_OVERRIDE = 'tickers_signalbuy.txt'

if os.path.exists(TICKERS_OVERRIDE):
    TICKERS = TICKERS_OVERRIDE


TIME_TO_WAIT = 2 # Minutes to wait between analysis
FULL_LOG = False # List analysis result to console

SIGNAL_NAME = 'nigec_signalbuy_RSI'
SIGNAL_FILE_BUY = 'signals/' + SIGNAL_NAME + '.buy'

TRADINGVIEW_EX_FILE = 'tradingview_ta_unknown'

########################################
# Do NOT edit settings below these lines
########################################

def analyze(pairs):

    signal_coins = {}
    analysis = {}
    handler = {}
    analysis2 = {}
    handler2 = {}
    
    if os.path.exists(SIGNAL_FILE_BUY):
        os.remove(SIGNAL_FILE_BUY)
        
    #BBif os.path.exists('signals/custsignalmod.sell'):
    #BB  os.remove('signals/custsignalmod.sell')

    for pair in pairs:
        handler[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout= 10)
            
        handler2[pair] = TA_Handler(
            symbol=pair,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL2,
            timeout= 10)
            
    for pair in pairs:
        try:
            analysis = handler[pair].get_analysis()
            analysis2 = handler2[pair].get_analysis()
        except Exception as e:
            print(f'{SIGNAL_NAME}Exception:')
            print("Exception:")
            print(e)
            print (f'Coin: {pair}')
            print (f'handler: {handler[pair]}')
            print (f'handler2: {handler2[pair]}')
            
            with open(TRADINGVIEW_EX_FILE,'a+') as f:
                    #f.write(pair.removesuffix(PAIR_WITH) + '\n')
                    f.write(rchop(pair, PAIR_WITH) + '\n')
            continue

        oscCheck=0
        maCheck=0
        
        for indicator in OSC_INDICATORS:
            oscResult = analysis.oscillators ['COMPUTE'][indicator]
            #print(f'{pair} - Indicator for {indicator} is {oscResult}')
            if analysis.oscillators ['COMPUTE'][indicator] != 'SELL': oscCheck +=1
      	
        for indicator in MA_INDICATORS:
            if analysis.moving_averages ['COMPUTE'][indicator] == 'BUY': maCheck +=1		

        # Stoch.RSI (19 - 99), RSI (19 - 69)
        RSI = round(analysis.indicators['RSI'],2)
        RSI1 = round(analysis.indicators['RSI[1]'],2)
        STOCH_K = round(analysis.indicators['Stoch.K'],2)
        STOCH_D = round(analysis.indicators['Stoch.D'],2)
        STOCH_K1 = round(analysis.indicators['Stoch.K[1]'],2)
        STOCH_D1 = round(analysis.indicators['Stoch.D[1]'],2)
        EMA10 = round(analysis.indicators['EMA10'],2)
        EMA20 = round(analysis.indicators['EMA20'],2)
        EMA30 = round(analysis.indicators['EMA30'],2)
        SMA10 = round(analysis.indicators['SMA10'],2)
        SMA20 = round(analysis.indicators['SMA20'],2)
        SMA30 = round(analysis.indicators['SMA30'],2)
        BUY_SIGS = round(analysis.summary['BUY'],0)
        BUY_SIGS2 = round(analysis2.summary['BUY'],0)
        STOCH_DIFF = round(STOCH_K - STOCH_D,2)
        RSI_DIFF = round(RSI - RSI1,2)
        
        if FULL_LOG:
         if (RSI < 80) and (BUY_SIGS >= 10) and (STOCH_DIFF >= 0.01) and (RSI_DIFF >= 0.01):
          print(f'{SIGNAL_NAME} Signals OSC: {pair} = RSI:{RSI}/{RSI1} DIFF: {RSI_DIFF} | STOCH_K/D:{STOCH_K}/{STOCH_D} DIFF: {STOCH_DIFF} | BUYS: {BUY_SIGS}_{BUY_SIGS2}/26 | {oscCheck}-{maCheck}')

        if (RSI >= RSI_MIN and RSI <= RSI_MAX) and (RSI_DIFF >= RSI_BUY):
         if (STOCH_DIFF >= STOCH_BUY) and (STOCH_K >= STOCH_MIN and STOCH_K <= STOCH_MAX) and (STOCH_D >= STOCH_MIN and STOCH_D <= STOCH_MAX):
          if (BUY_SIGS >= MA_SUMMARY) and (BUY_SIGS2 >= MA_SUMMARY2) and (STOCH_K > STOCH_K1):
            if (oscCheck >= OSC_THRESHOLD and maCheck >= MA_THRESHOLD):
                signal_coins[pair] = pair
                
                print(f'\033[92m{SIGNAL_NAME} Signals RSI: {pair} - Buy Signal Detected | {BUY_SIGS}_{BUY_SIGS2}/26')
                
                with open(SIGNAL_FILE_BUY,'a+') as f:
                    f.write(pair + '\n')

                timestamp = datetime.now().strftime("%d/%m %H:%M:%S")
                with open(SIGNAL_NAME + '.log','a+') as f:
                    f.write(timestamp + ' ' + pair + '\n')
                    f.write(f'  {SIGNAL_NAME} Signals OSC: {pair} = RSI:{RSI}/{RSI1} DIFF: {RSI_DIFF} | STOCH_K/D:{STOCH_K}/{STOCH_D} DIFF: {STOCH_DIFF} | BUYS: {BUY_SIGS}_{BUY_SIGS2}/26 | {oscCheck}-{maCheck}\n')
            else:
                print(f'{SIGNAL_NAME} Signals RSI: {pair} - Stoch/RSI ok, not enough buy signals | {BUY_SIGS}_{BUY_SIGS2}/26 | {STOCH_DIFF}/{RSI_DIFF} | {STOCH_K}')
        
        #BBif SELL_COINS:
        #BB if (BUY_SIGS < SIGNALS_SELL) and (BUY_SIGS2 < SIGNALS_SELL) and (STOCH_DIFF < STOCH_SELL) and (RSI_DIFF < RSI_SELL) and (STOCH_K < STOCH_K1):
        #BB  #signal_coins[pair] = pair
        #BB  print(f'\033[33mSignals RSI: {pair} - Sell Signal Detected | {BUY_SIGS}_{BUY_SIGS2}/26')
        #BB  with open('signals/custsignalmod.sell','a+') as f:
        #BB     f.write(pair + '\n')
        #BB #else:
        #BB #   print(f'Signal: {pair} - Not selling!')
    
    return signal_coins

def do_work():        
    while True:
        try:
            if not os.path.exists(TICKERS):
                time.sleep((TIME_TO_WAIT*60))
                continue

            signal_coins = {}
            pairs = {}

            pairs=[line.strip() for line in open(TICKERS)]
            for line in open(TICKERS):
                pairs=[line.strip() + PAIR_WITH for line in open(TICKERS)] 

            if not threading.main_thread().is_alive(): exit()
            print(f'{SIGNAL_NAME} Signals RSI: Analyzing {len(pairs)} coins')
            signal_coins = analyze(pairs)
            print(f'{SIGNAL_NAME} Signals RSI: {len(signal_coins)} coins with Buy Signals. Waiting {TIME_TO_WAIT} minutes for next analysis.')
            time.sleep((TIME_TO_WAIT*60))
        except Exception as e:
            print(f'{SIGNAL_NAME}: Exception do_work() 1: {e}')
            continue
        except KeyboardInterrupt as ki:
            continue
