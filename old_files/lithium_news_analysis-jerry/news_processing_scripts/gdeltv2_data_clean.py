import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time
import os
import sys

sys.setrecursionlimit(10000)

curdir = os.path.dirname(__file__)



# Clean tables by matching organization names

df = pd.read_pickle(f'{curdir}/eod_dict.pickle')
company_dict = {}
for key,value in df.items():
    key_temp=key.replace(',',' ')
    company_dict[key_temp.lower()] = value.lower()
company_key = list(company_dict.keys())
company_key1=','.join(company_key)

df_theme = pd.read_pickle(f'{curdir}/theme_sdg_mapping.pk')
themes = list(df_theme.keys())

redundant = ['co', 'plc', 'ltd', '&', 'inc', 'company', 'corp', 'corporation']



def clean_bot(x):
    """
    The actual robot which is gonna clean the company suffix for every company.
    :type x: str
    :rtype: str
    """
    if len(x) > 0 and x[-1] in redundant:
        del x[-1]
        clean_bot(x)
    return x

def clean(x):
    """
    Clean all the organizations from the 'Organizations' column in the raw data file.
    The data type of every entry in the 'Organizations' column is string.
    :type x: str
    :rtype: list
    """
    x = x.split(';')
    temp = list()
    for y in x:
        y = y.split(' ')
        temp.append(clean_bot(y))
    return temp

nations = set(['afghanistan', 'albania', 'algeria', 'america', 'andorra', 'angola', 'antigua', 'argentina', 'armenia',
               'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain', 'bangladesh', 'barbados', 'belarus',
               'belgium', 'belize', 'benin', 'bhutan', 'bissau', 'bolivia', 'bosnia', 'botswana', 'brazil', 'british',
               'brunei', 'bulgaria', 'burkina', 'burma', 'burundi', 'cambodia', 'cameroon', 'canada', 'cape verde',
               'central african republic', 'chad', 'chile', 'china', 'colombia', 'comoros', 'congo', 'costa rica',
               'country debt', 'croatia', 'cuba', 'cyprus', 'czech', 'denmark', 'djibouti', 'dominica', 'east timor',
               'ecuador', 'egypt', 'el salvador', 'emirate', 'england', 'eritrea', 'estonia', 'ethiopia', 'fiji',
               'finland', 'france', 'gabon', 'gambia', 'georgia', 'germany', 'ghana', 'great britain', 'greece',
               'grenada', 'grenadines', 'guatemala', 'guinea', 'guyana', 'haiti', 'herzegovina', 'honduras', 'hungary',
               'iceland', 'in usa', 'india', 'indonesia', 'iran', 'iraq', 'ireland', 'israel', 'italy', 'ivory coast',
               'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati', 'korea', 'kosovo', 'kuwait',
               'kyrgyzstan', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya', 'liechtenstein', 'lithuania',
               'luxembourg', 'macedonia', 'madagascar', 'malawi', 'malaysia', 'maldives', 'mali', 'malta', 'marshall',
               'mauritania', 'mauritius', 'mexico', 'micronesia', 'moldova', 'monaco', 'mongolia', 'montenegro',
               'morocco', 'mozambique', 'myanmar', 'namibia', 'nauru', 'nepal', 'netherlands', 'new zealand',
               'nicaragua', 'niger', 'nigeria', 'norway', 'oman', 'pakistan', 'palau', 'panama', 'papua', 'paraguay',
               'peru', 'philippines', 'poland', 'portugal', 'qatar', 'romania', 'russia', 'rwanda', 'saint kitts',
               'samoa', 'san marino', 'santa lucia', 'sao tome', 'saudi arabia', 'scotland', 'scottish', 'senegal',
               'serbia', 'seychelles', 'sierra leone', 'singapore', 'slovakia', 'slovenia', 'solomon', 'somalia',
               'south africa', 'south sudan', 'spain', 'sri lanka', 'st kitts', 'st lucia', 'st. kitts', 'st. lucia',
               'sudan', 'suriname', 'swaziland', 'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan', 'tanzania',
               'thailand', 'tobago', 'togo', 'tonga', 'trinidad', 'tunisia', 'turkey', 'turkmenistan', 'tuvalu',
               'uganda', 'ukraine', 'united kingdom', 'united states', 'uruguay', 'usa', 'uzbekistan', 'vanuatu',
               'vatican', 'venezuela', 'vietnam', 'wales', 'welsh', 'yemen', 'zambia', 'zimbabwe'])

def del_countries(x):
    """
    Delete the strings which are names of countries in every entry from the 'Organizations' column.
    :type: list (list of lists)
    :rtype: list (list of lists)
    """
    x = [k for k in x if ' '.join(k).lower() not in nations]
    return x

def find_index(corp_name, middle_index, company_key1):
    """
    Precisely find the index of the objective string (company name) by setting ',' as delimiter and loop the string.
    Return the index if found, return -1 if not found.
    :type: string, int, string
    :rtype: int
    """
    middle2 = company_key1[middle_index:].find(corp_name)
    if middle2 == -1:
        return middle2
    elif middle2 == 0:
        return middle2
    elif company_key1[middle2 + middle_index - 1] == ',':
        return middle2 + middle_index
    else:
        index1 = company_key1[middle2 + middle_index:].find(',')
        if index1 == -1:
            return -1
        count1 = middle2 + middle_index + index1
        return find_index(corp_name, count1, company_key1)

def company_matching(x, company_key1, company_dict):
    """
    Match the objective string (company name) and return a list of found companies.
    :type: list (list of lists)
    :type company_key1: string
    :type company_dict: dictionary
    :rtype: list
    """
    x1 = [' '.join(y) for y in x]
    childs = list()
    for i in x1:
        head_index = find_index(i, 0, company_key1)

        if head_index == -1:
            continue
        else:
            if company_key1[head_index:].find(',') == -1:
                childs.append(company_key1[head_index:])
            else:
                childs.append(company_key1[head_index:head_index + company_key1[head_index:].find(',')])

    if len(childs) == 0:
        return np.nan

    else:
        return childs

def return_first_v2tone_score(x):
    """
    Return the first numerical value of a string in an entry of V2Tone column from raw data file.
    :type: string
    :rtype: float
    """
    # l = x.split(',')
    return float(x.split(',')[0])

def clean_raw_data(data):

    news_clean = data[['DATE', 'SourceCommonName', 'DocumentIdentifier', 'V2Tone', 'Themes', 'V2Organizations']]        

    # # Drop missing value for org and themes; drop duplicate value for V2Tone(there are duplicate news which can affect our research performance)
    # news_clean = news[~news['Organizations'].isna()]
    # news_clean = news_clean[~news_clean['Themes'].isna()]

    # # print('Cleaning corp...')
    # index = news_clean['Organizations'].apply(lambda x: clean(x))
    # news_clean['Organizations'] = index

    # # print('Cleaning countries...')
    # index = news_clean['Organizations'].apply(del_countries)
    # news_clean['Organizations'] = index

    # # print('Matching companies...')
    # index = news_clean['Organizations'].apply(lambda x: company_matching(x, company_key1, company_dict))
    # news_clean['Organizations'] = index

    # # Drop missing values
    # news_clean = news_clean.loc[index[~index.isnull()].index]

    # # Drop duplicates based on tone,themes,organization
    # news_clean['Organizations'] = news_clean['Organizations'].apply(lambda x: ','.join(x))
    # news_clean = news_clean.drop_duplicates(subset=['V2Tone', 'Themes', 'Organizations'], keep='first')
    # news_clean['Organizations'] = news_clean['Organizations'].apply(lambda x: x.split(','))

    # Return the first value in each entry from v2tone column
    news_clean.loc[:,'V2Tone'] = news_clean['V2Tone'].apply(lambda x: return_first_v2tone_score(x))

    # Sort by date
    news_clean = news_clean.sort_values(by=['DATE'], ascending=False)

    return news_clean


def process_theme(news_clean):

    final_themes = []
    news_clean['Themes'] = news_clean['Themes'].fillna('')
    col_themes = news_clean['Themes'].str.split(';')
    for i in range(len(news_clean['Themes'])):
        needed_themes = []
        row_themes = col_themes.iloc[i]
        for j in row_themes:
            if j in themes:
                needed_themes.append(j)
        final_themes.append(needed_themes)
    
    news_clean.loc[:,'FinalThemes'] = final_themes
    news_clean.loc[:,'FinalThemes'] = [','.join(map(str, l)) for l in news_clean['FinalThemes']]
    news_clean.loc[:,'FinalThemes'] = news_clean['FinalThemes'].replace(r'^\s*$', np.nan, regex=True)
    # news_clean = news_clean[news_clean['FinalThemes'].notna()]

    return news_clean


def combine_raw_data():
    def preprocess_data(filename):
        df = pd.read_csv(filename)
        df['DATE'] = pd.to_datetime(df['DATE'], format = '%Y%m%d%H%M%S')
        df.set_index('DATE', inplace=True)
        return df

    filenames = [f'{curdir}../GDELT_lithium_news/{t}_raw.csv' for t in ['2016-2018', '2018-2020', '2020-2023', '2023']]
    combined = []
    for f in filenames:
        df = preprocess_data(f)
        combined.append(df)

    combined_df = pd.concat(combined)
    combined_df = combined_df.sort_index(ascending = True).drop(columns=['Dates'])
    combined_df.to_csv(f"{curdir}../GDELT_lithium_news/combined_raw.csv")


def pipeline(df):
    df_ = clean_raw_data(df)
    df_ = process_theme(df_)
    return df_


if __name__ == '__main__':

    # combine_raw_data()

    break1 = time.time()
    df = pd.read_csv(f"{curdir}../GDELT_lithium_news/lithium_news_raw.csv", on_bad_lines='skip', dtype="string", encoding = "ISO-8859-1")
    df_clean = pipeline(df)    
    print(df_clean)
    break2 = time.time()
    print(f"Total processing time: {round(break2-break1,2)} seconds")
    df_clean.to_csv(f"{curdir}../GDELT_lithium_news/lithium_news_clean.csv")