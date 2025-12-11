from yahooquery import Ticker
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from flask import Flask
from werkzeug.routing import BaseConverter
from random import randint
import json
import threading
import time as times
import re
import os

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super().__init__(url_map)
        self.regex = items[0]

with open("/config/config.json") as f:
  cfg = json.load(f)


tickers = cfg.get("tickers", [])
ticker_objs = {t: Ticker(t) for t in tickers}

data = {}
data_lock = threading.Lock()

app = Flask(__name__)

app.url_map.converters['regex'] = RegexConverter

def updater(data, tickers, ticker_objs, init=False):
    print("Starting Data Refresh")

    for ticker in tickers:
        try:

            result = ticker_objs[ticker].price

            if not isinstance(result, dict) or not result:
                raise ValueError("Bad or empty cached price data")

            if not init:
                if randint(1, 20) == 1:  
                    print(f"Forcing refresh of ticker object: {ticker}")
                    ticker_objs[ticker] = Ticker(ticker)
                    result = ticker_objs[ticker].price

                if not isinstance(result, dict) or not result:
                    raise ValueError("Fresh Ticker object also returned invalid data")

            with data_lock:
                data[ticker] = result

        except Exception as e:
            print(f"Error fetching {ticker} data: {e}")

            try:
                ticker_objs[ticker] = Ticker(ticker)
                result = ticker_objs[ticker].price

                if not isinstance(result, dict):
                    result = {}

                with data_lock:
                    data[ticker] = result

            except Exception as inner:
                print(f"Ticker rebuild failed for {ticker}: {inner}")
                with data_lock:
                    data[ticker] = {}

    print("Refreshed Data")
   

def update_loop():
    while True:
        time_delay = 330 + randint(1, 25)
        times.sleep(time_delay)
        if time_check_tz(time(9,30), time(16,00), "America/Toronto") and datetime.today().weekday() < 5:
            updater(data, tickers, ticker_objs)
        else:
            print("Markets Closed: No API Requests until open.")
        

@app.get("/v1/<regex('[A-Za-z0-9.\\-^]{1,15}'):ticker>")
def get_tick(ticker):
    raw = get_info(data, ticker)
    if not isinstance(raw, dict):
        return {"error": "Internal Server Error"}, 500

    inner = raw.get(ticker)
    if not isinstance(inner, dict):
        return {"error": "Internal Server Error"}, 500

    price = inner.get("regularMarketPrice")

    if not isinstance(price, (int, float)):
        return {"error": "Internal Server Error"}, 500
    
    return f"{price:.2f}"
    

@app.errorhandler(500)
def handle_500_error(e):
    return {"error": "Internal Server Error"}, 500

@app.errorhandler(404)
def handle_404_error(e):
    return {"error": "Internal Server Error"}, 500

def time_check_tz(beginning=None, ending=None, tz="America/Edmonton"):
    tzinfo = ZoneInfo(tz)
    now = datetime.now(tzinfo)
    check = now.time()

    today = now.date()
    bg = datetime.combine(today, beginning, tzinfo)
    ed = datetime.combine(today, ending, tzinfo)
    ch = datetime.combine(today, check, tzinfo)

    if ed < bg:
        ed += timedelta(days=1)
        if ch < bg:
            ch += timedelta(days=1)

    return bg <= ch <= ed

def get_info(data, ticker):
    return data.get(ticker)


updater(data, tickers, ticker_objs, True)
print("Data Initialization Complete.")
        

threading.Thread(target=update_loop, daemon=True).start()
 
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

