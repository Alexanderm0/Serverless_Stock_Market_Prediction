import yfinance as yf
import pandas as pd
from random import randint


def getEarnings(stock):
    return stock.earnings_history

def parseMonth(month):
    """
    Function to parse the string of a month from the earnings date
    :param month: string with the given month
    :return: the number corresponding to the month in datetime format
    """
    if month == 'Jan':
        return 1
    elif month == 'Feb':
        return 2
    elif month == 'Mar':
        return 3
    elif month == 'Apr':
        return 4
    elif month == 'May':
        return 5
    elif month == 'Jun':
        return 6
    elif month == 'Jul':
        return 7
    elif month == 'Aug':
        return 8
    elif month == 'Sep':
        return 9
    elif month == 'Oct':
        return 10
    elif month == 'Nov':
        return 11
    else:
        return 12

def convertEarningsDate(df):
    """
    Function to convert the earnings date format to datetime
    :param df: dataframe containing the earnings history
    :return: dataframe updated with the parsed datetime as date
    """
    test = [None]*len(df)
    for i in range(len(df)):
        temp = df.loc[i, "Earnings Date"].split(', ')
        temp = [x.strip() for x in temp]
        temp = (temp[0] + ' ' + temp[1]).split(' ')
        test[i] = [temp[2], parseMonth(temp[0]), temp[1]]
    dt = pd.DataFrame(test, columns=['year', 'month', 'day'])
    df['Earnings Date'] = pd.to_datetime(dt)
    return df

def getHistory(symbol, stock, period='30d', interval='30m'):
    """
    Function to retrieve the price history of the stock and parse its date
    :param stock: yfinance ticker object
    :param period: the period over which data should be collected
    :param interval: the interval for data points
    :return: history dataframe with additional columns
    """
    hist = stock.history(period = period, interval = interval)
    hist['company'] = symbol
    hist['date'] = hist.index.date
    hist['date'] = pd.to_datetime(hist['date'])
    hist['Diff'] = hist['Close'] - hist['Open']
    return hist

def getRelEarnings(e_df, hist_df):
    """
    Finds the earnings data which is relevant for the given history time frame
    :param e_df: earnings dataframe
    :param hist_df: history dataframe
    :return: relevant dates dataframe
    """
    minmax = hist_df['date'].agg(['min', 'max'])
    last_er_idx = e_df[e_df['Earnings Date'] <= minmax['min']].index[0]
    first_er_idx = e_df[e_df['Earnings Date'] <= minmax['max']].index[0]
    relevant_earnings = e_df[first_er_idx:last_er_idx+1].reset_index(drop=True)
    return relevant_earnings

def fillEarnings(current, hist_df, idx_in):
    """
    Function to fill the earnings columns into the history
    :param current: dataframe holding the earnings data for the selected indices
    :param hist_df: history dataframe
    :param idx_in: relevant indices on the history dataframe to fill the earnings data for
    :return: history dataframe with the earnings added for the given indices
    """
    hist_df.loc[idx_in, 'EPS Estimate'] = current['EPS Estimate']
    hist_df.loc[idx_in, 'Reported EPS'] = current['Reported EPS']
    hist_df.loc[idx_in, 'Offset'] = current['Surprise(%)']
    hist_df.loc[idx_in, 'Earnings'] = current['Earnings Date']
    return hist_df

def getHistWithEarnings(relevant_earnings, hist_df):
    """
    Function to add the corresponding earnings data to the days for which the data was known.
    :param relevant_earnings: The earnings columns which are relevant for the given history time frame
    :param hist_df: The history dataframe
    :return: History with added columns for each of the relevant earnings
    """
    for idx in reversed(relevant_earnings.index):
        if idx>0:
            current = relevant_earnings.iloc[idx]
            next = relevant_earnings.iloc[idx-1]
            idx_in = hist_df[(hist_df['date'] >= current['Earnings Date']) &
                             (hist_df['date'] < next['Earnings Date'])].index
            hist_df = fillEarnings(current, hist_df, idx_in)
        else:
            current = relevant_earnings.iloc[idx]
            idx_in = hist_df[(hist_df['date'] >= current['Earnings Date'])].index
            hist_df = fillEarnings(current, hist_df, idx_in)
    return hist_df

def dropIrrelevant(hist_df: pd.DataFrame):
    labels = ['']
    return hist_df.drop(labels, axis=1)

def stockToCSV(symbol, period='60d', interval='30m'):
    """
    Functions to write stock information to CSV
    :param symbol: ticker symbol of the company
    :param period: over what time period the history data should be taken
    :param interval: how often a sample is taken over the period
    :return:
    """
    stock = yf.Ticker(symbol)
    earnings = getEarnings(stock)
    earnings = convertEarningsDate(earnings)
    hist = getHistory(symbol, stock, period=period, interval=interval)
    rel_earnings = getRelEarnings(earnings, hist)
    hist = getHistWithEarnings(rel_earnings, hist)
    hist.to_csv('./data/' + symbol)

def stockToDf(symbol, period='60d', interval='30m'):
    """
    Functions to write stock information to CSV
    :param symbol: ticker symbol of the company
    :param period: over what time period the history data should be taken
    :param interval: how often a sample is taken over the period
    :return:
    """
    stock = yf.Ticker(symbol)
    earnings = getEarnings(stock)
    earnings = convertEarningsDate(earnings)
    hist = getHistory(symbol, stock, period=period, interval=interval)
    rel_earnings = getRelEarnings(earnings, hist)
    hist = getHistWithEarnings(rel_earnings, hist)
    return hist

def getStocks():
    """
    Get all stock symbols listed on Nasdaq
    :return: list with symbols
    """
    df = pd.read_table('http://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt')
    # local run
    # df = pd.read_table('tickers.txt')
    symbols = [None]*len(df)
    for idx, line in df.iterrows():
        symbols[idx] = line[0].split('|')[0]
    return symbols

def selectStocks(stocks, n):
    """
    Select n random stocks from the list
    :param stocks: list of company symbols
    :param n: number of companies to select
    :return: selected symbols
    """
    idxs = []
    selected = [None]*n
    counter = 0
    while len(idxs) < n:
        temp_int = randint(0, len(stocks))
        if temp_int not in idxs:
            if yf.Ticker(stocks[temp_int]).earnings_history is not None:
                idxs.append(temp_int)
                selected[counter] = stocks[temp_int]
                counter += 1
    return selected

def selectAll(stocks):
    """
    Select all stocks which have enough data on yfinance listed on the Nasdaq list
    :param stocks: list of company symbols fom Nasdaq
    :return: current symbols
    """
    selected = []
    for stock in stocks:
        if yf.Ticker(stock).earnings_history is not None:
            selected.append(stock)
    return selected
