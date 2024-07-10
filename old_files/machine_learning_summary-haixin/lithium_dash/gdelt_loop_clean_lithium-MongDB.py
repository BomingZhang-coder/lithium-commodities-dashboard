import pandas as pd
import pandas as pd
import requests
import zipfile
import numpy as np
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import shutil
import os
import sys

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

sys.setrecursionlimit(10000)

curdir = os.path.dirname(__file__).replace("\\","/")
time_interval = 1  # Total number of hours we want to look back into
mongodb_account = 'quantumgaihold'
mongodb_password = 'ZBYamTQ4EMDVgKl5'


#######################################
### Establish connection to MongoDB ###
#######################################
uri = "mongodb+srv://" + mongodb_account + ":" + mongodb_password + "@cluster0.etjr4e4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))             
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client.lithiumdash # MongoDB database name
collection_lithium_15 = db.lithium_data_15
collection_lithium_map_15=db.lithium_map_15

### First clear all existing data to ensure that all data are up-to-date
collection_lithium_15.delete_many({})
collection_lithium_map_15.delete_many({})
print("Removed outdated data from MongoDB\n")

# get current date and time
now = datetime.now(timezone.utc)
t = now.strftime("%D,%H,%M,%S")
t = t.split(",")
t[0] = t[0].split("/")

# round to nearest 15 minutes
# decide first date of range based on closest time interval
if ( int(t[2]) >= 0 ) & ( int(t[2]) < 15 ):
    m = '00'
elif ( int(t[2]) >= 15 ) & ( int(t[2]) < 30 ):
    m = '15'
elif ( int(t[2]) >= 30 ) & ( int(t[2]) < 45 ):
    m = '30'
elif ( int(t[2]) >= 45 ):
    m = '45'

#date1 = '20230101000000'
date = '20' + t[0][2] + t[0][0] + t[0][1] + t[1] + m + '00'
date = datetime.strptime(date, '%Y%m%d%H%M%S')

def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

news_all= pd.DataFrame()
download_path='C:/Users/18045/Downloads/lithium-dash-main-stephen/'
print("Downloading and assembling data begin ...")
num_hrs=6
lithium_preprocessing=pd.DataFrame([])

while len(lithium_preprocessing)==0:
    for i in range(4*num_hrs):    # 4* #of hrs

        offset = i*15
        l = date - timedelta(minutes=offset)
        l = l.strftime("%D,%H,%M,%S")
        l = l.split(",")
        l[0] = l[0].split("/")

        dateN = '20' + l[0][2] + l[0][0] + l[0][1] + l[1] + l[2] + '00'

        url = 'http://data.gdeltproject.org/gdeltv2/' + dateN + '.gkg.csv.zip'

        # get filename
        name = url.split("/")
        name = name[-1]
        names = name.split(".")

        # download and unzip file
        download_url(url, curdir + '/data/' + name)
        with zipfile.ZipFile(curdir + '/data/' + name, 'r') as zip_ref:
            zip_ref.extractall(curdir + '/data/' + names[0])

        # assemble table
        news = pd.read_csv(curdir + '/data/' + names[0] + '/' + names[0] + "." + names[1] + "." + names[2], on_bad_lines='skip', delimiter="\t", names=["GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName", "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes", "Locations", "V2Locations", "Persons", "V2Persons", "Organizations", "V2Organizations", "V2Tone", "Dates", "GCAM", "SharingImage", "RelatedImages", "SocialImageEmbeds", "SocialVideoEmbeds", "Quotations", "AllNames", "Amounts", "TranslationInfo", "Extras"], dtype="string", encoding = "ISO-8859-1")

        if i==0:
            news_15 = pd.DataFrame(news)
        
        news_all = pd.concat([news_all, news])
        lithium_preprocessing = news_all[news_all['DocumentIdentifier'].str.contains('lithium')]
        lithium_preprocessing=lithium_preprocessing.dropna(subset=['DocumentIdentifier','SourceCommonName','V2Locations','Organizations'])
        os.remove(curdir + '/data/' + name)
        shutil.rmtree(curdir + '/data/' + names[0])
    num_hrs=num_hrs+1


print("Downloading and assembling data finished.")
print("-----------------------------------------")

# Clean tables by matching organization names
print("Begin cleaning tables by matching organization names ...")

df = pd.read_pickle('eod_dict.pickle')
company_dict = {}
for key,value in df.items():
    key_temp=key.replace(',',' ')
    company_dict[key_temp.lower()] = value.lower()
company_key = list(company_dict.keys())
company_key1=','.join(company_key)

df_theme = pd.read_pickle('theme_sdg_mapping.pk')
themes = list(df_theme.keys())

redundant = ['co', 'plc', 'ltd', '&', 'inc', 'company', 'corp', 'corporation']
print("Finished cleaning.")
print("-----------------------------------------")

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
    news = data[['DATE', 'DocumentIdentifier', 'V2Tone', 'Themes', 'Organizations']]          # maybe don't need to drop missing org
    # Drop missing value for org and themes; drop duplicate value for V2Tone(there are duplicate news which can affect our research performance)
    news_clean = news[~news['Organizations'].isna()]
    news_clean = news_clean[~news_clean['Themes'].isna()]

    # print('Cleaning corp...')
    index = news_clean['Organizations'].apply(lambda x: clean(x))
    news_clean['Organizations'] = index

    # print('Cleaning countries...')
    index = news_clean['Organizations'].apply(del_countries)
    news_clean['Organizations'] = index

    # print('Matching companies...')
    index = news_clean['Organizations'].apply(lambda x: company_matching(x, company_key1, company_dict))
    news_clean['Organizations'] = index
    # Drop missing values
    news_clean = news_clean.loc[index[~index.isnull()].index]
    # Drop duplicates based on tone,themes,organization
    news_clean['Organizations'] = news_clean['Organizations'].apply(lambda x: ','.join(x))
    news_clean = news_clean.drop_duplicates(subset=['V2Tone', 'Themes', 'Organizations'], keep='first')
    news_clean['Organizations'] = news_clean['Organizations'].apply(lambda x: x.split(','))
    # Return the first value in each entry from v2tone column
    news_clean['V2Tone'] = news_clean['V2Tone'].apply(lambda x: return_first_v2tone_score(x))

    return news_clean

def process_theme(news_clean):
    final_themes = []
    for i in range(len(news_clean['Themes'])):
        needed_themes = []
        row_themes = news_clean['Themes'].str.split(';').iloc[i]
        for j in row_themes:
            if j in themes:
                needed_themes.append(j)
        final_themes.append(needed_themes)

    news_clean['FinalThemes'] = final_themes
    news_clean['FinalThemes'] = [','.join(map(str, l)) for l in news_clean['FinalThemes']]
    news_clean['FinalThemes'] = news_clean['FinalThemes'].replace(r'^\s*$', np.nan, regex=True)
    news_clean = news_clean[news_clean['FinalThemes'].notna()]

    return news_clean


def to_mongodb(df, collection):     # if empty df there will be problem
    docs = []
    if df.empty:
        print('DataFrame is empty!')
        return
    for index, row in df.iterrows():
        doc = {
            'DATE': int(row['DATE']),
            'DocumentIdentifier': row['DocumentIdentifier'],
            'V2Tone': row['V2Tone'],
            'Themes': row['Themes'],
            'Organizations': str(row['Organizations']),
            'FinalThemes': row['FinalThemes']
        }
        docs.append(doc) 
    collection.insert_many(docs)
    print("Imported data to", collection)


def to_mongodb_map(df, collection):
    docs = []
    if df.empty:
        print('DataFrame is empty!')
        return
    for index, row in df.iterrows():
        doc = {
            'DATE': int(row['DATE']),
            'SourceCommonName': row['SourceCommonName'],
            'DocumentIdentifier': row['DocumentIdentifier'],
            'V2Locations': row['V2Locations'],
            'V2Tone': row['V2Tone'],
            'dates': row['dates'],
        }
        docs.append(doc) 
    collection.insert_many(docs)
    print("Imported data to", collection)

# Note timestamp is PST, west coast time



print("Begin processing last 15 minutes data ...")
print("-----------------------------------------")
# Final of last 15 minutes, pre data processing

#lithium_preprocessing.to_csv(curdir+'/lithium_preprocessing_15.csv', index=True, header=True)---
#lithium_preprocessing_15 = pd.read_csv(curdir+'/lithium_preprocessing_15.csv', dtype="string")---
lithium_preprocessing_15 =lithium_preprocessing
lithium_15 = clean_raw_data(lithium_preprocessing_15)

# Fianl of last 15 minutes data
lithium_final_15 = process_theme(lithium_15)
#lithium_final_15.to_csv(curdir+'/lithium_final_15.csv', index=True, header=True)   ---

to_mongodb(lithium_final_15, collection_lithium_15)



#lithium_preprocessing_merged = pd.read_csv(download_path+'lithium_preprocessing_merged.csv', dtype="string")
#lithium_merged = clean_raw_data(lithium_preprocessing_merged)
#lithium_final_merged = process_theme(lithium_merged)
#lithium_final_merged.to_csv(download_path+'lithium_final_merged.csv', index=True, header=True)




## below for location and source counts
#lithium_merged_15=pd.read_csv(curdir+'/lithium_preprocessing_15.csv', usecols = ['DATE','DocumentIdentifier','SourceCommonName','V2Locations','V2Tone'])---
lithium_merged_15=lithium_preprocessing_15[['DATE','DocumentIdentifier','SourceCommonName','V2Locations','V2Tone']]
lithium_merged_15=lithium_merged_15.dropna(subset=['SourceCommonName','V2Locations'])
lithium_merged_15['dates'] = pd.to_datetime(lithium_merged_15['DATE'], format='%Y%m%d%H%M%S')
lithium_merged_15.sort_values(by=['DATE'],ascending=False,inplace=True)
#lithium_merged_15.to_csv(curdir+'/lithium_merged_15.csv', index=True, header=True)
to_mongodb_map(lithium_merged_15, collection_lithium_map_15)


print("Finish processing and saving data.")
print("----------------DONE!!!!!----------------")