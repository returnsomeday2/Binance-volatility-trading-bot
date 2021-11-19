from datetime import datetime

from .constants import *
from . import constants_klines
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, DateTime, Index

Base = declarative_base()

class Candle(Base):
    __tablename__ = 'candles'

    pair = Column(String, primary_key=True)
    open_time = Column(DateTime, primary_key=True)
    close_time = Column(DateTime)
    open_price = Column(Float)
    close_price = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)
    # qav = Column(Float)
    # trades = Column(Integer)
    # tbbav = Column(Float)
    # tbqav = Column(Float)

    __table_args__ = (
        Index('open_time_asc', open_time.asc(), postgresql_using='btree'),
        Index('open_time_desc', open_time.desc(), postgresql_using='btree'),
    )

    def __init__(self, pair, kline):
        self.pair = pair
        self.open_time = self.to_date(kline[constants_klines.OPEN_TIME])
        self.close_time = self.to_date(kline[constants_klines.CLOSE_TIME])
        self.open_price = float(kline[constants_klines.OPEN_PRICE])
        self.close_price = float(kline[constants_klines.CLOSE_PRICE])
        self.high = float(kline[constants_klines.HIGH])
        self.low = float(kline[constants_klines.LOW])
        self.volume = float(kline[constants_klines.VOLUME])
        # self.qav = float(kline[QAV])
        # self.trades = kline[TRADES]
        # self.tbbav = float(kline[TBBAV])
        # self.tbqav = float(kline[TBQAV])

    def __eq__(self, other):
        if other == None:
            return False
        return self.pair == other.pair and self.close_time == other.close_time

    def __hash__(self):
        return hash(('pair', self.pair,
                     'close_time', self.close_time))

    def __repr__(self):
        date = self.open_time.strftime('%Y-%m-%d %H:%M:%S')
        return "<Candle(id={}, open_time={}, open={}, close={})>".format(
                self.pair, date, self.open_price, self.close_price)

    @staticmethod
    def to_date(timestamp):
        return datetime.utcfromtimestamp(timestamp / 1000)

class WSCandle(Candle):
    def __init__(self, ws_event):
        self.pair = ws_event[SYMBOL]
        self.open_time = self.to_date(ws_event[KLINE_DATA][OPEN_TIME])
        self.close_time = self.to_date(ws_event[KLINE_DATA][CLOSE_TIME])
        self.open_price = float(ws_event[KLINE_DATA][OPEN_PRICE])
        self.close_price = float(ws_event[KLINE_DATA][CLOSE_PRICE])
        self.high = float(ws_event[KLINE_DATA][HIGH_PRICE])
        self.low = float(ws_event[KLINE_DATA][LOW_PRICE])
        self.volume = float(ws_event[KLINE_DATA][VOLUME])
        self.qav = float(ws_event[KLINE_DATA][QAV])
        self.trades = ws_event[KLINE_DATA][TRADES]
        self.tbbav = float(ws_event[KLINE_DATA][TBBAV])
        self.tbqav = float(ws_event[KLINE_DATA][TBQAV])
        self.closed = ws_event[KLINE_DATA][IS_CLOSED]