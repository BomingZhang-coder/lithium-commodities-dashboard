import pandas as pd
import json


'''
up_company_listed.csv comes from Up_yf_listed sheet of 
https://docs.google.com/spreadsheets/d/1L1Kuh0J6FqF-_S0torGGPDLqc2de1GL8JWcKQHSb7AU/edit#gid=201493030

Output company_product.json with mining company as key, products as values
Output product_company.json with products as key, mining companies as values
'''

df = pd.read_csv('danyang/Data/up_company_listed.csv')[['Stock_EOD','Product']]
comp = df['Stock_EOD'].to_list()
df['Product'] = df['Product'].str.split(', ')
prod = df['Product'].to_list()

 # Companies as key, product lists as value 
comp_prod = {i[0]:i[1] for i in list(zip(comp,prod))}

with open('danyang/Data/up_company_product.json', 'w') as outfile:
    json.dump(comp_prod, outfile)
outfile.close()


# Products as keys, company lists as value
prod_comp = {prod: [] for prod in ['Brine','Spodumene','Lithium Porcelain Ore']} 

for prod in prod_comp.keys():
    for stock in comp_prod.keys():
        if prod in comp_prod[stock]:
            prod_comp[prod].append(stock)

with open('danyang/Data/up_product_company.json', 'w') as outfile:
    json.dump(prod_comp, outfile)