# Serverless Stock Market Predictions
#### Authors: Alexander Mo & Tommaso Lucarelli
This project features a serverless machine learning pipeline for 
predicting the stock market price action based on past events. The
resulting application can be found on: 
https://huggingface.co/spaces/tommyL99/Stock_Market_Prediction

### DISCLAIMER
This project is for educational and entertainment purposes only.
It is not advised to base any real world financial decisions partly,
or completely on this model.

### Data source
The real life data source will be taken from Yahoo Finance using 
the yfinance package: https://pypi.org/project/yfinance/

### Model
For this application, it has been opted for a Long-Short-Term-Memory
(LSTM) recurrent neural network (RNN) as this model has shown to
achieve great performance on this exact task according to Moghar &
Hamiche (https://www.sciencedirect.com/science/article/pii/S1877050920304865).

### Application
In the interface a user will be able to select the ticker symbol 
for a given stock in the list. Based on this, the app will use the 
yfinance package to retrieve up-to-date historical data and perform 
inference on this input. Advice will be displayed to the user 
based on the intent, i.e. a short or longer term investment.

### Project architecture
As mentioned, the project is based on serverless or modular design,
i.e. each pipeline is implemented separately to enhance testing;
maintenance; and robustness of the system. Specifically this project
consists of four main components:

##### 1. Feature pipeline
This pipeline takes one or more stock symbols as input for which data
is then retrieved through yfinance. This raw data is then processed
to contain desired features in the correct data format in order to
be interpreted by the training pipeline. These features are then
saved using a feature store (Google Drive in this implementation).
So this, or any application can access and retrieve the features
on demand.

##### 2. Training pipeline
Using the feature store, the implemented LSTM model will be able
to quickly access the data in the correct format. From there, the
model is trained as usual, after which it is deployed on Hugging
Face for easy access when doing inference.

##### 3. Inference pipeline
Using the trained model accessible on Hugging Face, the inference
pipeline simply parses the desired stock's raw data using the 
feature pipeline once more to get an interpretable format. Finally,
the trained model is queried using these features to return a prediction.

##### 4. User interface
In order to put this model into practice, an easily accessible UI
is provided as a web application developed using Gradio. This 
application allows the user to select any stock from the list and
input their intent in terms of the investment duration. From here,
the model will interpret the prediction and make a verdict on the
short term movement (positive or negative).
