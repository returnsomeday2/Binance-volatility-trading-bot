# https://gist.github.com/nitred/4323d86bb22b7ec788a8dcfcac03b27a

import contextlib
import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy_utils import database_exists, create_database

from db.candle import Candle
from globals import user_data_path
from helpers.parameters import load_config
from utilities.txcolors import txcolors

config_file = user_data_path +'config.yml'
parsed_config = load_config(config_file)
DB_TYPE =  parsed_config['data_options']['DB_TYPE']
POSTGRESS_HOST =  parsed_config['data_options']['POSTGRESS_HOST']
POSTGRESS_PORT =  parsed_config['data_options']['POSTGRESS_PORT']
POSTGRES_USER =  parsed_config['data_options']['POSTGRES_USER']
POSTGRES_PASS =  parsed_config['data_options']['POSTGRES_PASS']
POSTGRESS_DB =  parsed_config['data_options']['POSTGRESS_DB']


engine = None
thread_safe_session_factory = None

# def init_candle_engine(uri, clean_start=False, **kwargs):
#     """Initialize the engine.
#     Args:
#         uri (str): The string database URI. Examples:
#             - sqlite:///database.db
#             - postgresql+psycopg2://username:password@0.0.0.0:5432/database
#     """
#     global engine
#     if engine is None:
#         if DB_TYPE == 'SQLITE':
#             engine = create_engine(uri, **kwargs)
#         elif DB_TYPE == 'POSTGRES':
#             db_url = f"postgres://{POSTGRES_USER}:{POSTGRES_PASS}@localhost/{POSTGRESS_DB}"
#             engine = create_engine(db_url)
#             if not database_exists(db_url):
#                 create_database(db_url)
#         else:
#             raise Exception(f'candle_db_manager: Unknown database type{txcolors.ERROR}')
#     if clean_start:
#         metadata = MetaData(engine)
#         metadata.reflect()
#         metadata.drop_all(engine, tables=metadata.sorted_tables)
#
#     return engine


def init_candle_session_factory(uri, clean_start=False, **kwargs):
    """Initialize the engine.
        Args:
            uri (str): The string database URI. Examples:
                - sqlite:///database.db
                - postgresql+psycopg2://username:password@0.0.0.0:5432/database
        """
    clean_start = False
    try:
        global engine
        if engine is None:
            if DB_TYPE == 'SQLITE':
                engine = create_engine(uri, **kwargs)
            elif DB_TYPE == 'POSTGRES':
                if os.name == 'nt':
                    db_host = f'{POSTGRESS_HOST}:{POSTGRESS_PORT}'
                else:
                    db_host = f'{POSTGRESS_HOST}'
                db_url = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASS}@{db_host}/{POSTGRESS_DB}"
                engine = create_engine(db_url)
                if not database_exists(db_url):
                    create_database(db_url)
                print(f'Connected to POSTGRES database successfully{txcolors.SUCCESS}')
            else:
                print(f'candle_db_manager: Unknown database type{txcolors.ERROR}')
                exit(-1)

        # if clean_start:
        #     metadata = MetaData(engine)
        #     metadata.reflect()
        #     metadata.drop_all(engine, tables=metadata.sorted_tables)

        Candle.metadata.create_all(engine)
        print('Candle DB created.')

        """Initialize the thread_safe_session_factory."""
        global thread_safe_session_factory
        # if engine is None:
        #     raise ValueError("Initialize engine by calling init_candle_engine before calling init_session_factory!")
        if thread_safe_session_factory is None:
            thread_safe_session_factory = scoped_session(sessionmaker(bind=engine))
        return thread_safe_session_factory
    except Exception as e:
        print(f'candle_db_manager: error {e}{txcolors.ERROR}')

@contextlib.contextmanager
def ManagedCandleDBSession():
    """Get a session object whose lifecycle, commits and flush are managed for you.
    Expected to be used as follows:
    ```
    with ManagedCandleDBSession() as session:            # multiple db_operations are done within one session.
        db_operations.select(session, **kwargs)  # db_operations is expected not to worry about session handling.
        db_operations.insert(session, **kwargs)  # after the with statement, the session commits to the database.
    ```
    """
    global thread_safe_session_factory
    if thread_safe_session_factory is None:
        raise ValueError("Call init_session_factory before using ManagedCandleDBSession!")
    session = thread_safe_session_factory()
    try:
        yield session
        session.commit()
        session.flush()
    except Exception:
        session.rollback()
        # When an exception occurs, handle session session cleaning,
        # but raise the Exception afterwards so that user can handle it.
        raise
    finally:
        # source: https://stackoverflow.com/questions/21078696/why-is-my-scoped-session-raising-an-attributeerror-session-object-has-no-attr
        thread_safe_session_factory.remove()