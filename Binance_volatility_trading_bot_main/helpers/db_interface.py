from datetime import datetime

import pandas as pd
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base


class DbInterface():
    db_file_name = ''
    engine = None 
    metadata = None 
    connection = None 

    def __init__(self, db_path):
        self.engine = db.create_engine(f'sqlite:///{db_path}')
        self.connection = self.engine.connect()
        self.metadata = db.MetaData(self.engine)
        
        if 'transactions' not in self.metadata.sorted_tables:
            self.create_db()


    def create_db(self):
        self.metadata.reflect()
        self.metadata.drop_all(self.engine, tables= self.metadata.sorted_tables)

        transactions = db.Table('transactions', self.metadata,
                       db.Column('id', db.Integer(), db.Sequence('user_id_seq'), primary_key=True),
                       db.Column('order_id', db.Integer()),
                       db.Column('buy_time', db.TIMESTAMP, nullable=False),
                       db.Column('symbol', db.String, nullable=False),
                       db.Column('volume', db.Float(), nullable=False),
                       db.Column('bought_at', db.Float(), nullable=False),
                       db.Column('now_at', db.Float(), nullable=False),
                       db.Column('change_perc', db.Float(), nullable=False),
                       db.Column('profit_dollars', db.Float(), nullable=False),
                       db.Column('time_held', db.String(), nullable=False),
                       db.Column('tp_perc', db.Float(), nullable=False),
                       db.Column('sl_perc', db.Float(), nullable=False),
                       db.Column('TTP_TSL', db.Float(), nullable=True, default=False),
                       db.Column('closed', db.Integer(), default=0, nullable=False),
                       db.Column('sell_time', db.TIMESTAMP, nullable=True),
                       db.Column('sold_at', db.Float(), nullable=True),
                       db.Column('buy_signal', db.String, nullable=True),
                       db.Column('sell_reason', db.String, nullable=True),
                        extend_existing=True
                       )


        self.metadata.create_all(self.engine)  # Creates the table

    def add_record(self, record):
        transactions = db.Table('transactions', self.metadata, autoload=True, autoload_with=self.engine)

        # Inserting record one by one
        query = db.insert(transactions).values(**record)

        ResultProxy = self.connection.execute(query)

    def update_transaction_record(self, symbol, update_dict):
        transactions = db.Table('transactions', self.metadata, autoload=True, autoload_with=self.engine)

        query = db.update(transactions).values(update_dict)
        query = query.where(transactions.columns.symbol == symbol, transactions.columns.closed == 0)
        results = self.connection.execute(query)
