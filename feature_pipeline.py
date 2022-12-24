"""
Authors: Alexander Mo & Tommaso Lucarelli

Feature pipeline to pre-process incoming data
"""


import yfinance as yf

def getStockData(ticker_symbol):
    stock = yf.Ticker(ticker_symbol)
    return stock.info, stock.history()


