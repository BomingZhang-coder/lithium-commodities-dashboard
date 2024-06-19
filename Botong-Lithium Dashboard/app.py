import pandas as pd
from pymongo import MongoClient
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO
from IPython.display import display, HTML

def get_mongo_data():
    uri = 'mongodb+srv://botongyuan00:Wojiaoybt1220@cluster0.okmf3dv.mongodb.net/'
    client = MongoClient(uri)
    db = client.lithium
    collection = db.refresh_per_15_min
    data = pd.DataFrame(list(collection.find()))
    return data

def clean_and_process_data(data):
    data['DATE'] = pd.to_datetime(data['DATE'], format='%Y%m%d%H%M%S')
    columns_to_keep = ['DATE', 'V2Tone', 'FinalThemes']
    data = data[columns_to_keep]
    data = clean_column(data, 'FinalThemes')
    data['ActualThemes'] = data['FinalThemes'].str.split(',')
    data = data.explode('ActualThemes')
    data['ActualThemes'] = data['ActualThemes'].str.strip()
    return data

def clean_column(df, column):
    df[column] = df[column].str.replace('[', '', regex=False)
    df[column] = df[column].str.replace(']', '', regex=False)
    df[column] = df[column].str.replace("'", '', regex=False)
    df[column] = df[column].str.replace('"', '', regex=False)
    return df

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1("Lithium Data Dashboard"),
    
    html.Div([
        html.Div([
            html.H2("Data Refreshed Every 3 Hours"),
            dcc.Interval(
                id='interval-3hours',
                interval=3*60*60*1000,  # in milliseconds
                n_intervals=0
            ),
            dcc.RadioItems(
                id='tone-selection-3hours',
                options=[
                    {'label': 'Positive Tone', 'value': 'positive'},
                    {'label': 'Negative Tone', 'value': 'negative'},
                    {'label': 'Neutral Tone', 'value': 'neutral'}
                ],
                value='positive',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Tabs([
                dcc.Tab(label='Bar Chart', children=[
                    dcc.Graph(id='bar-chart-3hours')
                ]),
                dcc.Tab(label='Treemap', children=[
                    dcc.Graph(id='tree-plot-3hours')
                ]),
                dcc.Tab(label='Word Cloud', children=[
                    html.Div([
                        html.H3("Word Cloud"),
                        html.Img(id='wordcloud-3hours')
                    ])
                ])
            ]),
            html.Div([
                html.H2("Spider Plot of V2Tone by Theme"),
                dcc.Graph(id='spider-plot-3hours')
            ]),
            html.Div([
                html.H2("Dispersion Plot of V2Tone and Themes"),
                dcc.Graph(id='dispersion-plot-3hours')
            ]),
            html.Div([
                html.H2("Heatmap of V2Tone by Theme"),
                dcc.Graph(id='heatmap-plot-3hours')
            ])
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H2("Data Refreshed Every 30 Minutes"),
            dcc.Interval(
                id='interval-30minutes',
                #interval=30*60*1000, # in milliseconds
                interval=30*60*1000,
                n_intervals=0
            ),
            dcc.RadioItems(
                id='tone-selection-30minutes',
                options=[
                    {'label': 'Positive Tone', 'value': 'positive'},
                    {'label': 'Negative Tone', 'value': 'negative'},
                    {'label': 'Neutral Tone', 'value': 'neutral'}
                ],
                value='positive',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Tabs([
                dcc.Tab(label='Bar Chart', children=[
                    dcc.Graph(id='bar-chart-30minutes')
                ]),
                dcc.Tab(label='Treemap', children=[
                    dcc.Graph(id='tree-plot-30minutes')
                ]),
                dcc.Tab(label='Word Cloud', children=[
                    html.Div([
                        html.H3("Word Cloud"),
                        html.Img(id='wordcloud-30minutes')
                    ])
                ])
            ]),
            html.Div([
                html.H2("Spider Plot of V2Tone by Theme"),
                dcc.Graph(id='spider-plot-30minutes')
            ]),
            html.Div([
                html.H2("Dispersion Plot of V2Tone and Themes"),
                dcc.Graph(id='dispersion-plot-30minutes')
            ]),
            html.Div([
                html.H2("Heatmap of V2Tone by Theme"),
                dcc.Graph(id='heatmap-plot-30minutes')
            ])
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ])
])

def generate_wordcloud(data):
    text = ' '.join(data)
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    img = wordcloud.to_array()
    plt.figure(figsize=(10, 5))
    plt.imshow(img, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)
    
    # Save the wordcloud image to a BytesIO object
    img_bytes = BytesIO()
    plt.savefig(img_bytes, format='PNG')
    img_bytes.seek(0)
    return base64.b64encode(img_bytes.getvalue()).decode()

def generate_heatmap(data):
    org = data[['ActualThemes', 'V2Tone']]
    new = org['ActualThemes'].str.split(',', expand=True).stack().reset_index(level=1, drop=True)
    org = org.drop(columns=['ActualThemes']).join(new.rename('Themes'))
    
    # Define bins
    bins = [
        (-100, -5), (-5, -4), (-4, -3), (-3, -2), (-2, -1), (-1, 0), 
        (0.01, 1), (1.01, 2), (2.01, 3), (3.01, 4), (4.01, 5), (5, 100)
    ]
    labels = [
        'Lesser than -5', '-5 to -4', '-4 to -3', '-3 to -2', '-2 to -1', '-1 to 0', 
        '0.01 to 1', '1.01 to 2', '2.01 to 3', '3.01 to 4', '4.01 to 5', 'Greater than 5'
    ]
    
    output = pd.DataFrame()
    output['V2Tone'] = org['V2Tone'].values
    output['Themes'] = org['Themes'].values
    output['new'] = output['V2Tone'].astype(str) + output['Themes']
    
    heatmap_data = pd.DataFrame(index=output['Themes'].unique(), columns=labels).fillna(0)
    
    for (low, high), label in zip(bins, labels):
        temp = output[output['V2Tone'].between(low, high, inclusive='both')]
        count = temp.groupby('Themes').size()
        heatmap_data[label] = count
    
    heatmap_data = heatmap_data.fillna(0)
    
    fig = px.imshow(heatmap_data.T, aspect='auto', color_continuous_scale="Teal")
    fig.update_layout(xaxis_title='Themes', yaxis_title='V2Tone Range')
    
    return fig

@app.callback(
    [Output('bar-chart-3hours', 'figure'),
     Output('wordcloud-3hours', 'src'),
     Output('tree-plot-3hours', 'figure'),
     Output('spider-plot-3hours', 'figure'),
     Output('dispersion-plot-3hours', 'figure'),
     Output('heatmap-plot-3hours', 'figure')],
    [Input('tone-selection-3hours', 'value'),
     Input('interval-3hours', 'n_intervals')]
)
def update_visualizations_3hours(selected_tone, n_intervals):
    lithium_data = get_mongo_data()
    lithium_data = clean_and_process_data(lithium_data)
    
    if selected_tone == 'positive':
        filtered_data = lithium_data[lithium_data['V2Tone'] > 0]
    elif selected_tone == 'negative':
        filtered_data = lithium_data[lithium_data['V2Tone'] < 0]
    else:
        filtered_data = lithium_data[lithium_data['V2Tone'] == 0]
    
    # Remove empty themes
    filtered_data = filtered_data[filtered_data['ActualThemes'].str.strip() != '']
    
    # Bar Chart
    theme_counts = filtered_data['ActualThemes'].value_counts().reset_index()
    theme_counts.columns = ['Theme', 'Count']
    top_10_themes = theme_counts.head(10)
    
    bar_fig = px.bar(top_10_themes, x='Count', y='Theme', orientation='h', title='Top 10 Most frequently used themes')
    bar_fig.update_traces(marker_color='darkblue')
    bar_fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # Word Cloud
    wordcloud_image = generate_wordcloud(filtered_data['ActualThemes'].dropna().values)
    
    # Tree Plot
    tree_fig = px.treemap(theme_counts, path=['Theme'], values='Count')
    
    # Spider Plot
    spider_filtered_data = lithium_data
    unique_themes = spider_filtered_data['ActualThemes'].unique()
    radar_fig = go.Figure()

    for theme in unique_themes:
        theme_data = spider_filtered_data[spider_filtered_data['ActualThemes'] == theme]
        radar_fig.add_trace(go.Scatterpolar(
            r=theme_data['V2Tone'],
            theta=[theme] * len(theme_data),
            name=theme
        ))

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        showlegend=True
    )
    
    # Dispersion Plot
    dispersion_fig = px.scatter(lithium_data, x='ActualThemes', y='V2Tone')

    # Heatmap Plot
    heatmap_fig = generate_heatmap(lithium_data)
    
    return bar_fig, f'data:image/png;base64,{wordcloud_image}', tree_fig, radar_fig, dispersion_fig, heatmap_fig

@app.callback(
    [Output('bar-chart-30minutes', 'figure'),
     Output('wordcloud-30minutes', 'src'),
     Output('tree-plot-30minutes', 'figure'),
     Output('spider-plot-30minutes', 'figure'),
     Output('dispersion-plot-30minutes', 'figure'),
     Output('heatmap-plot-30minutes', 'figure')],
    [Input('tone-selection-30minutes', 'value'),
     Input('interval-30minutes', 'n_intervals')]
)
def update_visualizations_30minutes(selected_tone, n_intervals):
    lithium_data = get_mongo_data()
    lithium_data = clean_and_process_data(lithium_data)
    
    if selected_tone == 'positive':
        filtered_data = lithium_data[lithium_data['V2Tone'] > 0]
    elif selected_tone == 'negative':
        filtered_data = lithium_data[lithium_data['V2Tone'] < 0]
    else:
        filtered_data = lithium_data[lithium_data['V2Tone'] == 0]
    
    # Remove empty themes
    filtered_data = filtered_data[filtered_data['ActualThemes'].str.strip() != '']
    
    # Bar Chart
    theme_counts = filtered_data['ActualThemes'].value_counts().reset_index()
    theme_counts.columns = ['Theme', 'Count']
    top_10_themes = theme_counts.head(10)
    
    bar_fig = px.bar(top_10_themes, x='Count', y='Theme', orientation='h', title='Top 10 Most frequently used themes')
    bar_fig.update_traces(marker_color='darkblue')
    bar_fig.update_layout(yaxis={'categoryorder':'total ascending'})
    
    # Word Cloud
    wordcloud_image = generate_wordcloud(filtered_data['ActualThemes'].dropna().values)
    
    # Tree Plot
    tree_fig = px.treemap(theme_counts, path=['Theme'], values='Count')
    
    # Spider Plot
    spider_filtered_data = lithium_data
    unique_themes = spider_filtered_data['ActualThemes'].unique()
    radar_fig = go.Figure()

    for theme in unique_themes:
        theme_data = spider_filtered_data[spider_filtered_data['ActualThemes'] == theme]
        radar_fig.add_trace(go.Scatterpolar(
            r=theme_data['V2Tone'],
            theta=[theme] * len(theme_data),
            name=theme
        ))

    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        showlegend=True
    )
    
    # Dispersion Plot
    dispersion_fig = px.scatter(lithium_data, x='ActualThemes', y='V2Tone')

    # Heatmap Plot
    heatmap_fig = generate_heatmap(lithium_data)
    
    return bar_fig, f'data:image/png;base64,{wordcloud_image}', tree_fig, radar_fig, dispersion_fig, heatmap_fig

def display_link():
    ip = 'localhost'  # Change to your local IP if needed
    port = 8054
    url = f'http://{ip}:{port}'
    display(HTML(f'<a href="{url}" target="_blank">Click here to open the Dash app</a>'))

# Run the app and display the link
if __name__ == '__main__':
    display_link()
    app.run_server(debug=True, host='0.0.0.0', port=8054)
