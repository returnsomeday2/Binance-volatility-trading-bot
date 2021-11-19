import atexit
import os
import signal
import threading
from datetime import datetime
import time
from logging import Logger

from binance import Client, ThreadedWebsocketManager


from db.candle_db_manager import ManagedCandleDBSession, init_candle_session_factory


from helpers.db_ohlc import *
from globals import user_data_path
from helpers.handle_creds import load_correct_creds
from helpers.parameters import parse_args, load_config

from db.constants import *
from db.candle import WSCandle, Candle

logger = Logger("Binance_websocket_service")
logger.info("Starting binance db_candle...")

args = parse_args()
DEFAULT_CONFIG_FILE = user_data_path + 'config.yml'
DEFAULT_CREDS_FILE = user_data_path + 'creds.yml'
config_file = args.config if args.config else DEFAULT_CONFIG_FILE
creds_file = args.creds if args.creds else DEFAULT_CREDS_FILE
parsed_config = load_config(config_file)
PAIR_WITH = parsed_config['trading_options']['PAIR_WITH']
EX_PAIRS = parsed_config['trading_options']['EX_PAIRS']
CUSTOM_LIST = parsed_config['trading_options']['CUSTOM_LIST']
CUSTOM_LIST_AUTORELOAD = parsed_config['trading_options']['CUSTOM_LIST_AUTORELOAD']
TICKERS_LIST = parsed_config['trading_options']['TICKERS_LIST']

INIT_START = parsed_config['data_options']['INIT_START']
INTERVAL = parsed_config['data_options']['INTERVAL']
INIT_PERIOD = parsed_config['data_options']['INIT_PERIOD']
DB_FILE_NAME = parsed_config['data_options']['DB_CANDLE_FILE_NAME']
TIME_TO_WAIT = 1 # Minutes to wait between ticker list update
SERVICE_NAME = 'Binance_websocket'
CLEAN_START = True


FIATS = parsed_config['trading_options']['FIATS']
ignore = FIATS + ['UP', 'DOWN', 'AGLD', 'AUD', 'BRL', 'BVND', 'BCC', 'CVP', 'BCHABC', 'BCHSV', 'BEAR', 'BNBBEAR', 'BNBBULL',
          'BULL', 'BKRW', 'DAI', 'ERD', 'EUR', 'FRONT', 'USDS', 'HC', 'LEND', 'MCO', 'GBP', 'RUB',
          'TRY', 'NPXS', 'PAX', 'STORM', 'VEN', 'UAH', 'NGN', 'VAI', 'STRAT', 'SUSD', 'XZC', 'RAD', 'USDC']

AMERICAN_USER = parsed_config['script_options'].get('AMERICAN_USER')
parsed_creds = load_config(creds_file)
access_key, secret_key = load_correct_creds(parsed_creds)

# Authenticate with the client, Ensure API key is good before continuing
if AMERICAN_USER:
    client = Client(access_key, secret_key, tld='us')
else:
    client = Client(access_key, secret_key)

currency_pair_data = {}
keys = ['t', 'o', 'l', 'h', 'c', 'v', 'T', 'q', 'n', 'V', 'Q', 'B']

STOP_UNLISTED_PAIR = False
SAVE2DB=True

if SAVE2DB:

    client = Client("", "")
    bsm = ThreadedWebsocketManager()
    bsm_open_sockets = {}
    print('WAIT WAIT WAIT')
    init_candle_session_factory(uri=user_data_path + DB_FILE_NAME, clean_start=True)
    print('HELLO HELLO')
from db.candle_db_manager import engine as candle_engine


def get_pairs():
    if CUSTOM_LIST:
        while True:
            if not os.path.exists(TICKERS_LIST):
                print(f"Binance websocket service : Autoreload tickers cannot find {TICKERS_LIST} file. Will retry in 1 second.")
                time.sleep(1)
            else:
                break
        symbols = [line.strip() for line in open(TICKERS_LIST)]
        symbols = [s + PAIR_WITH for s in symbols if s not in EX_PAIRS]
    else:
        response = client.get_ticker()
        symbols = []

        for symbol in response:
            if PAIR_WITH in symbol['symbol'] and all(item not in symbol['symbol'] for item in ignore):
                if symbol['symbol'][-len(PAIR_WITH):] == PAIR_WITH:
                    symbols.append(symbol['symbol'])
                symbols.sort()
    return symbols


def add_candle_2_db(candle):
    with ManagedCandleDBSession() as session:
        pg_try = 0
        while True:
            # time.sleep(5)
            try:
                if isinstance(candle, list):
                    # session.execute("CREATE TEMPORARY TABLE IF NOT EXISTS temp_candle AS(SELECT * FROM candles)")

                    session.bulk_save_objects(candle)
                    # [session.merge(c) for c in candle]
                else:
                    session.merge(candle)
                break
            except Exception as e:
                pass

                y = set(candle)
                # pg_try += 1
                # if pg_try > 3:
                #     logger.error(f"{SERVICE_NAME}: Unable to INSERT to candle DB from")
                #     break
            finally:
                break

# columns = ['open', 'high', 'low', 'close', 'volume']
def kline_streaming_data_process(msg):
    """
    Function to process the received messages and add latest token id price
    into the dictionary
    :param msg: input message
    """
    if msg[EVENT_TYPE] == ERROR_EVENT:
        logger.error(msg)
        exit(1)

    candle = WSCandle(msg)

    if candle.closed:
        # global init
        logger.info(f'New candle: {candle}')


        add_candle_2_db(candle)

def download_historical_data(pair, interval, start_str, end_str):
    klines = client.get_historical_klines(pair, interval, start_str, end_str)[:-1]
    logger.info("Data retrieved, adding to db_candle...")

    # add_candle_2_db([Candle(pair, kline) for kline in klines])

    try:
        df = pd.DataFrame(klines)
        df['pair'] = pair
        df.columns = ['open_time', 'open_price', 'high', 'low', 'close_price', 'volume', 'close_time', 'x1','x2','x3','x4', 'x5', 'pair']
        df = df[['pair', 'open_time', 'close_time', 'open_price', 'close_price', 'high', 'low', 'volume']]
        df.open_time = pd.to_datetime(df.open_time, unit='ms')
        df.close_time = pd.to_datetime(df.close_time, unit='ms')
        df.open_price = df.open_price.astype(float)
        df.close_price = df.close_price.astype(float)
        df.high = df.high.astype(float)
        df.low = df.low.astype(float)
        df.volume = df.volume.astype(float)

        with ManagedCandleDBSession() as session:
            temp_table = f'temp_candle_{pair.lower()}'
            df.to_sql(temp_table, candle_engine, if_exists="replace", index=False)
            insert_sql = f'INSERT INTO candles (SELECT * FROM {temp_table}) ON CONFLICT DO NOTHING'
            session.execute(insert_sql)
            session.execute(f'DROP TABLE IF EXISTS {temp_table};')
        logger.info(f"Historical data for {pair } loaded...")
    except Exception as e:
        print(f'{SERVICE_NAME}: error downloading historical data for {pair} -> {e}')

def init_pair_df():
    df = pd.DataFrame(columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df = df.set_index('timestamp')
    df.index = pd.to_datetime(df.index, unit='ms')
    return df

import asyncio
# https://www.delftstack.com/howto/python/parallel-for-loops-python/
def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped

@background
def start_data_websocket(pair):
    # if not bsm.is_alive():
    #     bsm.start()

    if pair not in currency_pair_data:
        print(f'Starting websocket for {pair}')
        bsm_open_sockets[pair] = bsm.start_kline_socket(callback=kline_streaming_data_process, symbol=pair, interval=INTERVAL)
        if INIT_START:
            download_historical_data(pair, INTERVAL, INIT_PERIOD, end_str=f'{datetime.datetime.utcnow()}')


@atexit.register
def cleanup():
    print("\nClosing binance sockets...")
    for key, s in bsm_open_sockets.items():
        bsm.stop_socket(s)
    print("Binance sockets closed...")

if os.name != 'nt':
    print('signal registration')
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGTSTP, cleanup)
    signal.signal(signal.SIGINT, cleanup)

def do_work():
    print('HERE HERE HERE')
    if SAVE2DB:
        bsm.start()

    pairs = get_pairs()

    for pair in pairs:
        start_data_websocket(pair)

    while True:
        try:
            if not threading.main_thread().is_alive(): exit()
            if CUSTOM_LIST:
                if CUSTOM_LIST_AUTORELOAD:
                    temp_pairs = get_pairs()
                    removed_pairs = set(pairs) - set(temp_pairs)
                    new_pairs = set(temp_pairs) - set(pairs)
                    pairs = set(pairs) - removed_pairs + new_pairs

                    for pair in new_pairs:
                        start_data_websocket(pair)

            time.sleep(TIME_TO_WAIT * 60) #check every minute if ticker list has changed
        except Exception as e:
            print(f'{SERVICE_NAME}: Exception: {e}')
            # continue
        except KeyboardInterrupt as ki:
            continue


if __name__ == "__main__":
    do_work()