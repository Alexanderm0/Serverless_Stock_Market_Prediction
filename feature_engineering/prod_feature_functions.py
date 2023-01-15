import yfinance as yf
import pandas as pd
from random import randint
from sklearn.preprocessing import MinMaxScaler

def getEarnings(stock):
    """
    Function to get earnings and process the date indexing
    :param stock: yf.Ticker object of the stock to process
    :return: earnings of the respective stock, processed.
    """
    earn = stock.get_earnings_dates()
    if earn is not None:
        earn['Earnings Date'] = earn.index.date
        earn['Earnings Date'] = pd.to_datetime(earn['Earnings Date'])
    return earn

def getHistory(symbol, stock, period='1mo', interval='15m'):
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
    e_df.reset_index(inplace=True, drop=True)
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
    """
    Drop the columns which are not needed for the model
    :param hist_df: dataframe containing the history with all other attribute columns.
    :return: same df with the columns dropped.
    """
    labels = ['date', 'Earnings', 'company']
    return hist_df.drop(labels, axis=1)

def processStock(symbol, period='1mo', interval='15m', seq=240):
    """
    Functions to write stock information to CSV
    :param symbol: ticker symbol of the company
    :param earnings: dataframe containing the respective earnings
    :param period: over what time period the history data should be taken
    :param interval: how often a sample is taken over the period
    :return:
    """
    success = False
    stock = yf.Ticker(symbol)
    # earnings = getEarnings(stock)
    while not success:
        try:
            earnings = getEarnings(stock)
            success = True
        except:
            print('yfinance error retrieving data')
    hist = getHistory(symbol, stock, period=period, interval=interval)
    rel_earnings = getRelEarnings(earnings, hist)
    hist = getHistWithEarnings(rel_earnings, hist)
    hist = dropIrrelevant(hist)
    hist.reset_index(drop=True, inplace=True)
    hist = hist[:seq]
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(hist)
    return scaled_data

