import pandas as pd
import yfinance as yf
import mplfinance as mf
import numpy as np
import matplotlib.pyplot as plt
from ta.trend import ADXIndicator


#input data (prices,vixc et), days=simple moving average windows
def sma(close_prices,days):
    ma = [0]*len(close_prices)
    for i in range(days,len(close_prices)):
        ma[i] = sum(close_prices[i-days:i])/days
    return ma

def ema(close_prices,sma,smoothing,days):
    emavg = [0]*len(close_prices)
    emavg[days] = sma[days]
    for i in range(days+1,len(close_prices)):
        emavg[i] = (close_prices[i]-emavg[i-1])*smoothing+emavg[i-1]
    return emavg

#MACD
#input yfinance dataframe, returns dataframe with macd and macdindicator added
def macd(data):
    smoothing12 = 2/13
    smoothing26 = 2/27
    smoothing9 = 2/10
    sma12 = sma(data['Close'],12)
    sma26 = sma(data['Close'],26)

    ema12 = ema(data['Close'],sma12,smoothing12,12)
    ema26 = ema(data['Close'],sma26,smoothing26,26)
    macd = np.subtract(ema12,ema26)
    data['macd'] = macd
    data['macd_indicator'] = np.where(macd>0,1,0)
    return data

#RSI
def rsi(data):
    window_length = 3
    delta = data['Close'].diff()
    delta = delta[1:]

    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0


    # Calculate the EWMA
    roll_up1 = up.ewm(span=window_length).mean()
    roll_down1 = down.abs().ewm(span=window_length).mean()

    # Calculate the RSI based on EWMA
    RS1 = roll_up1 / roll_down1
    RSI1 = 100.0 - (100.0 / (1.0 + RS1))

    # Calculate the SMA
    roll_up2 = up.rolling(window_length).mean()
    roll_down2 = down.abs().rolling(window_length).mean()

    # Calculate the RSI based on SMA
    RS2 = roll_up2 / roll_down2
    RSI2 = 100.0 - (100.0 / (1.0 + RS2))

    data['rsi'] = RSI2
    data['rsi_indicator'] = np.where(data['rsi']>50,1,0)

    return data

#In Squeeze
def in_squeeze(df):
    return np.where((df['lower_band'] > df['lower_keltner']) and (df['upper_band'] < df['upper_keltner']),1,0)

#TTM
#Input yfinance dataframe, return dataframe with ttm squeeze on RSI_indicator
def ttm(df):
    df['20sma'] = df['Close'].rolling(window=20).mean()
    df['stddev'] = df['Close'].rolling(window=20).std()
    df['lower_band'] = df['20sma'] - (2 * df['stddev'])
    df['upper_band'] = df['20sma'] + (2 * df['stddev'])

    df['TR'] = abs(df['High'] - df['Low'])
    df['ATR'] = df['TR'].rolling(window=20).mean()

    df['lower_keltner'] = df['20sma'] - (df['ATR'] * 1.5)
    df['upper_keltner'] = df['20sma'] + (df['ATR'] * 1.5)

    df['ttm_indicator'] = df.apply(in_squeeze, axis=1)
    return df

#ADX
def adx_indicator(data):
    data['Adj Open'] = data.Open * data['Adj Close']/data['Close']
    data['Adj High'] = data.High * data['Adj Close']/data['Close']
    data['Adj Low'] = data.Low * data['Adj Close']/data['Close']
    data.dropna(inplace=True)

    adxI = ADXIndicator(data['Adj High'],data['Adj Low'],data['Adj Close'],14,False)
    data['pos_directional_indicator'] = adxI.adx_pos()
    data['neg_directional_indicator'] = adxI.adx_neg()
    data['adx'] = adxI.adx()
    data['di_pos'] = adxI.adx_pos()
    data['di_neg'] = adxI.adx_neg()
    #print(data['di_neg'])
    data['trend_signal'] = np.where(data['adx']>25,1,0)
    data['adx_indicator'] = np.where((data['adx']>=25) & (data['di_pos'] >= data['di_neg']),1,0)
    return data

#returns ddiscrete derivative
def dx(vector):
    temp = np.zeros(len(vector))
    for i in range(1,len(vector)):
        temp[i] = vector[i]-vector[i-1]
    return temp

#inputs: - yfinance dataframe
#        - vector of weights for indicators: [rsi adx ttm macd vix]
def buysell(data,weights):
    sum = np.zeros(len(data))
    for i in range(0,len(data)):
        sum[i] = weights[0]*data.iloc[i,9] + weights[1]*data.iloc[i,28] + weights[2]*data.iloc[i,18] + weights[3]*data.iloc[i,7] + weights[4]*data.iloc[i,30]
    data['overall_indicator'] = sum
    return sum

def backtesting(data,weights,start_balance,buy,sell):
    start_index = data.index.get_loc('2021-02-08')
    vix_index = data.columns.get_loc('vix_indicator')
    cash_value = np.zeros(len(data))
    stock_shares = np.zeros(len(data))
    stock_value = np.zeros(len(data))
    total_value = np.zeros(len(data))
    cash_value[0:start_index] = np.ones(start_index)*start_balance
    total_value[0:start_index] = np.ones(start_index)*start_balance
    indicator = buysell(data,weights)
    returns = np.zeros(len(data))
    indicator_idx = data.columns.get_loc('overall_indicator')
    close_idx = data.columns.get_loc('Close')

    for i in range(start_index,len(data)):
        if (data.iloc[i,indicator_idx] >= buy) and (cash_value[i-1] > 0) and (data.iloc[i,vix_index]>0):
            #print('triggered buy')
            stock_shares[i] = cash_value[i-1]/data.iloc[i,close_idx]
            stock_value[i] = stock_shares[i]*data.iloc[i,close_idx]
            cash_value[i] = 0
            total_value[i] = cash_value[i] + stock_value[i]
            returns[i] = (total_value[i] - start_balance)/start_balance
            #print('cash: ',cash_value[i])
            #print('stock: ',stock_value[i])

        elif (data.iloc[i,indicator_idx] == sell) and (stock_value[i-1] > 0):
            #print('triggered sell')
            cash_value[i] = stock_shares[i-1] * data.iloc[i,close_idx] + cash_value[i-1]
            stock_shares[i] = 0
            stock_value[i] = stock_shares[i]*data.iloc[i,close_idx]
            total_value[i] = cash_value[i] + stock_value[i]
            returns[i] = (total_value[i] - start_balance)/start_balance
            #print('cash: ',cash_value[i])
            #print('stock: ',stock_value[i])
        else:
            #print('triggered hold')
            stock_shares[i] = stock_shares[i-1]
            cash_value[i] = cash_value[i-1]
            stock_value[i] = stock_shares[i]*data.iloc[i,close_idx]
            total_value[i] = cash_value[i] + stock_value[i]
            returns[i] = (total_value[i] - start_balance)/start_balance
            #print('cash: ',cash_value[i])
            #print('stock: ',stock_value[i])

    data['cash_balance'] = cash_value
    data['shares'] = stock_shares
    data['total_balance'] = total_value
    data['returns'] = returns
    return data['returns'].iloc[-1]
