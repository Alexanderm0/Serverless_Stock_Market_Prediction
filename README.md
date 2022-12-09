# Serverless Stock Market Predictions
This project features a serverless machine learning pipeline for predicting the stock market price action based on past events.

### Data source
The real life data source will be taken from Yahoo Finance using the yfinance package: https://pypi.org/project/yfinance/

### Application
In the interface a user will be able to fill in the ticker symbol for a given stock. Based on this, the app will use the yfinance package to retrieve up-to-date historical data and perform inference on this input. Advice will be displayed to the user based on the intent, i.e. a short or long term investment.
