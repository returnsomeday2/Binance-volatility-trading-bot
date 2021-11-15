FROM python:3.8.2-slim-buster


COPY /Binance_volatility_trading_bot_main/requirements.txt ./
RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY /user_data/. ./user_data/

WORKDIR /Binance_volatility_trading_bot_main
COPY /Binance_volatility_trading_bot_main/. ./Binance_volatility_trading_bot_main/

EXPOSE 8501
#EXPOSE 8051
	
CMD ./start.sh
