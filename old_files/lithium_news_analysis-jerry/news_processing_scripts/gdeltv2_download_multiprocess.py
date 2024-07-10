from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import pandas as pd
import sys, os
import zipfile
import requests
from multiprocessing import Pool, cpu_count
from functools import partial
from io import BytesIO
import time


########################################
### LITHIUM COMPANY NAMES PROCESSING ###
########################################

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

lithium_mines_clean = {
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

DLE_clean = {
	"LTHM": ["Livent"],
	"300487.SZ": ["Sunresin New Materials"],
	"": ["Eramet"],
	"IBAT.CN": ["International Battery Metals"],
	"": ["EnergySource Minerals"],
	"": ["EnergyX"],
	"RIO.AX": ["Rio Tinto"],
	"": ["Albemarle"],
	"": ["SQM"],
	"CMP": ["Compass Minerals International"],
	"": ["Standard Lithium"],
	"": ["Lilac Solutions"],
	"": ["Summit Nanotech"],
	"": ["IBC Advanced Technologies"],
	"": ["Controlled Thermal"],
	"": ["Occidental Petroleum"],
	"VUL.AX": ["Vulcan Energy Resources"],
}

refining = [
    'Tianqi Lithium',
    'Ganfeng Lithium',
    'Mineral Resources Limited',
    'Pilbara Minerals',
    'Allkem Limited',
    'Lithium Americas',
    'Sichuan Yahua Group',
    'Livent',
    'Jiangxi Special Electric Motor',
    'Yongxing Special Materials Technology',
    'Sinomine Resource',
    'Altura Mining Limited',
    'Critical Elements Lithium Corporation',
    'Eramet SA',
    'Galaxy Resources Limited',
    'Infinity Lithium Corporation Limited',
    'Lithium Chile Inc.',
    'Lithium Power International Limited',
    'Lithium South Development Corporation',
    'Lithium Werks',
    'Lithium Energy Products',
    'Lithium Exploration Group',
    'Lithium Corporation',
    'LithiumOre Corp.',
    'Lithium X',
    'Lithium Energi Exploration',
    'Millennial Lithium Corp.',
    'Nemaska Lithium Inc.',
    'Neo Lithium Corp.',
    'North American Lithium Inc.',
    'Piedmont Lithium Limited',
    'Power Metals Corp.',
    'Pure Energy Minerals Limited',
    'QMC Quantum Minerals Corp.',
    'Rare Earth Salts',
    'Sigma Lithium Resources Corporation',
    'Sonora Lithium Ltd.',
]


mining = [
    'Lithium Americas',
    'Sichuan Yahua Group',
    'Allkem Limited',
    'Livent',
    'Mineral Resources Limited',
    'Pilbara Minerals',
    'Jiangxi Special Electric Motor',
    'Yongxing Special Materials Technology',
    'Sinomine Resource',
    'Altura Mining Limited',
    'Critical Elements Lithium Corporation',
    'Eramet SA',
    'Galaxy Resources Limited',
    'Infinity Lithium Corporation Limited',
    'International Lithium Corp.',
    'Lithium Chile Inc.',
    'Lithium South Development Corporation',
    'Lithium Werks',
    'Lithium Corporation',
    'Lithium X',
    'Lithium Energy Japan',
    'Lithium Energy Limited',
    'Lithium Urban Technologies',
    'Lithium Valley Technology',
    'LSC Lithium Corporation',
    'MGX Minerals Inc.',
    'QMC Quantum Minerals Corp.',
    'Sigma Lithium Resources Corporation',
    'Lithium Australia NL',
    'Lithium Ionic Corp.',
    'Arena Minerals Inc.',
    'Rock Tech Lithium Inc.',
    'American Lithium',
    'Wealth Minerals Ltd.',
    'Zadar Ventures Ltd.',
    'Lithium Power International',
    'Bacanora Lithium Ltd',
    'RB Energy',
    'Tianqi Lithium',
    'Ganfeng Lithium',
]

midstream = [
    'Ganfeng Lithium',
    'Livent',
    'General Lithium',
    'Neometals',
    'Eramet',
    'Nemaska Lithium',
    'Galaxy Resources',
    'Orocobre',
    'Piedmont Lithium',
    'Lithium Americas',
    'POSCO',
    'Tianqi Lithium',
    'Beta Hunt',
    'Sayona Mining',
    'Pilbara Minerals',
    'Altura Mining',
    'Kidman Resources',
    'Neo Lithium',
    'Bacanora Lithium',
    'Core Lithium',
    'European Metals',
    'Plateau Energy Metals',
    'Millennial Lithium',
    'Lake Resources',
]

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
    res = map(str.lower, res)
    res = list(set(res))
    return sorted(list(set(res)))

def compile_entity_names2(listoflist):
    res = []
    for lst in listoflist:
        res = res + lst
    res = list(map(lambda x: clean_bot(x.lower()), res))
    return sorted(list(set(res)))

ALL_COMPANY_NAMES1 = compile_entity_names([midstream_list_clean, mining_co_list_clean, lithium_mines_clean, DLE_clean])
ALL_COMPANY_NAMES2 = compile_entity_names2([refining, mining, midstream])

ALL_COMPANY_NAMES = sorted(list(set(ALL_COMPANY_NAMES1 + ALL_COMPANY_NAMES2)))

def company_in_string(str, mask):
    for m in mask:
        if m.lower() in str:
            return True
    return False




##################################################
### MULTIPROCESSING + MULTITHREADING FUNCTIONS ###
##################################################

def download_zip(url, filePath):
    try:
        file_name = url.split("/")[-1]
        r = requests.get(url)
        with open(filePath + '/' + file_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        # response = requests.get(url)
        # sourceZip = zipfile.ZipFile(BytesIO(response.content))
        print(" Downloaded {} ".format(file_name))
        # sourceZip.extractall(filePath)
        # print(" extracted {}".format(file_name))
        # sourceZip.close()
    except Exception as e:
        print(e)


def process_frame(filename, filePath):
    df = pd.read_csv(filePath + '/' + filename,
                     compression='zip',
                     on_bad_lines='skip', 
                     delimiter="\t", 
                     dtype="string", 
                     encoding = "ISO-8859-1",
                     names=["GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName", "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes", "Locations", "V2Locations", "Persons", "V2Persons", "Organizations", "V2Organizations", "V2Tone", "Dates", "GCAM", "SharingImage", "RelatedImages", "SocialImageEmbeds", "SocialVideoEmbeds", "Quotations", "AllNames", "Amounts", "TranslationInfo", "Extras"])
    os.remove(f"{filePath}/{filename}")
    df["Organizations"] = df["Organizations"].fillna('missing')
    mask = df["Organizations"].apply(lambda x: company_in_string(x, ALL_COMPANY_NAMES))
    df = df[mask | df['DocumentIdentifier'].str.contains('lithium')]
    print(f"Processed file {filename}")
    return df
    

def load_url(url, filepath, process_executor):
    """Downloads URL if the file does not already exist
    Passes filename to aggregation function via a process executor for conccurent aggregation.
    Returns a reference to the future object created by the process executor
    """
    filename = url.split('/')[-1]
    if not os.path.exists(filepath + '/' + filename):
        # print(f'Downloading {url}')
        r = requests.get(url)
        with open(filepath + '/' + filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        # print(f'Downloaded {url}. Passing to aggregator.')
    # else:
    #     print(f'{filename} already exists. Passing to aggregator.')
    return process_executor.submit(aggregate_data, filename, filepath)


def aggregate_data(filename, filepath):
    """Aggregate data from raw file
    The files are stored in zip format. Pandas is used to decompress the file, extract
    FEATURES_OF_INTEREST and calculate aggregated information.
    """
    # print(f'Processing {filename}')
    # Unzip and read the csv
    df = pd.read_csv(filepath + '/' + filename, 
                     compression='zip', 
                     on_bad_lines='skip', 
                     delimiter="\t", 
                     dtype="string", 
                     encoding = "ISO-8859-1",
                     names=["GKGRECORDID", "DATE", "SourceCollectionIdentifier", "SourceCommonName", "DocumentIdentifier", "Counts", "V2Counts", "Themes", "V2Themes", "Locations", "V2Locations", "Persons", "V2Persons", "Organizations", "V2Organizations", "V2Tone", "Dates", "GCAM", "SharingImage", "RelatedImages", "SocialImageEmbeds", "SocialVideoEmbeds", "Quotations", "AllNames", "Amounts", "TranslationInfo", "Extras"])
    os.remove(f"{filepath}/{filename}")

    # # Filter for lithium related news & organizations
    # df["Organizations"] = df["Organizations"].fillna('missing')
    # mask = df["Organizations"].apply(lambda x: company_in_string(x, ALL_COMPANY_NAMES))
    # df = df[mask | df['DocumentIdentifier'].str.contains('lithium')]
    # # print(f'Processed: {filename}')

    return df


def multiprocess_func(start_time, end_time, filepath, overwrite=False):

    timer_1 = time.time()
    print(f"Processing news data bewteen {start_time} and {end_time}")

    date_list = pd.date_range(start_time, end_time, freq='15min')
    urls = [f"http://data.gdeltproject.org/gdeltv2/{date_str}.gkg.csv.zip" for date_str in date_list.strftime("%Y%m%d%H%M%S")]
    # print(urls)

    with ProcessPoolExecutor() as pe, ThreadPoolExecutor() as te:
        # First, the ThreadPoolExecutor is used to download each file.
        future_url_request = [te.submit(load_url, url, filePath, pe) for url in urls]

        # As each download thread completes it returns a Future object from the process executor
        processes = []
        for future in as_completed(future_url_request):
            processes.append(future.result())

        # As each process completes it returns an aggregated dataframe
        aggregated_data = []
        for future in as_completed(processes):
            aggregated_data.append(future.result())

    # Finally, the dataframes are concatenated 
    results = pd.concat(aggregated_data)

    # Filter for lithium related news & organizations
    results["Organizations"] = results["Organizations"].fillna('missing')
    mask = results["Organizations"].apply(lambda x: company_in_string(x, ALL_COMPANY_NAMES))
    results = results[mask | results['DocumentIdentifier'].str.contains('lithium')]
    # print(f'Processed: {filename}')

    if overwrite:
        results.to_csv(filepath, mode='w', index=False, header=True)
    else:
        results.to_csv(filepath, mode='a', index=False, header=False)

    timer_2 = time.time()
    print(f"Finished processing news data bewteen {start_time} and {end_time}")
    print(f"Total time elapsed: {round(timer_2 - timer_1, 2)} seconds", '\n')



# def multiprocess_func2(start_time, end_time, filepath, overwrite=False):

#     break1 = time.time()

#     start = datetime(2023,7,27,12,00,00)
#     end = datetime(2023,7,28,12,00,00)
#     date_list = pd.date_range(start, end, freq='15min')
#     urls = [f"http://data.gdeltproject.org/gdeltv2/{date_str}.gkg.csv.zip" for date_str in date_list.strftime("%Y%m%d%H%M%S")]
#     names = [f"{date_str}.gkg.csv.zip" for date_str in date_list.strftime("%Y%m%d%H%M%S")]

#     with Pool(processes=cpu_count()) as pool:
#         download_func = partial(download_zip, filePath = filePath)
#         results = pool.map(download_func, urls)
#         pool.close()
#         pool.join()

#     break2 = time.time()

#     with Pool(processes=cpu_count()) as pool:
#         process_func = partial(process_frame, filePath=filePath)
#         df_list = pool.map(process_func, names)
#         combined_df = pd.concat(df_list, ignore_index=True)
#         pool.close()
#         pool.join()

#     combined_df.to_csv(filePath + '/test.csv')

#     break3 = time.time()
#     print(f"Total time elapsed: {round(break3 - break1, 2)} seconds")
#     print(break2-break1, break3-break2)


if __name__ == "__main__":

    print(ALL_COMPANY_NAMES)
    
    filePath = os.path.dirname(os.path.abspath(__file__))
    print("filePath is %s " % filePath)

    end_date = datetime(2023,8,2)
    start_date = datetime(2016,1,1)
    overwrite = True
    
    while end_date > start_date:
        end = end_date
        start = end_date - timedelta(days=1)
        
        multiprocess_func(start, end, filePath + '/' + 'filter.csv', overwrite)
        
        end_date = start
        overwrite = False





