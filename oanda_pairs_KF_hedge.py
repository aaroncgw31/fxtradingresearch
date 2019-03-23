# -*- coding: utf-8 -*-
"""
Created on Tue Sep 26 11:08:08 2017

@author: Guanwen
"""

from oandapy import oandapy
import numpy as np
import time
import pandas as pd



domain = "https://api-fxtrade.oanda.com/"
token = 'c3c619b83a1f631c1f2f6ce18b8304ed-f0c89f28c64d1e0561b07b9fd3f00903'
account_id = '5640873'
filename = 'KF_Params.csv'

oanda = oandapy.API(environment="practice", access_token=token)
positions = False

inti_params = pd.DataFrame.from_csv(filename)

G0 = np.matrix(np.eye(2))
W0 = np.matrix(np.eye(2)) * 0.00000001
Vdelta = 0.98

C0 = np.matrix([[0.7843, -0.6350], [-0.6350, 0.5147]]) * 0.0001
m0 = np.matrix([0.5625, 0.3403]).T
d0 = 1.2675e-05
n0 = 50
S0 = d0/n0



while(True):

    response = oanda.get_prices(instruments="USD_CAD")
    USD_CAD_ASK = response.get("prices")[0].get("ask")
    USD_CAD_BID = response.get("prices")[0].get("bid")
    CAD_USD_MID = ((1 / USD_CAD_ASK) + (1 / USD_CAD_BID)) / 2
    
    response = oanda.get_prices(instruments="AUD_USD")
    AUD_USD_ASK = response.get("prices")[0].get("ask")
    AUD_USD_BID = response.get("prices")[0].get("bid")
    AUD_USD_MID = (AUD_USD_ASK + AUD_USD_BID) / 2
    
    
    Y = AUD_USD_MID
    X = np.matrix([CAD_USD_MID, 1]).T
    
    
    a = G0 * m0               #Prior mean for system equation parameters
    R = G0*C0*G0.T + W0       #Variance for prior mean for system equation parameters
    f = X.T*m0                #One step ahead forecast
    Q = X.T*R*X   +  S0       #One step ahead forecast variance
    e = Y - f                 #Forecast error
    n = Vdelta*n0 + 1         #Degrees of freedom
    d = Vdelta*d0 + (S0*e*e)/Q
    S = d/n                   #Posterior estimate of unknown variance V(t)
    
    A = (R*X) / Q             #Adaptive vector (Kalman gain
    m = a + A*e               #Posterior mean for system equation parameters
    C = (S/S0)[0,0]*(R- A*(A.T)*Q[0,0])  #Posterior variance for system equation parameters
    
    S0 = S;
    C0 = C;
    m0 = m;
    n0 = n;
    d0 = d;
    
    AUD_Position = 100000
    CAD_Position = int(AUD_Position * m[0,0])
    
    spread = e[0,0]
    spread_f = np.sqrt(Q)[0,0]
    
    if positions is False and spread < spread_f:
        response = oanda.create_order(account_id, instrument="AUD_USD", units=AUD_Position, side='buy',type='market')
        response = oanda.create_order(account_id, instrument="USD_CAD", units=CAD_Position, side='buy',type='market')
        positions = True
        print("Buy " + response['time'])
    elif positions and spread > 0:
        response = oanda.close_position(account_id, instrument="AUD_USD")
        response = oanda.close_position(account_id, instrument="USD_CAD")
        positions = False
        print("CloseBuy " + response['time'])
    elif positions is False and spread > spread_f:
        response = oanda.create_order(account_id, instrument="AUD_USD", units=AUD_Position, side='sell',type='market')
        response = oanda.create_order(account_id, instrument="USD_CAD", units=CAD_Position, side='sell',type='market')
        positions = True
        print("Sell " + response['time'])
    elif spread < 0:
        response = oanda.close_position(account_id, instrument="AUD_USD")
        response = oanda.close_position(account_id, instrument="USD_CAD")
        positions = False
        print("CloseSell " + response['time'])
        
    
    params = pd.DataFrame([G0, W0, C0, m0, n0, d0])
    params.to_csv(filename)    

        
    
    time.sleep(900)























