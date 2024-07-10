import csv
import urllib.request, json
import pandas as pd
from eod import EodHistoricalData
import pandas as pd

'''
up_company_listed.csv comes from Up_yf_listed sheet of 
https://docs.google.com/spreadsheets/d/1L1Kuh0J6FqF-_S0torGGPDLqc2de1GL8JWcKQHSb7AU/edit#gid=201493030

Output merged dataframe of outstandingShares of each tickers based on years
'''

file = open('danyang/Data/up_company_listed.csv','r')
data = list(csv.reader(file))
tickers = [(row[0],row[1]) for row in data][1:]



end_date = '2023-05-22' # Wind database data stops at this date
api_key = '5f3afd582bd7b4.95720069'
api = EodHistoricalData(api_key)

def get_outstandingShares(ticker): 
    # get outstandingShares of a single ticker in million
    url = f"https://eodhistoricaldata.com/api/fundamentals/{ticker}?api_token={api_key}&order=d&fmt=json"

    response = urllib.request.urlopen(url, timeout=5)
    data = json.loads(response.read())

    outstandingShares = {}
    for val in data['outstandingShares']['annual'].values():
        outstandingShares[val['date']] = val['sharesMln']
    df_os = pd.DataFrame.from_dict(outstandingShares, orient = 'index', columns=[f'{ticker}'])
    
    return df_os

def merge_outstanding(tickers): 
    # get merged dataframe of outstandingShares based on years
    df = get_outstandingShares(tickers[0][1])
    for ticker in tickers[1:]:
        df = df.join(get_outstandingShares(ticker[1]), how='outer')
    return df

outstandingShares = merge_outstanding(tickers)
outstandingShares.to_csv('danyang/Data/up_outstandingShares.csv')