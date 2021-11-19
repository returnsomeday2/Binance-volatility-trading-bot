

################
'''
{
    "e": "kline",     // Event type
    "E": 123456789,   // Event time
    "s": "BNBBTC",    // Symbol
    "k": {
        "t": 123400000, // Kline start time
        "T": 123460000, // Kline close time
        "s": "BNBBTC",  // Symbol
            "i": "1m",      // Interval
            "f": 100,       // First trade ID
            "L": 200,       // Last trade ID
            "o": "0.0010",  // Open price
            "c": "0.0020",  // Close price
            "h": "0.0025",  // High price
            "l": "0.0015",  // Low price
            "v": "1000",    // Base asset volume
            "n": 100,       // Number of trades
            "x": false,     // Is this kline closed?
            "q": "1.0000",  // Quote asset volume
            "V": "500",     // Taker buy base asset volume
            "Q": "0.500",   // Taker buy quote asset volume
            "B": "123456"   // Ignore
    }
}'''

KLINE_EVENT = "kline"
ERROR_EVENT = "error"

EVENT_TYPE = 'e'
EVENT_TIME = 'E'
SYMBOL = 's'
KLINE_DATA = 'k'

OPEN_TIME = 't'
CLOSE_TIME = 'T'
SYMBOL = 's'
INTERVAL = 'i'
FIRST_TRADE_ID = 'f'
LAST_TRADE_ID = 'L'
OPEN_PRICE = 'o'
CLOSE_PRICE = 'c'
HIGH_PRICE = 'h'
LOW_PRICE = 'l'
VOLUME = 'v'
TRADES = 'n' # NUMBER_OF_TRADES
IS_CLOSED = 'x'
QAV = 'q' # QUOTE_ASSET_VOLUME
TBBAV = 'V' # TAKER_BUY_BASE_ASSET_VOLUME
TBQAV = 'Q' # TAKER_BUY_QUOTE_ASSET_VOLUME
IGNORE = 'B'