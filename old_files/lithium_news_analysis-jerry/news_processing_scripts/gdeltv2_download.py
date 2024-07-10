import pandas as pd
import requests
import os
import zipfile
from datetime import datetime, timedelta
import time

curdir = os.path.dirname(__file__)

midstream_list = {
    "002340.SZ": ["gem co ltd"],
    "300919.SZ": ["cngr advanced material co ltd"],
    "VAR1.STU":	['VAR1.DE','VAR1','VARTA','VARTA AG','STU:VAR1','VAR1:STU','VAR1.DE','VAR1.STU','ETR:VAR1'],
    "002340.SZ": ['GEM Co., Ltd','GEM Co Ltd','GEM Co','Jingmen Gelinmei New Materials Co Ltd','Gelinmei New Materials Co Ltd','Gelinmei Co Ltd','002340.SZ','002340 (SHE)'],
    "300919.SZ": ['CNGR Advanced Material Co Ltd','CNGR','cngrgf','CNGR Advanced Material','300919.SZ','300919 (SHE)'],
    "603799.SS": ['Zhejiang Huayou Cobalt Co.,Ltd','Zhejiang Huayou','Zhejiang Huayou Cobalt','Zhejiang Huayou Cobalt Co Ltd','Huayou Cobalt','603799.SS','603799 (SHA)'],
    "002125.SZ": ['Xiangtan Electrochemical Technology Co Ltd','chinaemd','Xiangtan Electrochemical Scientific Ltd','002125.SZ','002125 (SHE)'],
    "300073.SZ": ['Beijing Easpring Material Technology','Beijing Easpring Material Technology Co Ltd','easpring','300073.SZ','300073 (SHE)'],
    "603659.SS": ['Shanghai Putailai New Energy Technology Co Ltd','Shanghai Putailai','Putailai','Shanghai PTL','Shanghai PTL New Energy Technology','603659.SS','603659 (SHA)'],
    "600884.SS": ['Ningbo Shanshan Co Ltd','Ningbo Shanshan','600884.SS','600884 (SHA)','ssgf.net'],
    "300035.SZ": ['Hunan Zhongke Electric','zhongkeelectric','Zhongke Electric','Hunan Zhongke','300035.SZ','300035 (SHE)'],
    "002812.SZ": ['002812.SZ','002812 (SHE)','Yunnan Energy New Material Co Ltd','Yunnan Energy New Material'],
    "300568.SZ": ['Shenzhen Senior Technology Material Co Ltd','Shenzhen Senior Technology Material','senior798.com','300568.SZ','300568 (SHE)'],
    "002080.SZ": ['Sinoma Science & Technology Co Ltd','Sinoma Science & Technology','Sinoma Science&Technology','Sinoma Science and Technology','002080.SZ','002080 (SHE)','sinomatech.com'],
    "002709.SZ": ['Tinci Materials','Tinci','Guangzhou Tinci Materials Technology Co Ltd','002709.SZ','002709 (SHE)','Guangzhou Tinci'],
    "002407.SZ": ['Do-Fluoride New Materials Co Ltd','Do-Fluoride New Materials','002407.SZ','002407 (SHE)','dfdchem.com'],
    "002759.SZ": ['TONZE NEW ENERGY TECHNOLOGY CO LTD','Tonze New Energy','Tonze','002759.SZ','002759 (SHE)','Tonze.com'],
    "CATL": ["contemporary amperex technology"],
    '0TWH.LSE':	['allkem ltd', 'allkem limited', 'Allkem', 'Orocobre Limited', 'Orocobre', 'Allkem.co', '0TWH.LSE', 'LON: 0TWH', '0TWH.L', '0TWH-GB'],
    'MIN.AX': ['Mineral Resources Ltd', 'MinRes', 'ASX:MIN', 'Mineral Resources Limited', 'MIN.AU', 'MIN.AX'],
}

mining_co_list = {
    "SLI.US": ["standard lithium ltd", "standard lithium ltd.", "standard lithium corp"],
    "ALB.US": ["albemarle corp", "albemarle corp.", "albemarle corporation"],
    'SQM.US': ["sociedad quimica y minera de chile sa adr b", "sociedad quimica y minera de chile sa"],
    '1772.Hk': ["ganfeng lithium co ltd", "ganfeng lithium co. ltd", "jiangxi ganfeng lithium co ltd"],
    '002466.SHE': ["tianqi lithium h yc 1", "tianqi lithium corporation", "sichuan tianqi lithium industries inc"],
    'LTHM.US': ["livent corp", "livent corporation"],
    'PLL.US': ["piedmont lithium ltd adr", "piedmont lithium inc", "piedmont lithium inc.", "piedmont lithium ltd"],
    'LAC.US': ["lithium americas corp"],
    'GALXF.US': ['Galaxy Resources Limited'],
    'ENS.US': ["enersys"],
    'VUL.AU': ["vulcan energy resources limited", "vulcan energy resources ltd", "vulcan energy resources"],
    'EMHLF.US': ["european metals holdings limited", "european metals holdings ltd", "european metals holdings"],
    'CRE.V': ["critical elements corporation", "critical elements", "critical elements lithium corporation", "critical elements (f12.sg)"],
}

lithium_mines = {
    'Greenbushes Lithium Mine': ['greenbushes mine', 'greenbushes lithium', 'greenbushes project'],
    'Salar del Hombre Muerto': ['Salar del Hombre Muerto'],
    'Salar de Atacama': ['Salar de Atacama'],
    'Mt Cattlin Lithium Mine': ['Mt Cattlin Lithium Mine', 'Mt Cattlin Mine'],
    'Bikita Minerals': ['Bikita Minerals'],
    'Mibra Lithium Mine': ['Mibra lithium Mine', 'Mimbra Mine'],
    'Mariana Lithium Mine': ['Mariana Lithium'],
}


redundant = ['co', 'plc', 'ltd', '&', 'inc', 'company', 'corp', 'corporation']
redundant = redundant + [x + '.' for x in redundant]


def clean_bot(x):
    """
    The actual robot which is gonna clean the company suffix for every company.
    :type x: str
    :rtype: str
    """
    x = x.split(' ')
    while len(x) > 0 and x[-1] in redundant:
        del x[-1]
    return ' '.join(x)


def compile_entity_names(dict_list):
    res = []
    for dict in dict_list:
        res = res + sum(list(dict.values()), [])
    return res


def download_url(url, save_path, chunk_size=128):
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)


def load_all_data(start_date, end_date, company_name_lst, save_file, col_names, restart=True):

    start = time.time()

    def company_in_string(str, mask):
        for m in mask:
            if m.lower() in str:
                return True
        return False

    while end_date >= start_date:

        # Download zip file from GKG
        date_str = datetime.strftime(end_date, "%Y%m%d%H%M%S")
        gkg_download_url = f"http://data.gdeltproject.org/gdeltv2/{date_str}.gkg.csv.zip"
        download_url(gkg_download_url, f"{curdir}/temp.gkg.csv.zip")
        with zipfile.ZipFile(f"{curdir}/temp.gkg.csv.zip", 'r') as zip_ref:
            zip_ref.extractall(curdir)
        os.remove(f"{curdir}/temp.gkg.csv.zip")

        # Load unziped csv file into pd dataframe
        data_day = pd.read_csv(f"{curdir}/{date_str}.gkg.csv", names=col_names, on_bad_lines='skip', delimiter="\t", dtype="string", encoding = "ISO-8859-1")
        os.remove(f"{curdir}/{date_str}.gkg.csv")

        # Filter for rows that contain given companies
        data_day["Organizations"] = data_day["Organizations"].fillna('missing')
        mask = data_day["Organizations"].apply(lambda x: company_in_string(x, company_name_lst))
        data_day = data_day[mask | data_day['DocumentIdentifier'].str.contains('lithium')]
        print(data_day[['Organizations', 'DocumentIdentifier']])

        # Load today's filtered data into a combined dataframe
        if restart:
            data_day.to_csv(f"{curdir}/{save_file}", mode='w', index=False, header=True)
        else:
            data_day.to_csv(f"{curdir}/{save_file}", mode='a', index=False, header=False)

        # Move to next date
        end_date = end_date - timedelta(minutes=15)
        restart = False
    
    end = time.time()
    print(f"Elapsed time: {end-start} seconds")



def find_company(company_name):

    df = pd.read_pickle(f"{curdir}/eod_dict.pickle")
    company_dict = {}
    for key,value in df.items():
        key_temp=key.replace(',',' ')
        company_dict[key_temp.lower()] = value.lower()
    company_key = list(company_dict.keys())
    company_key1=','.join(company_key)

    for k in company_key:
        if company_name.lower() in k:
            print(k)




if __name__ == '__main__':

    midstream_list_clean = {
        "002340.SZ": ["gem co ltd", 'Jingmen Gelinmei New Materials', 'Gelinmei New Materials', 'Gelinmei'],
        "300919.SZ": ["cngr advanced material", 'cngr'],
        "VAR1.STU":	['varta ag'],
        "603799.SS": ['Zhejiang Huayou Cobalt', 'Huayou Cobalt'],
        "002125.SZ": ['Xiangtan Electrochemical Technology', 'chinaemd', 'Xiangtan Electrochemical Scientific'],
        "300073.SZ": ['Beijing Easpring Material Tech', 'easpring'],
        "603659.SS": ['Shanghai Putailai New Energy Technology ', 'Shanghai Putailai', 'Putailai', 'Shanghai PTL'],
        "600884.SS": ['Ningbo Shanshan'],
        "300035.SZ": ['Hunan Zhongke Electric', 'zhongkeelectric', 'Zhongke Electric', 'Hunan Zhongke'],
        "002812.SZ": ['Yunnan Energy New Material'],
        "300568.SZ": ['Shenzhen Senior Technology Material', 'senior798.com'],
        "002080.SZ": ['Sinoma Science & Technology', 'Sinoma Science&Technology', 'Sinoma Science and Technology', 'sinomatech.com'],
        "002709.SZ": ['Tinci Materials', 'Guangzhou Tinci Materials Technology', 'Guangzhou Tinci'],
        "002407.SZ": ['Do-Fluoride New Materials', 'Do-Fluoride Chemicals', 'dfdchem.com'],
        "002759.SZ": ['TONZE NEW ENERGY TECHNOLOGY', 'Tonze New Energy', 'Tonze.com'],
        '0TWH.LSE':	['allkem', 'Orocobre', 'Allkem.co'],
        'MIN.AX': ['Mineral Resources Ltd', 'MinRes', 'ASX:MIN', 'Mineral Resources Limited', 'MIN.AU', 'MIN.AX'],
    }

    mining_co_list_clean = {
        "SLI.US": ["standard lithium"],
        "ALB.US": ["albemarle corp"],
        'SQM.US': ["sociedad quimica y minera de chile sa"],
        '1772.Hk': ["ganfeng lithium"],
        '002466.SHE': ["tianqi lithium"],
        'LTHM.US': ["livent corp"],
        'PLL.US': ["piedmont lithium"],
        'LAC.US': ["lithium americas"],
        'GALXF.US': ["Galaxy Resources"],
        'ENS.US': ["enersys"],
        'VUL.AU': ["vulcan energy resources"],
        'EMHLF.US': ["european metals holdings"],
        'CRE.V': ["critical elements"], 
    }

    lithium_mines = {
        'Greenbushes Lithium Mine': ['greenbushes mine', 'greenbushes lithium', 'greenbushes project'],
        'Salar del Hombre Muerto': ['Salar del Hombre Muerto'],
        'Salar de Atacama': ['Salar de Atacama'],
        'Mt Cattlin Lithium Mine': ['Mt Cattlin Lithium Mine', 'Mt Cattlin Mine'],
        'Bikita Minerals': ['Bikita Minerals'],
        'Mibra Lithium Mine': ['Mibra lithium Mine', 'Mimbra Mine'],
        'Mariana Lithium Mine': ['Mariana Lithium'],
    }

    battery_co_list_clean = {
        'PCRFY.US': ['Panasonic'],
        '051910.KO': ['LG Chem'],
        '300750.SHE': ['contemporary amperex technology'],
        '006400.KO': ['Samsung'],
        'MRAAF.US': ['Murata'],
        '300014.SHE': ['EVE energy'],
        'ENR.US': ['Energizer'],
        '1211.HK': ['byd'],
        'SONY.US': ['sony'],
    }

    start = datetime(2023,7,27,12,00,00)
    end = datetime(2023,7,28,12,00,00)

    all_names = compile_entity_names([midstream_list_clean, mining_co_list_clean])
    print(all_names)

    load_all_data(start_date=start, 
                  end_date=end, 
                  company_name_lst=all_names, 
                  save_file='filter2.csv',
                  col_names=["GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName", "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes", "Locations", "V2Locations", "Persons", "V2Persons", "Organizations", "V2Organizations", "V2Tone", "Dates", "GCAM", "SharingImage", "RelatedImages", "SocialImageEmbeds", "SocialVideoEmbeds", "Quotations", "AllNames", "Amounts", "TranslationInfo", "Extras"],
                  restart=True)



    # find_company('byd')

    # for key, value in mining_co_list.items():
    #     cleaned = list(set(map(clean_bot, value)))
    #     mining_co_list[key] = cleaned

    # print(mining_co_list)
