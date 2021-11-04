from tradingview_ta import TA_Handler, Interval, Exchange
import os
import time
import threading

INTERVAL = Interval.INTERVAL_1_MINUTE #Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SYMBOL = 'BTCUSDT'
TIME_TO_WAIT = 1
SIGNAL_NAME = 'os_pausebot_MA'
SIGNAL_FILE = 'signals/pausebot.pause'

def analyze():

    analysis = {}
    handler = {}

    handler = TA_Handler(
            symbol=SYMBOL,
            exchange=EXCHANGE,
            screener=SCREENER,
            interval=INTERVAL,
            timeout= 10)

    try:
        analysis = handler.get_analysis()

    except Exception as e:
        print("{SIGNAL_NAME}:")
        print("Exception:")
        print(e)
        return

    ma_analysis_sell = analysis.moving_averages['SELL']
    ma_analysis_buy = analysis.moving_averages['BUY']
    ma_analysis_neutral = analysis.moving_averages['NEUTRAL']

    # if ma_analysis_sell >= (ma_analysis_buy + ma_analysis_neutral) or price_downward_trend():       
    if ma_analysis_sell >= (ma_analysis_buy + ma_analysis_neutral):       
        paused = True
        # print(f'pausebotmod: {SYMBOL} Market not looking too good, bot paused from buying. SELL indicators: {ma_analysis_sell}. BUY/NEUTRAL indicators: {ma_analysis_buy + ma_analysis_neutral}. P: {price} | LP: {lastprice} | Waiting {TIME_TO_WAIT} minutes for next market checkup')
        print(f'{SIGNAL_NAME}: {SYMBOL} Market not looking too good, bot paused from buying. SELL indicators: {ma_analysis_sell}. BUY/NEUTRAL indicators: {ma_analysis_buy + ma_analysis_neutral}. Waiting {TIME_TO_WAIT} minutes for next market checkup')
    else:
        #print(f'pausebotmod: {SYMBOL} Market looks ok, bot is running. SELL indicators: {ma_analysis_sell}. BUY/NEUTRAL indicators: {ma_analysis_buy + ma_analysis_neutral}. P: {price} | LP: {lastprice} | Waiting {TIME_TO_WAIT} minutes for next market checkup')
        print(f'{SIGNAL_NAME}: {SYMBOL} Market looks ok, bot is running. SELL indicators: {ma_analysis_sell}. BUY/NEUTRAL indicators: {ma_analysis_buy + ma_analysis_neutral}. Waiting {TIME_TO_WAIT} minutes for next market checkup')
        paused = False

    #lastprice = price

    return paused
#if __name__ == '__main__':
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

        
    
