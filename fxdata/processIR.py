# -*- coding: utf-8 -*-
"""
Created on Fri Sep 16 15:53:20 2016

@author: Guanwen
"""

#https://www.oanda.com/forex-trading/analysis/historical-rates

import pandas as pd
import numpy as np

from datetime import date
import datetime

#start = datetime.date(2011, 9 , 18)
start = datetime.date(2009, 1, 1)
today = date.today()
date_range = pd.date_range(start, today)
Irate_data = pd.DataFrame(index=date_range)


data = pd.read_csv(r'C:\Users\Guanwen\Desktop\IR.csv')

data['DATE'] = pd.to_datetime(data['DATE'])
data['DATE'] = data['DATE'].map(lambda x: x.date())



currencies = np.unique(data['CURRENCY'])
#count = np.count_nonzero(currencies)

for currency in currencies:
    raw_data = pd.DataFrame(index=date_range)
    
    c_data = data[data['CURRENCY'] == currency][['BID', 'ASK', 'DATE']]
    c_data = c_data.drop_duplicates(subset='DATE')
    #c_data[currency] = (c_data['BID'] + c_data['ASK']) / 2     
    c_data.columns = [currency+'_BID', currency+'_ASK', 'DATE']
    c_data.set_index('DATE', inplace=True)
    #c_data = c_data[currency]    
    c_data = c_data.sort_index()
    
    begin_IR = c_data[c_data.index < start].tail(1)
    raw_data = raw_data.join(c_data, how='left')
    raw_data.iloc[0] = begin_IR.iloc[0]
    raw_data = raw_data.fillna(method='ffill')
    
    Irate_data = Irate_data.join(raw_data)

Irate_data = Irate_data / 100

col = list()

for currency in currencies:
    if currency is not 'USD':
        Irate_data[currency + '/USD'] = Irate_data[currency + '_BID'] - Irate_data['USD_ASK']
        Irate_data['USD/' + currency] = Irate_data['USD_BID'] - Irate_data[currency + '_ASK']
        col.append(currency + '/USD')
        col.append('USD/' + currency)
        
#Irate_data = Irate_data[['AUD/USD', 'USD/AUD']]        

#Irate_data['EUR/USD'] = Irate_data['EUR_BID'] - Irate_data['USD_ASK']
#Irate_data['USD/EUR'] = Irate_data['USD_BID'] - Irate_data['EUR_ASK']
    
#data = Xrate_data.join(Irate_data)

#Irate_data.to_csv(r'C:\Users\Guanwen\Google Drive\Strategies\Other\Forex\Irate_' + str(today) + '.csv')
#data.to_csv(r'C:\Users\Guanwen\Google Drive\Strategies\Other\Forex\data_' + str(today) + '.csv')

















