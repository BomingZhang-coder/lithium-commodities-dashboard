# GKG dash main file
import pandas as pd
from dash import  dcc, Input, Output, html
import dash
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import numpy as np
from datetime import datetime
from datetime import date
import math
import json
import os


from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


curdir = os.path.dirname(__file__).replace("\\","/")
mongodb_account = 'quantumgaihold'
mongodb_password = 'ZBYamTQ4EMDVgKl5'

####################################
### Establish MongoDB Connection ###
####################################

uri = "mongodb+srv://" + mongodb_account + ":" + mongodb_password + "@cluster0.etjr4e4.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, server_api=ServerApi('1'))
                          
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!\n")
except Exception as e:
    print(e)


db = client.lithiumdash
lithium_data_15= db.lithium_data_15

newsdata15_pre = pd.DataFrame(list(lithium_data_15.find()))


# Should be running the newly generated csv for the past 24 hours
newdata24_pre=pd.read_csv(curdir+'/lithium_final.csv')              # entire historical data   #update: replace to lithium_final_merged.csv? more rows
#newsdata15_pre=pd.read_csv('lithium_final_15.csv')          # latest 15min data

def process_data(df):
    df['Organizations']=df['Organizations'].str.replace('[','')
    df['Organizations']=df['Organizations'].str.replace(']','')
    df['Organizations']=df['Organizations'].str.replace("'",'')
    df['Organizations']=df['Organizations'].str.replace('"','')

    options24 = (list(df['Organizations'].str.split(',', expand=True).stack()))
    options24 = [x.strip(' ') for x in options24]

    orgs24 = []

    for i in options24:
        if (i not in orgs24):
            orgs24.append(i)
    #%%
    df_theme = pd.read_pickle('theme_sdg_mapping.pk')
    themes=list(df_theme.keys())
    actualthemes24=[]

    for i in range(len(df['Themes'])):
        rowthemes=df['Themes'].str.split(';')[i]
        neededthemes=[]
        if type(rowthemes) is float:
            pass
        else:
            for i in range(len(themes)):
                theme=themes[i]
                if theme in rowthemes:
                    neededthemes.append(theme)
                else:
                    neededthemes.append(np.nan)

        cleanedList24 = [x for x in neededthemes if str(x) != 'nan']
        actualthemes24.append(cleanedList24)
    #%%
    df['ActualThemes']=actualthemes24
    df['ActualThemes'] = [','.join(map(str, l)) for l in df['ActualThemes']]
    df['ActualThemes'] = df['ActualThemes'].replace(r'^\s*$', np.nan, regex=True)
    df=df[df['ActualThemes'].notna()]
    #%%
    df['dates'] = pd.to_datetime(df['DATE'], format='%Y%m%d%H%M%S')

    return df, orgs24

# newdata24, orgs24 = process_data(newdata24_pre)
data_15, orgs15 = process_data(newsdata15_pre)
# newdata24.to_csv('C:/Users/18045/Downloads/lithium-dash-main/newdata24.csv', index=True, header=True)
# data_15.to_csv('C:/Users/18045/Downloads/lithium-dash-main/data_15.csv', index=True, header=True)

lithium_merged=pd.read_csv(curdir+'/lithium_merged.csv').iloc[41434:79959,2:8]    ## for source and location(map)
#lithium_merged=lithium_merged.iloc[0:300,:]
lithium_merged['dates'] = pd.to_datetime(lithium_merged['dates'])
lithium_merged = lithium_merged.dropna(subset=['V2Locations'])


lithium_map_15= db.lithium_map_15

lithium_merged_15 = pd.DataFrame(list(lithium_map_15.find()))
#lithium_merged_15=pd.read_csv('lithium_merged_15.csv')
#lithium_merged_15['dates'] = pd.to_datetime(lithium_merged_15['dates'])
#lithium_merged_15_loc = lithium_merged_15.dropna(subset=['V2Locations'])    ## for map uses

newdata24=pd.read_csv('newdata24.csv')
newdata24['dates'] = pd.to_datetime(newdata24['DATE'], format='%Y%m%d%H%M%S')
#data_15=pd.read_csv('data_15.csv')
data_15['dates'] = pd.to_datetime(data_15['DATE'], format='%Y%m%d%H%M%S')

date_string_s = str(newdata24['DATE'][0])
datetime_obj_s = datetime.strptime(date_string_s, '%Y%m%d%H%M%S')
formatted_date_s = datetime_obj_s.strftime('%B %d, %Y, %H:%M%p')
date_string_e = str(newdata24['DATE'].iloc[-1])
datetime_obj_e = datetime.strptime(date_string_e, '%Y%m%d%H%M%S')
formatted_date_e = datetime_obj_e.strftime('%B %d, %Y, %H:%M%p')

date_string_latest = str(data_15['DATE'][0])
datetime_obj_latest = datetime.strptime(date_string_latest, '%Y%m%d%H%M%S')
formatted_date_latest = datetime_obj_latest.strftime('%B %d, %Y, %H:%M%p')
"""date_string = str(data_15['DATE'])
datetime_obj = datetime.strptime(date_string, '%Y%m%d%H%M%S')
formatted_date = datetime_obj.strftime('%B %d, %Y, %H:%M%p')"""

#data_15=newdata24[newdata24['dates'].isin([newdata24['dates'][0]])]
#%%
# master=pd.read_csv('/Users/AbhirMehra/PycharmProjects/stockmetadata_Abhir/mastertable.csv')
# master=master[['Ticker','Company_Name']]
# master=master[master['Company_Name'].isin([i.upper() for i in options24])]
# prices=pd.read_csv('prices.csv')
# prices=prices.merge(master,left_on="Ticker",right_on="Ticker",how="right")
#%%

## extraction location information from lithium_merged_loc
cities = []
for index, row in lithium_merged.iterrows():


    city_info = row['V2Locations'].split(";")

    # Iterate over each city information
    for info in city_info:
        # Split the information by '#' delimiter
        city_data = info.split("#")
        city_name = city_data[1]  # Extract the city name
        if city_data[5]=="" or city_data[6]=="":
            continue
        latitude = float(city_data[5])  # Extract the latitude
        longitude = float(city_data[6])  # Extract the longitude

        # Append the city information to the cities list as a tuple
        cities.append((row['dates'],row['DocumentIdentifier'],city_name, latitude, longitude,float(row['V2Tone'].split(',')[0])))
cities=pd.DataFrame(cities,columns=['dates','DocumentIdentifier','City','Latitude','Longtitude','V2Tone'])
cities['dates'] = pd.to_datetime(cities['dates'])
lithium_merged=lithium_merged[['dates','SourceCommonName']]


maptype=['open-street-map','white-bg','carto-positron','carto-darkmatter','stamen-terrain','stamen-toner','stamen-watercolor']
colorscales = px.colors.named_colorscales()

up_key1=['lithium-ore', 'nickel', 'cobalt','lithium-future','lithium-mining-companies', 'nickel-futures',
        'spodumene', 'spodumenite','lithium-market-share', 'cobalt-oxide', 'nickel-index', 'lithium-ore-reserves',
        'lithium-etf','lithium-index','lithium-concentration', 'industry-grade','battery-grade', 'li2co3', 'li-oh','lioh','lithium-mangnate',
        'lithium-iron-phosphate', 'ternary-materials', 'lithium-refining','lithium-carbonate','lithium-hydroxide','lithium-production']
up_key=up_key1
down_key1=['ev-car','electric-battery','lithium-battery', 'ev-car-subsidy','battery-subsidy', 'ev-company', 'ev-sales', 'ev-tax-credit','battery-tax-credit',
          'storage', 'lfp-battery','lithium-battery-companies','price-of-li-ion-battery','ternary-lithium-battery']
down_key=down_key1
for space in ["+","_","%20"]:
    up_key2=[sub.replace("-",space) for sub in up_key1]
    up_key=up_key+up_key2
    down_key2=[sub.replace("-",space) for sub in down_key1]
    down_key=down_key+down_key2
up_key=list(set(up_key))
down_key=list(set(down_key))

# ***dropdown menu below***
drop24=html.Div([dcc.Dropdown(id='dropdown24',options = [],placeholder="Pending")])
drop15=html.Div([dcc.Dropdown(id='dropdown15',options = [],placeholder="Pending")])

"""html.Div([
        html.H1(formatted_date + ' PST',style={'textAlign': 'left'})]),"""
layout=dbc.Container([
    html.Div([
        html.H1('Data Timespan: '+formatted_date_s + ' UTC ~ '+formatted_date_e+' UTC ',style={'textAlign': 'left'})]),
    html.Div([
        html.H1('Latest Data Time: '+formatted_date_latest + ' UTC ',style={'textAlign': 'left'})]),
    html.Div([
        dcc.Dropdown(id='dropdown24',options = [],placeholder="Select a Company for Last 24hr Data")],style={"width": "5%"}),
    html.Div([
        dcc.Dropdown(id='dropdown15',options = [],placeholder="Select a Company for Last 15min Data")],style={"width": "5%"}),
    #dbc.Row([dbc.Col(drop24,width=2),dbc.Col(drop15,width=2)]),
    html.Div([
    dcc.DatePickerRange(
        id='datepicker1',
        min_date_allowed=date(int(date_string_s[0:4]),int(date_string_s[4:6]),int(date_string_s[6:8])),
        max_date_allowed=date(int(date_string_e[0:4]),int(date_string_e[4:6]),int(date_string_e[6:8])),
        initial_visible_month=date(int(date_string_e[0:4]),int(date_string_e[4:6]),int(date_string_e[6:8])),
        end_date=date(int(date_string_e[0:4]),int(date_string_e[4:6]),int(date_string_e[6:8])),
        start_date=date(int(date_string_e[0:4]),int(date_string_e[4:6])-1,int(date_string_e[6:8])-1),
        day_size=50
    ),
    html.Div(id='output-container-date-picker-range')]),
    #html.Div([drop24,drop15]),
    html.Div([
        dcc.Graph(id='spyder24', style={'display': 'inline-block','height':'650px','width':'2000px'}),
        dcc.Graph(id='spyder',style={'display': 'inline-block','height':'650px','width':'2000px'})]),
    html.Div([
        dcc.Graph(id='scatter24', style={'display': 'inline-block','height':'1300px'}),
        dcc.Graph(id='scatter',style={'display': 'inline-block','height':'1300px'})]),
    html.Div([
        dcc.Graph(id='groupedscatter24', style={'display': 'inline-block','height':'1000px'}),
        dcc.Graph(id='groupedscatter',style={'display': 'inline-block','height':'1000px'})]),
    html.Div([
        dcc.Graph(id='freqhist24', style={'display': 'inline-block'}),
        dcc.Graph(id='freqhist',style={'display': 'inline-block'})]),
    html.Div([
        dcc.Graph(id='avghist24', style={'display': 'inline-block'}),
        dcc.Graph(id='avghist',style={'display': 'inline-block'})]),
    html.Div([
        dcc.Graph(id='heatmap24', style={'display': 'inline-block'}),
        dcc.Graph(id='heatmap',style={'display': 'inline-block'})]),
    html.Div([
        html.Div(id='table24', style={'display': 'inline-block'}),
        html.Div(id='table',style={'display': 'inline-block'})]),
    html.Div([
        html.Div(id='tableurl24', style={'display': 'inline-block'}),
        html.Div(id='tableurl',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='pricegraph24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='pricegraph',style={'display': 'inline-block'})]),
    html.Div([
        dcc.Graph(id='themegraph24', style={'display': 'inline-block'}),
        dcc.Graph(id='themegraph',style={'display': 'inline-block'})]),
    # html.Div([
    #     dcc.Graph(id='stackedbar24', style={'display': 'inline-block'}),
    #     dcc.Graph(id='stackedbar',style={'display': 'inline-block'})]),
    html.Div([
        dcc.Graph(id='stackedbar24_relative', style={'display': 'inline-block'}),
        dcc.Graph(id='stackedbar_relative',style={'display': 'inline-block'})]),
    html.Div([
        dcc.Graph(id='barsource', style={'display': 'inline-block'}),
        dcc.Graph(id='barsource15', style={'display': 'inline-block'})
        ]),
    html.Div([
        dcc.Input(id="mapcountin", type="text", placeholder="Input location; separate by comma",style={"width": "100%"}),
        dcc.Dropdown(id='dropdownmapcount',options = maptype,placeholder="Select Map Type",value='open-street-map',style={"width": "50%"}),
        dcc.Dropdown(id='mapcountcolor', options=colorscales,value='viridis',style={"width": "50%"}),
        dcc.Graph(id='mapcount', style={'display': 'inline-block','width':'1400px','height':'800px'})
        ]),
    html.Div([
        dcc.Markdown("""Click on locations in the map."""),
        html.Pre(id='click-data-count', style={'height':'600px','overflowY':'scroll'}),
        ]),


    html.Div(
        style = {'display' : 'flex'},
        children=[
            html.Div(
                dcc.Dropdown(id='dropdownmapcount_up',options = maptype,placeholder="Select Map Type",value='open-street-map',style={"width": "1000px"})),
            html.Div(
                dcc.Dropdown(id='dropdownmapcount_down',options = maptype,placeholder="Select Map Type",value='open-street-map',style={"width": "1000px"}))
        ]),
    html.Div(
        style = {'display' : 'flex'},
        children=[
            html.Div(
                dcc.Graph(id='mapcount_up', style={'display': 'inline-block','width':'1000px','height':'700px'}),),
            html.Div(
                dcc.Graph(id='mapcount_down', style={'display': 'inline-block','width':'1000px','height':'700px'}))
        ]),
    html.Div(
        style = {'display' : 'flex'},
        children=[
            html.Div(
                html.Pre(id='click-data-count_up', style={'height':'600px','width':'1000px','overflowY':'scroll'})),
            html.Div(
                html.Pre(id='click-data-count_down', style={'height':'600px','width':'1000px','overflowY':'scroll'}))
        ]),

    html.Div([
        dcc.Input(id="maptonein", type="text", placeholder="Input location; separate by comma",style={"width": "40%"}),
        dcc.Dropdown(id='dropdownmaptone',options = maptype,placeholder="Select Map Type",value='open-street-map',style={"width": "50%"}),
        dcc.Dropdown(id='maptonecolor', options=colorscales,value='rdbu',style={"width": "50%"}),
        dcc.Graph(id='maptone', style={'display': 'inline-block','width':'1400px','height':'800px'})
        ]),
    html.Div([
        dcc.Markdown("""Click on locations in the map."""),
        html.Pre(id='click-data-tone', style={'height':'600px','overflowY':'scroll'}),
        ]),

    html.Div(
        style = {'display' : 'flex'},
        children=[
            html.Div(
                dcc.Dropdown(id='dropdownmaptone_up',options = maptype,placeholder="Select Map Type",value='open-street-map',style={"width": "1000px"})),
            html.Div(
                dcc.Dropdown(id='dropdownmaptone_down',options = maptype,placeholder="Select Map Type",value='open-street-map',style={"width": "1000px"}))
        ]),
    html.Div(
        style = {'display' : 'flex'},
        children=[
            html.Div(
                dcc.Graph(id='maptone_up', style={'display': 'inline-block','width':'1000px','height':'700px'}),),
            html.Div(
                dcc.Graph(id='maptone_down', style={'display': 'inline-block','width':'1000px','height':'700px'}))
        ]),
    html.Div(
        style = {'display' : 'flex'},
        children=[
            html.Div(
                html.Pre(id='click-data-tone_up', style={'height':'600px','width':'1000px','overflowY':'scroll'})),
            html.Div(
                html.Pre(id='click-data-tone_down', style={'height':'600px','width':'1000px','overflowY':'scroll'}))
        ]),

    ])
    # html.Div([
    #     html.Iframe(id='wordcloud24', srcDoc=None,style={'width':'45%','height':'500px','display': 'inline-block'}),
    #     html.Iframe(id='wordcloud',srcDoc=None,style={'width':'45%','height':'500px','display': 'inline-block'})]
#%%
curr15=data_15['dates'][0]
delta=pd.Timedelta('0 days 00:15:00')
prev15=curr15-delta
org15=data_15[data_15['dates'].isin([curr15])]

app = dash.Dash(__name__)
server = app.server
app.layout=layout

@app.callback(Output('spyder', 'figure'),
              Input('dropdown15', 'value'))
def update_spyder(value):
    org=data_15
    # Use similar method to search through documentidentifier for lithium
    org = org[['ActualThemes','V2Tone']]
    org_closed = pd.concat([org, org.iloc[[0]]], ignore_index=True)
    fig=px.line_polar(org_closed,r='V2Tone',theta='ActualThemes')
    return fig

@app.callback(Output('spyder24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_spyder24(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org = org[['ActualThemes','V2Tone']]
    org_closed = pd.concat([org, org.iloc[[0]]], ignore_index=True)
    fig=px.line_polar(org_closed,r='V2Tone',theta='ActualThemes')
    return fig


@app.callback(Output('scatter', 'figure'),
              [Input('dropdown15', 'value')])
def update_scatter(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    fig = px.scatter(x=output.V2Tone, y=output.Themes)
    return fig

@app.callback(Output('scatter24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_scatter24(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    fig = px.scatter(x=output.V2Tone, y=output.Themes)
    return fig

@app.callback(Output('groupedscatter', 'figure'),
              [Input('dropdown15', 'value')])
def update_spyder(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org = org[['ActualThemes','V2Tone']]
    fig = px.scatter(x=org.V2Tone, y=org.ActualThemes)
    return fig

@app.callback(Output('groupedscatter24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_spyder24(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org = org[['ActualThemes','V2Tone']]
    fig = px.scatter(x=org.V2Tone, y=org.ActualThemes)
    return fig

@app.callback(Output('freqhist', 'figure'),
              [Input('dropdown15', 'value')])
def update_freqhist(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    output=output['Themes']
    fig = px.histogram(output,x='Themes').update_xaxes(categoryorder="total descending")
    return fig

@app.callback(Output('freqhist24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_freqhist24(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    output=output['Themes']
    fig = px.histogram(output,x='Themes').update_xaxes(categoryorder="total descending")
    return fig

@app.callback(Output('avghist', 'figure'),
              [Input('dropdown15', 'value')])
def update_avghist(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    output=output.groupby('Themes', as_index=False).mean()
    output.sort_values(by=['V2Tone'],inplace=True)
    fig = px.bar(output, x='Themes', y='V2Tone')
    return fig

@app.callback(Output('avghist24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_avghist24(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    output=output.groupby('Themes', as_index=False).mean()
    output.sort_values(by=['V2Tone'],inplace=True)
    fig = px.bar(output, x='Themes', y='V2Tone')
    return fig

@app.callback(Output('heatmap', 'figure'),
              [Input('dropdown15', 'value')])
def update_heatmap(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    output['new']=output['V2Tone'].astype(str)+output['Themes']
    c1=output[output['V2Tone'].between(-100, -5, inclusive='both')].drop('Themes',axis=1)
    c2=output[output['V2Tone'].between(-4.99, -4, inclusive='both')].drop('Themes',axis=1)
    c3=output[output['V2Tone'].between(-3.99, -3, inclusive='both')].drop('Themes',axis=1)
    c4=output[output['V2Tone'].between(-2.99, -2, inclusive='both')].drop('Themes',axis=1)
    c5=output[output['V2Tone'].between(-1.99, -1, inclusive='both')].drop('Themes',axis=1)
    c6=output[output['V2Tone'].between(-0.99, 0, inclusive='both')].drop('Themes',axis=1)
    c7=output[output['V2Tone'].between(0.01, 1, inclusive='both')].drop('Themes',axis=1)
    c8=output[output['V2Tone'].between(1.01, 2, inclusive='both')].drop('Themes',axis=1)
    c9=output[output['V2Tone'].between(2.01, 3, inclusive='both')].drop('Themes',axis=1)
    c10=output[output['V2Tone'].between(3.01, 4, inclusive='both')].drop('Themes',axis=1)
    c11=output[output['V2Tone'].between(4.01, 5, inclusive='both')].drop('Themes',axis=1)
    c12=output[output['V2Tone'].between(5, 100, inclusive='both')].drop('Themes',axis=1)
    c1.rename(columns={"V2Tone": 'Lesser than -5'},inplace=True)
    c2.rename(columns={"V2Tone": '-5 to -4'},inplace=True)
    c3.rename(columns={"V2Tone": '-4 to -3'},inplace=True)
    c4.rename(columns={"V2Tone": '-3 to -2'},inplace=True)
    c5.rename(columns={"V2Tone": '-2 to -1'},inplace=True)
    c6.rename(columns={"V2Tone": '-1 to 0'},inplace=True)
    c7.rename(columns={"V2Tone": '0.01 to 1'},inplace=True)
    c8.rename(columns={"V2Tone": '1.01 to 2'},inplace=True)
    c9.rename(columns={"V2Tone": '2.01 to 3'},inplace=True)
    c10.rename(columns={"V2Tone": '3.01 to 4'},inplace=True)
    c11.rename(columns={"V2Tone": '4.01 to 5'},inplace=True)
    c12.rename(columns={"V2Tone": 'Greater than 5'},inplace=True)
    output=output.merge(c1, on='new',how='left')
    output=output.merge(c2, on='new',how='left')
    output=output.merge(c3, on='new',how='left')
    output=output.merge(c4, on='new',how='left')
    output=output.merge(c5, on='new',how='left')
    output=output.merge(c6, on='new',how='left')
    output=output.merge(c7, on='new',how='left')
    output=output.merge(c8, on='new',how='left')
    output=output.merge(c9, on='new',how='left')
    output=output.merge(c10, on='new',how='left')
    output=output.merge(c11, on='new',how='left')
    output=output.merge(c12, on='new',how='left')
    output=output.drop(['V2Tone','new'],axis=1).set_index('Themes')
    fig = px.imshow(output,text_auto=True,aspect='auto',color_continuous_scale=["red", "green"])
    return fig

@app.callback(Output('heatmap24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_heatmap(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org
    output['Themes']=new.values
    output['new']=output['V2Tone'].astype(str)+output['Themes']
    c1=output[output['V2Tone'].between(-100, -5, inclusive='both')].drop('Themes',axis=1)
    c2=output[output['V2Tone'].between(-4.99, -4, inclusive='both')].drop('Themes',axis=1)
    c3=output[output['V2Tone'].between(-3.99, -3, inclusive='both')].drop('Themes',axis=1)
    c4=output[output['V2Tone'].between(-2.99, -2, inclusive='both')].drop('Themes',axis=1)
    c5=output[output['V2Tone'].between(-1.99, -1, inclusive='both')].drop('Themes',axis=1)
    c6=output[output['V2Tone'].between(-0.99, 0, inclusive='both')].drop('Themes',axis=1)
    c7=output[output['V2Tone'].between(0.01, 1, inclusive='both')].drop('Themes',axis=1)
    c8=output[output['V2Tone'].between(1.01, 2, inclusive='both')].drop('Themes',axis=1)
    c9=output[output['V2Tone'].between(2.01, 3, inclusive='both')].drop('Themes',axis=1)
    c10=output[output['V2Tone'].between(3.01, 4, inclusive='both')].drop('Themes',axis=1)
    c11=output[output['V2Tone'].between(4.01, 5, inclusive='both')].drop('Themes',axis=1)
    c12=output[output['V2Tone'].between(5, 100, inclusive='both')].drop('Themes',axis=1)
    c1.rename(columns={"V2Tone": 'Lesser than -5'},inplace=True)
    c2.rename(columns={"V2Tone": '-5 to -4'},inplace=True)
    c3.rename(columns={"V2Tone": '-4 to -3'},inplace=True)
    c4.rename(columns={"V2Tone": '-3 to -2'},inplace=True)
    c5.rename(columns={"V2Tone": '-2 to -1'},inplace=True)
    c6.rename(columns={"V2Tone": '-1 to 0'},inplace=True)
    c7.rename(columns={"V2Tone": '0.01 to 1'},inplace=True)
    c8.rename(columns={"V2Tone": '1.01 to 2'},inplace=True)
    c9.rename(columns={"V2Tone": '2.01 to 3'},inplace=True)
    c10.rename(columns={"V2Tone": '3.01 to 4'},inplace=True)
    c11.rename(columns={"V2Tone": '4.01 to 5'},inplace=True)
    c12.rename(columns={"V2Tone": 'Greater than 5'},inplace=True)
    output=output.merge(c1, on='new',how='left')
    output=output.merge(c2, on='new',how='left')
    output=output.merge(c3, on='new',how='left')
    output=output.merge(c4, on='new',how='left')
    output=output.merge(c5, on='new',how='left')
    output=output.merge(c6, on='new',how='left')
    output=output.merge(c7, on='new',how='left')
    output=output.merge(c8, on='new',how='left')
    output=output.merge(c9, on='new',how='left')
    output=output.merge(c10, on='new',how='left')
    output=output.merge(c11, on='new',how='left')
    output=output.merge(c12, on='new',how='left')
    output=output.drop(['V2Tone','new'],axis=1).set_index('Themes')
    fig = px.imshow(output,text_auto=True,aspect='auto',color_continuous_scale=["red", "green"])
    return fig

@app.callback(Output('table', 'children'),
              [Input('dropdown15', 'value')])
def update_scatter(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
    org=org.sort_values(by=['V2Tone'])
    # fig = go.Figure(data=[go.Table(
    # header=dict(values=list(org.columns)),
    # cells=dict(values=[org.ActualThemes, org.V2Tone, org.DocumentIdentifier],height=60))])
    # return fig
    print(org.to_dict('records'))
    table = dash.dash_table.DataTable(
        data=org.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in org.columns],
        fixed_rows={'headers': True},
        style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
        style_table={'overflowX': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-left':'70px'}
    )
    return table

@app.callback(Output('table24', 'children'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_scatter(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
    org=org.sort_values(by=['V2Tone'])
    # fig = go.Figure(data=[go.Table(
    # header=dict(values=list(org.columns)),
    # cells=dict(values=[org.ActualThemes, org.V2Tone, org.DocumentIdentifier],height=60))])
    # return fig
    print(org.to_dict('records'))
    table = dash.dash_table.DataTable(
        data=org.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in org.columns],
        fixed_rows={'headers': True},
        style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
        style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-left':'70px'}
    )
    return table
@app.callback(Output('tableurl', 'children'),
              [Input('dropdown15', 'value')])
def update_scatter(input_value):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
    org=org.sort_values(by=['V2Tone'])
    org=org['DocumentIdentifier']
    org=org.to_frame()
    # fig = go.Figure(data=[go.Table(
    # header=dict(values=list(org.columns)),
    # cells=dict(values=[org.DocumentIdentifier],height=60))])
    # return fig
    print(org.to_dict('records'))
    table = dash.dash_table.DataTable(
        data=org.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in org.columns],
        fixed_rows={'headers': True},
        style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
        style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-left':'70px'}
    )
    return table
@app.callback(Output('tableurl24', 'children'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_scatter(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone','DocumentIdentifier']]
    org=org.sort_values(by=['V2Tone'])
    org=org['DocumentIdentifier']
    org=org.to_frame()
    # fig = go.Figure(data=[go.Table(
    # header=dict(values=list(org.columns)),
    # cells=dict(values=[org.DocumentIdentifier],height=60))])
    # return fig
    print(org.to_dict('records'))
    table = dash.dash_table.DataTable(
        data=org.to_dict('records'),
        columns=[{'name': i, 'id': i} for i in org.columns],
        fixed_rows={'headers': True},
        style_cell={'textAlign':'left', 'maxWidth': '300px','whiteSpace': 'normal'},
        style_table={'overflowX:': 'scroll','overflowY':'scroll','height': '40vh','width':'40vw','margin-left':'70px'}
    )
    return table
# @app.callback(Output('pricegraph', 'figure'),
#               [Input('dropdown', 'value')])
# def update_stsfig(input_value):
#     input_value=input_value.upper()
#     data=prices[prices['Company_Name'].isin([input_value])].set_index('date')['adjusted_close']
#     fig = px.line(data)
#     return fig
#
# @app.callback(Output('pricegraph24', 'figure'),
#               [Input('dropdown', 'value')])
# def update_stsfig(input_value):
#     input_value=input_value.upper()
#     data=prices[prices['Company_Name'].isin([input_value])].set_index('date')['adjusted_close']
#     fig = px.line(data)
#     return fig

@app.callback(Output('themegraph', 'figure'),
              [Input('dropdown15', 'value')])
def update_stsfig(input_value):
    #org = data_15[data_15['Organizations'].str.contains(input_value)]
    org=data_15
    org = org[['ActualThemes', 'V2Tone', 'dates']]
    new = org['ActualThemes'].str.split(',', expand=True).stack()
    vals = new.index.get_level_values(level=0)
    org = org.drop(columns=['ActualThemes']).loc[vals]
    output = pd.DataFrame()
    output['V2Tone'] = org['V2Tone']
    output['dates'] = org['dates']
    output['Themes'] = new.values
    fig = px.scatter(output, x="dates", y="V2Tone", color='Themes')
    return fig

@app.callback(Output('themegraph24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_stsfig(value,start_date,end_date):
    #org = newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    # org = org[['ActualThemes', 'V2Tone', 'dates']]
    # new = org['ActualThemes'].str.split(',', expand=True).stack()
    # vals = new.index.get_level_values(level=0)
    # org = org.drop(columns=['ActualThemes']).loc[vals]
    # output = pd.DataFrame()
    # output['V2Tone'] = org['V2Tone']
    # output['Date'] = org['dates']
    # output['Themes'] = new.values
    # output = output.sort_values('Date')
    # fig = px.line(output, x="Date", y="V2Tone", color='Themes',markers=True)
    # return fig
    org=org[['ActualThemes','V2Tone','dates']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org['V2Tone']
    output['Themes']=new.values
    output['dates']=org['dates'].dt.date
    output=output.groupby(['dates','Themes'], as_index=False).mean()
    fig = px.scatter(output, x="dates", y="V2Tone", color='Themes')
    return fig

@app.callback(Output('stackedbar', 'figure'),
              [Input('dropdown15', 'value')])
def update_stackedbar(input_value):
    curr=data_15['dates'][0]
    prev=curr-pd.Timedelta('0 days 00:15:00')            ## need modification
    #org = newdata24[newdata24['dates'].isin([curr, prev])]
    #org = org[org['Organizations'].str.contains(input_value)]
    #org=data_15[data_15['dates'].isin([curr, prev])]
    org=data_15
    org = org[['ActualThemes', 'V2Tone', 'dates']]
    new = org['ActualThemes'].str.split(',', expand=True).stack()
    vals = new.index.get_level_values(level=0)
    org = org.drop(columns=['ActualThemes']).loc[vals]
    output = pd.DataFrame()
    output['V2Tone'] = org['V2Tone']
    output['dates'] = org['dates']
    output['Themes'] = new.values
    # d1 = output[output['dates'].isin([curr])].groupby('Themes', as_index=False).mean()
    # d1['dates'] =  curr
    # d2 = output[output['dates'].isin([prev])].groupby('Themes', as_index=False).mean()
    # d2['dates'] = prev
    # new = pd.concat([d1, d2])
    fig = px.bar(output, x="dates", y="V2Tone", color='Themes',
              hover_data=['Themes'], barmode='stack')
    return fig

@app.callback(Output('stackedbar24', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_stackedbar(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone','dates']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org['V2Tone']
    output['Themes']=new.values
    output['dates']=org['dates'].dt.date
    output=output.groupby(['dates','Themes'], as_index=False).mean()
    #output.sort_values(by=['V2Tone'],inplace=True)
    #output['col'] = 'Themes'
    fig = px.bar(output, x="dates", y="V2Tone", color='Themes',
            hover_data=['Themes'], barmode = 'stack')
    return fig

@app.callback(Output('stackedbar_relative', 'figure'),
              [Input('dropdown15', 'value')])
def update_stackedbar(input_value):
    curr=data_15['dates'][0]
    delta=pd.Timedelta('0 days 00:15:00')
    prev=curr-delta           ## need modification
    timeWindow=[]
    timeWindow.append(curr)
    timeWindow.append(prev)


    #org = newdata24[newdata24['dates'].isin([curr, prev])]
    #org = org[org['Organizations'].str.contains(input_value)]
    #org=data_15[data_15['dates'].isin([curr, prev])]
    org=data_15
    org = org[['ActualThemes', 'V2Tone', 'dates']]
    new = org['ActualThemes'].str.split(',', expand=True).stack()
    vals = new.index.get_level_values(level=0)
    org = org.drop(columns=['ActualThemes']).loc[vals]
    output = pd.DataFrame()
    output['V2Tone'] = org['V2Tone']
    output['dates'] = org['dates']
    output['Themes'] = new.values
    # d1 = output[output['dates'].isin([curr])].groupby('Themes', as_index=False).mean()
    # d1['dates'] =  curr
    # d2 = output[output['dates'].isin([prev])].groupby('Themes', as_index=False).mean()
    # d2['dates'] = prev
    # new = pd.concat([d1, d2])
    output.sort_values(by=['V2Tone'],inplace=True)
    fig = px.bar(output, x="dates", y="V2Tone", color='Themes',
              hover_data=['Themes'], barmode='relative')
    return fig

@app.callback(Output('stackedbar24_relative', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_stackedbar(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=newdata24

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    org=org[['ActualThemes','V2Tone','dates']]
    new=org['ActualThemes'].str.split(',',expand=True).stack()
    vals=new.index.get_level_values(level=0)
    org=org.drop(columns=['ActualThemes']).loc[vals]
    output=pd.DataFrame()
    output['V2Tone']=org['V2Tone']
    output['Themes']=new.values
    output['dates']=org['dates'].dt.date
    output=output.groupby(['dates','Themes'], as_index=False).mean()
    output.sort_values(by=['V2Tone'],inplace=True)
    #output['col'] = 'Themes'
    fig = px.bar(output, x="dates", y="V2Tone", color='Themes',
            hover_data=['Themes'], barmode = 'relative')
    return fig

# @app.callback(Output('wordcloud', 'srcDoc'),
#               [Input('dropdown', 'value')])
# def update_wordcloud(input_value):
#     org=data_15[data_15['Organizations'].str.contains(input_value)]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     text=""
#     for i in new.values:
#         text+=i + ' '
#     wordcloud = WordCloud(width = 800, height = 800,
#                 background_color ='white',
#                 min_font_size = 10).generate(text)
#     fig,ax=plt.subplots()
#     ax.imshow(wordcloud)
#     ax.axis("off")
#     wc = mpld3.fig_to_html(fig)
#     return wc
#
# @app.callback(Output('wordcloud24', 'srcDoc'),
#               [Input('dropdown', 'value')])
# def update_wordcloud(input_value):
#     org=newdata24[newdata24['Organizations'].str.contains(input_value)]
#     org=org[['ActualThemes','V2Tone']]
#     new=org['ActualThemes'].str.split(',',expand=True).stack()
#     text=""
#     for i in new.values:
#         text+=i + ' '
#     wordcloud = WordCloud(width = 800, height = 800,
#                 background_color ='white',
#                 min_font_size = 10).generate(text)
#     fig,ax=plt.subplots()
#     ax.imshow(wordcloud)
#     ax.axis("off")
#     wc = mpld3.fig_to_html(fig)
#     return wc
@app.callback(Output('barsource', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'))
def update_barsource(value,start_date,end_date):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=lithium_merged

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    fig = px.histogram(org,y='SourceCommonName').update_yaxes(categoryorder="total ascending")
    return fig

@app.callback(Output('barsource15', 'figure'),
              Input('dropdown24', 'value'))
def update_barsource15(value):
    #org=newdata24[newdata24['Organizations'].str.contains(input_value)]
    org=lithium_merged_15

    fig = px.histogram(org,y='SourceCommonName').update_yaxes(categoryorder="total ascending")
    return fig

@app.callback(Output('mapcount', 'figure'),
              [Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'),
              Input('mapcountin','value'),Input('dropdownmapcount', 'value'),Input('mapcountcolor', 'value')])
def update_mapcount(value,start_date,end_date,location,map_t,scale):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=cities

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    if location is not None and len(location)>0:
        location=location.split(",")
        org=org[org['City'].str.contains('|'.join(location))]

    org1=org.loc[:,['City','Latitude','Longtitude']].groupby(['City','Latitude','Longtitude']).size().reset_index(name='Count')
    org2=org.groupby(['City','Latitude','Longtitude'])['DocumentIdentifier'].unique().apply(list).reset_index(name='Url')
    org=org1.merge(org2,how='right',on=['City','Latitude','Longtitude'])
    #org['dummy_column_for_size'] = 1
    fig = px.scatter_mapbox(org,  # Dataframe with city names and values
                        lat='Latitude', lon='Longtitude',  # Specify the latitude and longitude columns
                        #z='Count',  # Column containing the values for coloring
                        #radius=10,  # Adjust the radius of each data point on the heatmap
                        color='Count',
                        size='Count',
                        size_max=18,
                        zoom=1,  # Adjust the initial zoom level of the map
                        mapbox_style=map_t,  # Choose a mapbox style (e.g., 'open-street-map')
                        color_continuous_scale='brwnyl',
                        title='Source Count City-based Heatmap',
                        hover_data={'City':True,'Latitude':True,'Longtitude':True,'Count':True,'Url':False})  # Title of the heatmap
    fig.update_layout(clickmode='event+select')
    return fig

@app.callback(
    Output('click-data-count', 'children'),
    Input('mapcount', 'selectedData'))
def display_click_data_count(clickData):
    return json.dumps({
        'City':clickData['points'][0]['customdata'][0],
        'Latitude & Longtitude':str(clickData['points'][0]['customdata'][1])+','+str(clickData['points'][0]['customdata'][2]),
        'Count':clickData['points'][0]['customdata'][3],
        'Url':clickData['points'][0]['customdata'][4]}, indent=2)


@app.callback(Output('mapcount_up', 'figure'),
              [Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'),
              Input('mapcountin','value'),Input('dropdownmapcount_up', 'value')])
def update_mapcount(value,start_date,end_date,location,map_t):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=cities[cities['DocumentIdentifier'].str.contains('|'.join(up_key))]

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    if location is not None and len(location)>0:
        location=location.split(",")
        org=org[org['City'].str.contains('|'.join(location))]

    org1=org.loc[:,['City','Latitude','Longtitude']].groupby(['City','Latitude','Longtitude']).size().reset_index(name='Count')
    org2=org.groupby(['City','Latitude','Longtitude'])['DocumentIdentifier'].unique().apply(list).reset_index(name='Url')
    org=org1.merge(org2,how='right',on=['City','Latitude','Longtitude'])
    #org['dummy_column_for_size'] = 1
    fig = px.scatter_mapbox(org,  # Dataframe with city names and values
                        lat='Latitude', lon='Longtitude',  # Specify the latitude and longitude columns
                        #z='Count',  # Column containing the values for coloring
                        #radius=10,  # Adjust the radius of each data point on the heatmap
                        color='Count',
                        size='Count',
                        size_max=18,
                        zoom=1,  # Adjust the initial zoom level of the map
                        mapbox_style=map_t,  # Choose a mapbox style (e.g., 'open-street-map')
                        color_continuous_scale='brwnyl',
                        title='Source Count City-based Heatmap (Upstream)',
                        hover_data={'City':True,'Latitude':True,'Longtitude':True,'Count':True,'Url':False})  # Title of the heatmap
    fig.update_layout(clickmode='event+select')
    return fig

@app.callback(
    Output('click-data-count_up', 'children'),
    Input('mapcount_up', 'selectedData'))
def display_click_data_count_up(clickData):
    return json.dumps({
        'City':clickData['points'][0]['customdata'][0],
        'Latitude & Longtitude':str(clickData['points'][0]['customdata'][1])+','+str(clickData['points'][0]['customdata'][2]),
        'Count':clickData['points'][0]['customdata'][3],
        'Url':clickData['points'][0]['customdata'][4]}, indent=2)


@app.callback(Output('mapcount_down', 'figure'),
              [Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'),
              Input('mapcountin','value'),Input('dropdownmapcount_down', 'value')])
def update_mapcount(value,start_date,end_date,location,map_t):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=cities[cities['DocumentIdentifier'].str.contains('|'.join(down_key))]

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    if location is not None and len(location)>0:
        location=location.split(",")
        org=org[org['City'].str.contains('|'.join(location))]

    org1=org.loc[:,['City','Latitude','Longtitude']].groupby(['City','Latitude','Longtitude']).size().reset_index(name='Count')
    org2=org.groupby(['City','Latitude','Longtitude'])['DocumentIdentifier'].unique().apply(list).reset_index(name='Url')
    org=org1.merge(org2,how='right',on=['City','Latitude','Longtitude'])
    #org['dummy_column_for_size'] = 1
    fig = px.scatter_mapbox(org,  # Dataframe with city names and values
                        lat='Latitude', lon='Longtitude',  # Specify the latitude and longitude columns
                        #z='Count',  # Column containing the values for coloring
                        #radius=10,  # Adjust the radius of each data point on the heatmap
                        color='Count',
                        size='Count',
                        size_max=18,
                        zoom=1,  # Adjust the initial zoom level of the map
                        mapbox_style=map_t,  # Choose a mapbox style (e.g., 'open-street-map')
                        color_continuous_scale='brwnyl',
                        title='Source Count City-based Heatmap (Downstream)',
                        hover_data={'City':True,'Latitude':True,'Longtitude':True,'Count':True,'Url':False})  # Title of the heatmap
    fig.update_layout(clickmode='event+select')
    return fig

@app.callback(
    Output('click-data-count_down', 'children'),
    Input('mapcount_down', 'selectedData'))
def display_click_data_count_down(clickData):
    return json.dumps({
        'City':clickData['points'][0]['customdata'][0],
        'Latitude & Longtitude':str(clickData['points'][0]['customdata'][1])+','+str(clickData['points'][0]['customdata'][2]),
        'Count':clickData['points'][0]['customdata'][3],
        'Url':clickData['points'][0]['customdata'][4]}, indent=2)


@app.callback(Output('maptone', 'figure'),
              Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'),
              Input('maptonein','value'),Input('dropdownmaptone', 'value'),Input('maptonecolor', 'value'))
def update_maptone(value,start_date,end_date,location,map_t,scale):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=cities

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    if location is not None and len(location)>0:
        location=location.split(",")
        org=org[org['City'].str.contains('|'.join(location))]

    org1=org.loc[:,['City','Latitude','Longtitude','V2Tone']].groupby(['City','Latitude','Longtitude'], as_index=False).mean()
    org2=org.groupby(['City','Latitude','Longtitude'])['DocumentIdentifier'].apply(list).reset_index(name='Url')
    org=org1.merge(org2,how='right',on=['City','Latitude','Longtitude'])
    org['dummy_column_for_size'] = 1
    fig = px.scatter_mapbox(org,  # Dataframe with city names and values
                lat='Latitude', lon='Longtitude',  # Specify the latitude and longitude columns
                #z='V2Tone',
                #size='V2Tone',  # Column containing the values for coloring
                color='V2Tone',
                size='dummy_column_for_size',
                size_max=8,
                #radius=10,  # Adjust the radius of each data point on the heatmap
                zoom=1,  # Adjust the initial zoom level of the map
                mapbox_style=map_t,  # Choose a mapbox style (e.g., 'open-street-map')
                color_continuous_scale='rdylgn',
                title='V2Tone City-based Heatmap',
                hover_data={'City':True,'Latitude':True,'Longtitude':True,'V2Tone':True,'Url':False})
    # fig.update_layout(
    #     mapbox_style=map_t,
    #     mapbox_layers=[
    #         {
    #         "below": 'traces',
    #         "sourcetype": "raster",
    #         "sourceattribution": "United States Geological Survey",
    #         "source": [
    #             "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
    #         ]
    #         }
    #     ])
    # fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    # fig.add_trace(go.Scattermapbox(
    #                     lat=cities2['Latitude'], lon=cities2['Longtitude'],  # Specify the latitude and longitude columns
    #                     #size='V2Tone',  # Column containing the values for coloring
    #                     mode="markers",
    #                     showlegend=False,
    #                     hoverinfo="skip",
    #                     marker={
    #                         "color":cities2["V2Tone"],
    #                         #"size":cities2["V2Tone"].fillna(0),
    #                         "coloraxis":"coloraxis",
    #                         "sizeref":(cities2["V2Tone"].max())/15**2,
    #                         "sizemode":"area",
    #                     },))
    fig.update_layout(clickmode='event+select')
    return fig

@app.callback(
    Output('click-data-tone', 'children'),
    Input('maptone', 'selectedData'))
def display_click_data_tone(clickData):
    return json.dumps({
        'City':clickData['points'][0]['customdata'][0],
        'Latitude & Longtitude':str(clickData['points'][0]['customdata'][1])+','+str(clickData['points'][0]['customdata'][2]),
        'V2Tone':clickData['points'][0]['customdata'][3],
        'Url':clickData['points'][0]['customdata'][4]}, indent=2)


@app.callback(Output('maptone_up', 'figure'),
              [Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'),
              Input('maptonein','value'),Input('dropdownmaptone_up', 'value')])
def update_maptone(value,start_date,end_date,location,map_t):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=cities[cities['DocumentIdentifier'].str.contains('|'.join(up_key))]

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    if location is not None and len(location)>0:
        location=location.split(",")
        org=org[org['City'].str.contains('|'.join(location))]

    org1=org.loc[:,['City','Latitude','Longtitude','V2Tone']].groupby(['City','Latitude','Longtitude'], as_index=False).mean()
    org2=org.groupby(['City','Latitude','Longtitude'])['DocumentIdentifier'].unique().apply(list).reset_index(name='Url')
    org=org1.merge(org2,how='right',on=['City','Latitude','Longtitude'])
    org['dummy_column_for_size'] = 1
    fig = px.scatter_mapbox(org,  # Dataframe with city names and values
                lat='Latitude', lon='Longtitude',  # Specify the latitude and longitude columns
                #z='V2Tone',
                #size='V2Tone',  # Column containing the values for coloring
                color='V2Tone',
                size='dummy_column_for_size',
                size_max=8,
                #radius=10,  # Adjust the radius of each data point on the heatmap
                zoom=1,  # Adjust the initial zoom level of the map
                mapbox_style=map_t,  # Choose a mapbox style (e.g., 'open-street-map')
                color_continuous_scale='rdylgn',
                title='V2Tone City-based Heatmap (Upstream)',
                hover_data={'City':True,'Latitude':True,'Longtitude':True,'V2Tone':True,'Url':False})
    fig.update_layout(clickmode='event+select')
    return fig

@app.callback(
    Output('click-data-tone_up', 'children'),
    Input('maptone_up', 'selectedData'))
def display_click_data_tone_up(clickData):
    return json.dumps({
        'City':clickData['points'][0]['customdata'][0],
        'Latitude & Longtitude':str(clickData['points'][0]['customdata'][1])+','+str(clickData['points'][0]['customdata'][2]),
        'V2Tone':clickData['points'][0]['customdata'][3],
        'Url':clickData['points'][0]['customdata'][4]}, indent=2)


@app.callback(Output('maptone_down', 'figure'),
              [Input('dropdown24', 'value'),Input('datepicker1', 'start_date'),Input('datepicker1', 'end_date'),
              Input('maptonein','value'),Input('dropdownmaptone_down', 'value')])
def update_maptone_down(value,start_date,end_date,location,map_t):
    #org=data_15[data_15['Organizations'].str.contains(input_value)]
    org=cities[cities['DocumentIdentifier'].str.contains('|'.join(down_key))]

    s=datetime.combine(date(int(start_date[0:4]),int(start_date[5:7]),int(start_date[8:10])), datetime.min.time())
    e=datetime.combine(date(int(end_date[0:4]),int(end_date[5:7]),int(end_date[8:10])), datetime.max.time())
    mask = (org['dates'] >= s) & (org['dates'] <= e)
    org=org.loc[mask]

    if location is not None and len(location)>0:
        location=location.split(",")
        org=org[org['City'].str.contains('|'.join(location))]

    org1=org.loc[:,['City','Latitude','Longtitude','V2Tone']].groupby(['City','Latitude','Longtitude'], as_index=False).mean()
    org2=org.groupby(['City','Latitude','Longtitude'])['DocumentIdentifier'].unique().apply(list).reset_index(name='Url')
    org=org1.merge(org2,how='right',on=['City','Latitude','Longtitude'])
    org['dummy_column_for_size'] = 1
    fig = px.scatter_mapbox(org,  # Dataframe with city names and values
                lat='Latitude', lon='Longtitude',  # Specify the latitude and longitude columns
                #z='V2Tone',
                #size='V2Tone',  # Column containing the values for coloring
                color='V2Tone',
                size='dummy_column_for_size',
                size_max=8,
                #radius=10,  # Adjust the radius of each data point on the heatmap
                zoom=1,  # Adjust the initial zoom level of the map
                mapbox_style=map_t,  # Choose a mapbox style (e.g., 'open-street-map')
                color_continuous_scale='rdylgn',
                title='V2Tone City-based Heatmap (Downstream)',
                hover_data={'City':True,'Latitude':True,'Longtitude':True,'V2Tone':True,'Url':False})
    fig.update_layout(clickmode='event+select')
    return fig

@app.callback(
    Output('click-data-tone_down', 'children'),
    Input('maptone_down', 'selectedData'))
def display_click_data_tone_down(clickData):
    return json.dumps({
        'City':clickData['points'][0]['customdata'][0],
        'Latitude & Longtitude':str(clickData['points'][0]['customdata'][1])+','+str(clickData['points'][0]['customdata'][2]),
        'V2Tone':clickData['points'][0]['customdata'][3],
        'Url':clickData['points'][0]['customdata'][4]}, indent=2)

if __name__ == '__main__':
    app.run_server(debug=False)
