import pandas as pd
import yfinance as yf

'''
up_company_listed.csv comes from Up_yf_listed sheet of 
https://docs.google.com/spreadsheets/d/1L1Kuh0J6FqF-_S0torGGPDLqc2de1GL8JWcKQHSb7AU/edit#gid=201493030

Output comp_info_yf.csv company information with column Stock, Stock_EOD, Name, Product, Currency, 
and latest market cap (CNY) adjusted by most recent to CNY exchange rate
'''

df = pd.read_csv('danyang/Data/up_company_listed.csv', usecols = [0,1,2,4])
# df['Exchange'] = df.apply(lambda x: (yf.Ticker(x['Stock']).info['exchange']), axis = 1) 
df['Currency'] = df.apply(lambda x: (yf.Ticker(x['Stock']).info['currency']), axis = 1)
# df['Time Zone'] = df.apply(lambda x: (yf.Ticker(x['Stock']).info['timeZoneShortName']), axis = 1)
def get_adjusted_mc(stock):
    ticker = yf.Ticker(stock)
    currency = ticker.info['currency']
    marketCap = ticker.info['marketCap']
    
    if currency != 'CNY':
        exchange_rate = yf.Ticker(currency+'CNY=X').info['previousClose']
        return exchange_rate * marketCap
    return marketCap

df['Market Cap CNY'] = df.apply(lambda x: round(get_adjusted_mc(x['Stock']) / 1000000, 4), axis = 1)
df.to_csv('danyang/Data/up_comp_info_yf.csv')