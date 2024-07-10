import numpy as np
import pandas as pd
import re
import os

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer
from newspaper import Article
import contractions
from textblob import TextBlob

from multiprocessing import  Pool



######################
### Load News Data ###
######################

data_dir = f"{os.path.dirname(__file__)}/lithium_dataset"
cleaned_data_dir = f"{os.path.dirname(__file__)}/lithium_dataset/cleaned_data"

news = pd.read_csv(f'{data_dir}/lithium_merged.csv')
news.set_index('DATE', inplace=True)
news.index = pd.to_datetime(news.index, format = '%Y%m%d%H%M%S')
news = news.sort_index(ascending = True)['2017-05-02':]
news = news[['DocumentIdentifier', 'V2Tone']].rename(columns={'DocumentIdentifier': 'url', 'V2Tone': 'tone'})

# print(news)


#####################
### Load Keywords ###
#####################

up_key1=['lithium-ore', 'nickel', 'cobalt','lithium-future','lithium-mining-companies', 'nickel-futures',
        'spodumene', 'spodumenite','lithium-market-share', 'cobalt-oxide', 'nickel-index', 'lithium-ore-reserves',
        'lithium-etf','lithium-index','lithium-concentration', 'industry-grade','battery-grade', 'li2co3', 'li-oh','lioh','lithium-mangnate',
        'lithium-iron-phosphate', 'ternary-materials', 'lithium-refining','lithium-carbonate','lithium-hydroxide','lithium-production']
up_key=up_key1

down_key1=['ev-car','electric-battery','lithium-battery', 'ev-car-subsidy','battery-subsidy', 'ev-company', 'ev-sales', 'ev-tax-credit','battery-tax-credit',
          'storage', 'lfp-battery','lithium-battery-companies','price-of-li-ion-battery','ternary-lithium-battery']
down_key=down_key1

for space in ["+","_","%20"," "]:
    up_key2=[sub.replace("-",space) for sub in up_key1]
    up_key=up_key+up_key2
    down_key2=[sub.replace("-",space) for sub in down_key1]
    down_key=down_key+down_key2

up_key=list(set(up_key))
down_key=list(set(down_key))



###########################
### Search for Keywords ###
###########################

lemmatizer = WordNetLemmatizer()

def process_text(text):
    text = contractions.fix(text)
    text = text.lower()
    text = re.sub('\n', ' ', text)
    text = re.sub('\s+', ' ', text).strip()
    return text

def match_keyword(url, keywords):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()
        res = {
            'title': process_text(article.title),
            'text': process_text(article.text),
            'summary': process_text(article.summary),
            'keywords': article.keywords,
        }
    
        for item in ['title', 'text', 'summary']:
            for kw in keywords:
                if lemmatizer.lemmatize(kw) in res[item]:
                    return True
        
        for item in res['keywords']:
            for kw in keywords:
                if lemmatizer.lemmatize(kw) in item:
                    return True
            
        return False
    
    except:
        return '1'
    
def add_categories(df):
    df['upstream'] = df['url'].apply(lambda x: match_keyword(x, up_key))
    df['downstream'] = df['url'].apply(lambda x: match_keyword(x, down_key))
    return df

def parallelize_dataframe(df, func, n_cores=4):
    df_split = np.array_split(df, n_cores)
    pool = Pool(n_cores)
    df = pd.concat(pool.map(func, df_split))
    pool.close()
    pool.join()
    return df


if __name__ == '__main__':

    news1 = news.copy()
    news1 = parallelize_dataframe(news1, add_categories)
    print(news1)
    news1.to_csv(f'{cleaned_data_dir}/news_cat_cleaned.csv')