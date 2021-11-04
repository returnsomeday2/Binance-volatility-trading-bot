from tradingview_ta import TA_Handler, Interval, Exchange
import os
import time
import threading
from globals import user_data_path
from utilities.misc import notify_bot_pause
INTERVAL = Interval.INTERVAL_1_MINUTE #Timeframe for analysis

EXCHANGE = 'BINANCE'
SCREENER = 'CRYPTO'
SYMBOL = 'BTCUSDT'
THRESHOLD = 7 # 7 of 15 MA's indicating sell
TIME_TO_WAIT = 5 # Minutes to wait between analysis
FULL_LOG = False # List analysis result to console
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
        print("pausebotmod:")
        print("Exception:")
        print(e)
        return
    
    ma_sell = analysis.moving_averages['SELL']
    if ma_sell >= THRESHOLD:
        paused = True
        print(f'pausebotmod: Market not looking too good, bot paused from buying {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup')
    else:
        print(f'pausebotmod: Market looks ok, bot is running {ma_sell}/{THRESHOLD} Waiting {TIME_TO_WAIT} minutes for next market checkup ')
        paused = False

    notify_bot_pause(user_data_path, paused, TIME_TO_WAIT)
    return paused

def do_work():
      
    while True:
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

# if __name__ == '__main__':
#     do_work()