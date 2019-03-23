# -*- coding: utf-8 -*-
"""
Created on Mon Sep 12 17:08:06 2016

@author: Guanwen
"""

import requests

import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
import logging
import json
from pandas.io.json import json_normalize

import pandas as pd
#http://developer.oanda.com/rest-live/rates/#getCurrentPrices


#start = '2011-09-18'


start = '2015-01-01'
today = '2019-01-20'
#today = str(date.today())

'''pairs = ["AUD_USD", "USD_CAD", "EUR_CHF", "USD_CNH", "EUR_CZK", "EUR_USD", "GBP_USD", "EUR_HUF", "USD_INR",
         "USD_JPY", "USD_MXN", "NZD_USD", "EUR_PLN", "USD_SGD", "USD_THB", "USD_TRY", "GBP_HKD", "USD_ZAR",
         "XAG_USD", "XAU_USD"]'''
         
pairs = ["AUD_USD", "NZD_USD", "USD_CAD", "EUR_USD", "GBP_USD", "USD_JPY"]
#pairs = ["USD_ZAR", "USD_MXN", "USD_SGD", "USD_INR", "USD_THB", "USD_TRY"]
#pairs = ["XAG_USD", "XAU_USD", "USD_CNH", 'TWD_USD']
#pairs = ['USD_CHF', 'USD_CZK', 'USD_HUF', 'USD_PLN', , 'USD_CHY']        


date_range_index = pd.date_range(start, today,  freq='15min')
raw_data = pd.DataFrame(index=date_range_index)

domain = "https://api-fxtrade.oanda.com/"
access_token = 'c3c619b83a1f631c1f2f6ce18b8304ed-f0c89f28c64d1e0561b07b9fd3f00903'
account_id = '5640873'

price_type = "v1/candles"
candleFormat = "bidask" #bidask or midpoint
granularity = "M15"   #15 min
dailyAlignment = "17"
alignmentTimezone = "America/New_York"

logger = logging.getLogger(__name__)
requests.packages.urllib3.disable_warnings()
s = requests.Session()
url = domain + price_type
headers = {'Authorization' : 'Bearer ' + access_token}

date_monthly = pd.date_range(start, today,  freq='MS') #oanda can only response 5000 rows each time



for pair in pairs:
    try:
        close_data = pd.DataFrame()
    
        for month in date_monthly:
            date_start = str(month.date())
            date_end = str((month + relativedelta(months=1) - datetime.timedelta(1)).date())
           
            #params = {'accountId' : account_id, 'instrument' : pair, 'start' : start, 'end' : today, "candleFormat" : candleFormat,
                #"granularity" : granularity, "dailyAlignment" : dailyAlignment, "alignmentTimezone" : alignmentTimezone} 
            params = {'accountId' : account_id, 'instrument' : pair, 'start' : date_start, 'end' : date_end, "candleFormat" : candleFormat,
                "granularity" : granularity}    
            req = requests.Request('GET', url, headers = headers, params=params)
            pre = req.prepare()
            response = s.send(pre, stream=True, verify=False)
            
            json_data = json.loads(response.text)
            candles = json_data['candles']
            data = json_normalize(candles)
            data['date'] = pd.to_datetime(data['time'])
            #data['date'] = data['date'].map(lambda x: x.date())  #if frequency is daily
            data.set_index('date', inplace=True)
            data = data[['closeAsk', 'closeBid']]   #closeMid, closeAsk, closeBid
            close_data = pd.concat([close_data, data])
            #close_data['spread'] = close_data[pair+'_Ask'] - close_data[pair+'_Bid']
        
        
        close_data.columns = [pair+'_Ask', pair+'_Bid']
        raw_data = raw_data.join(close_data)
    except Exception as e:
        print(e)

#Xrate_data = raw_data[:-1].copy()
Xrate = raw_data.dropna(how='any')
Xrate.to_csv(r'C:\Users\Guanwen\Desktop\Xrate_' + str(today) + '.csv')
        
        
        
        
        
        
        
        
        
        
        
        
        
    