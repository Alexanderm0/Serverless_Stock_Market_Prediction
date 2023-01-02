"""
Authors: Alexander Mo & Tommaso Lucarelli

Feature pipeline to pre-process incoming data
"""

import modal
import yfinance as yf
import pandas as pd
from random import randint
from stock_processing_functions import getStocks, selectAll, selectStocks, stockToDf, stockToCSV

N = 10


def preprocessStockData(n, all_stocks=True):
    """
    Preprocess data into interpretable format
    :param all_stocks: boolean to do all stocks or to do n random ones
    :param n: number of random stocks to process
    :return: dataframe with the preprocessed data, all companies concatenated
    """
    stocks = getStocks()
    if all_stocks:
        selected = selectAll(stocks)
    else:
        selected = selectStocks(stocks, n)
    df = pd.DataFrame()
    for stock in selected:
        df = df.append(stockToDf(stock))
    return df


LOCAL = True

if LOCAL == False:
    stub = modal.Stub()
    image = modal.Image.debian_slim().pip_install(
        ["hopsworks==3.0.4", "joblib", "seaborn", "sklearn", "dataframe-image"])
    # "yfinance --upgrade --no-cache-dir",

    @stub.function(image=image, schedule=modal.Period(days=1), secret=modal.Secret.from_name("HOPSWORKS_API_KEY"))
    def f():
        g()


def g():
    import hopsworks
    import pandas as pd

    project = hopsworks.login(
        api_key_value="3iG2VIJVq2uuEjxu.pCmzotAAAzGqUJEeJNfgsvuXMJDzjciEJOCgjOs5tqSpBJbJ6FPM1DAadY42mrlD")
    fs = project.get_feature_store()
    stock_df = pd.read_csv("https://repo.hops.works/master/hopsworks-tutorials/data/iris.csv")
    stock_fg = fs.get_or_create_feature_group(
        name="stocks",
        version=1,
        primary_key=["date", "sepal_width", "petal_length", "petal_width"],
        description="Iris flower dataset")
    iris_fg.insert(iris_df, write_options={"wait_for_job": False})


if __name__ == "__main__":
    if LOCAL == True:
        g()
    else:
        with stub.run():
            f()
