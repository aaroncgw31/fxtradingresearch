# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 15:18:58 2017

@author: Guanwen
"""

#https://github.com/oanda/oandapy
#http://developer.oanda.com/rest-live/rates/#getCurrentPrices

import oandapy
import csv

import datetime

import pandas as pd

from getHistPrices import getHistPrices
from johansen import coint_johansen, print_johan_stats


domain = "https://api-fxtrade.oanda.com/"
token = 'c3c619b83a1f631c1f2f6ce18b8304ed-f0c89f28c64d1e0561b07b9fd3f00903'
account_id = '5640873'

oanda = oandapy.API(environment="practice", access_token=token)

trainlen = 96
lookback = 8

filename = 'data.csv'

initial_prices_CAD = 1 / getHistPrices('USD_CAD', trainlen) 
initial_prices_AUD = getHistPrices('AUD_USD', trainlen) 

initial_prices = pd.DataFrame(zip(initial_prices_CAD, initial_prices_AUD), columns=['CAD_USD', 'AUD_USD'])
initial_prices.to_csv(filename, index=False)

res = coint_johansen(initial_prices[['CAD_USD','AUD_USD']], 0, 1)
initial_prices['yport'] = initial_prices['CAD_USD'] * res.evec[0][0] + initial_prices['AUD_USD'] * res.evec[1][0]
ma = initial_prices['yport'][-lookback:].mean()
mstd = initial_prices['yport'][-lookback:].std()

zscore = (float(initial_prices['yport'].tail(1)) - ma) / mstd

#print_johan_stats(res)

   

response = oanda.get_prices(instruments="USD_CAD")
USD_CAD_ASK = response.get("prices")[0].get("ask")
USD_CAD_BID = response.get("prices")[0].get("bid")
CAD_USD_MID = ((1 / USD_CAD_ASK) + (1 / USD_CAD_BID)) / 2

response = oanda.get_prices(instruments="AUD_USD")
AUD_USD_ASK = response.get("prices")[0].get("ask")
AUD_USD_BID = response.get("prices")[0].get("bid")
AUD_USD_MID = (AUD_USD_ASK + AUD_USD_BID) / 2

current_price = [CAD_USD_MID, AUD_USD_MID]

with open('data.csv', 'a') as myfile:
    wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
    wr.writerow(current_price)
    