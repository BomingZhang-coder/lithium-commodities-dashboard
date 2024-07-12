import pandas as pd
from pymongo import MongoClient
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import base64
from io import BytesIO
from IPython.display import display, HTML
from dash import dash_table
from transformers import pipeline
import nltk
from nltk.corpus import stopwords
import re

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Initialize the summarization pipeline
summarizer = pipeline("summarization")

# Function to get cleaned data from MongoDB
def get_cleaned_data():
    uri = 'mongodb+srv://botongyuan00:Wojiaoybt1220@cluster0.okmf3dv.mongodb.net/lithium?retryWrites=true&w=majority&connectTimeoutMS=30000&socketTimeoutMS=30000'
    client = MongoClient(uri)
    db = client.lithium
    collection = db.cleaned_data
    data = pd.DataFrame(list(collection.find()))
    return data

# Function to parse V2Locations column
def parse_v2locations(v2locations):
    locations = []
    if pd.notnull(v2locations):
        loc_entries = v2locations.split(';')
        for entry in loc_entries:
            parts = entry.split('#')
            if len(parts) >= 7:
                location_type = int(parts[0])
                location_name = parts[1]
                country_code = parts[2]
                adm1_code = parts[3]
                latitude = float(parts[5])
                longitude = float(parts[6])
                locations.append({
                    'Location Type': location_type,
                    'Location Name': location_name,
                    'Country Code': country_code,
                    'ADM1 Code': adm1_code,
                    'Latitude': latitude,
                    'Longitude': longitude
                })
    return locations

# Function to generate a global map
def generate_global_map(data):
    # Extract unique V2Tone documents
    data = data.drop_duplicates(subset='V2Tone', keep='first')
    
    # Parse V2Locations
    all_locations = []
    for _, row in data.iterrows():
        v2locations = row['V2Locations']
        locations = parse_v2locations(v2locations)
        all_locations.extend(locations)
    
    # Create DataFrame from locations
    locations_df = pd.DataFrame(all_locations)
    locations_df.columns = ['Location Type', 'Location Name', 'Country Code', 'ADM1 Code', 'Latitude', 'Longitude']
    
    # Aggregate by Location to get the frequency
    locations_df['Frequency'] = locations_df.groupby(['Latitude', 'Longitude'])['Latitude'].transform('count')
    locations_df = locations_df.drop_duplicates(subset=['Latitude', 'Longitude'])
    
    # Create the map
    fig = px.scatter_geo(
        locations_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='Location Name',
        size='Frequency',  # Size of the dot represents frequency
        color='Frequency',  # Color of the dot represents frequency
        size_max=15,
        title='Global Map of News Frequency'
    )
    
    fig.update_geos(
        projection_type="natural earth",
        showcoastlines=True,
        coastlinecolor="black",
        showland=True,
        landcolor="limegreen",
        showocean=True,
        oceancolor="aqua"
    )
    
    return fig

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
                    html.Div(id='wordcloud-3hours')
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
            ]),
            html.Div([
                html.H2("Theme Distribution and Scatter Plot"),
                dcc.Dropdown(
                    id='theme-dropdown-3hours',
                    placeholder="Select a theme",
                ),
                dcc.Graph(id='theme-distribution-3hours'),
                dcc.Graph(id='theme-scatter-3hours'),
                html.H2("DataFrame for Selected Theme"),
                html.Div(id='theme-table-3hours')
            ]),
            html.Div([
                html.H2("Global News Frequency Map"),
                dcc.Graph(id='global-map-3hours')
            ]),
            html.Div([
                html.H2("Top 5 Most Negative V2Tone Summaries"),
                html.Div(id='negative-summaries-3hours')
            ]),
            html.Div([
                html.H2("Top 5 Most Positive V2Tone Summaries"),
                html.Div(id='positive-summaries-3hours')
            ]),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            html.H2("Data Refreshed Every 30 Minutes"),
            dcc.Interval(
                id='interval-30minutes',
                interval=30*60*1000,  # in milliseconds
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
                    html.Div(id='wordcloud-30minutes')
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
            ]),
            html.Div([
                html.H2("Theme Distribution and Scatter Plot"),
                dcc.Dropdown(
                    id='theme-dropdown-30minutes',
                    placeholder="Select a theme",
                ),
                dcc.Graph(id='theme-distribution-30minutes'),
                dcc.Graph(id='theme-scatter-30minutes'),
                html.H2("DataFrame for Selected Theme"),
                html.Div(id='theme-table-30minutes')
            ]),
            html.Div([
                html.H2("Global News Frequency Map"),
                dcc.Graph(id='global-map-30minutes')
            ]),
            html.Div([
                html.H2("Top 5 Most Negative V2Tone Summaries"),
                html.Div(id='negative-summaries-30minutes')
            ]),
            html.Div([
                html.H2("Top 5 Most Positive V2Tone Summaries"),
                html.Div(id='positive-summaries-30minutes')
            ]),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'})
    ]),
])

def generate_wordcloud(data):
    text = ' '.join(data)
    if not text.strip():
        return None  # Return None if there is no text to generate a word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
    
    # Save the wordcloud image to a BytesIO object
    img_bytes = BytesIO()
    wordcloud.to_image().save(img_bytes, format='PNG')
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

def generate_table(data):
    table = dash_table.DataTable(
        columns=[{"name": i, "id": i, "presentation": "markdown" if i == "DocumentIdentifier" else "input"} for i in data.columns],
        data=data.to_dict('records'),
        page_size=5,  # Display 5 rows per page
        style_table={'overflowX': 'auto'},
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'minWidth': '150px', 'width': '150px', 'maxWidth': '150px',
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'DocumentIdentifier'},
                'textAlign': 'left',
            },
        ],
        markdown_options={"link_target": "_blank"},
    )
    return table

def clean_text(text):
    text = re.sub(r'\@w+|\#','', text)
    text = re.sub(r'\d+', '', text)
    text = text.lower()
    text_tokens = text.split()
    filtered_words = [word for word in text_tokens if word not in stop_words]
    return " ".join(filtered_words)

def get_summaries(data):
    data['cleaned_text'] = data['DocumentIdentifier'].apply(clean_text)
    summaries = []
    for text in data['cleaned_text']:
        try:
            summary = summarizer(text, max_length=50, min_length=25, do_sample=False)[0]['summary_text']
        except Exception as e:
            summary = text[:50]  # Fallback to a truncated version if summarization fails
        summaries.append(summary)
    return summaries

@app.callback(
    [Output('bar-chart-3hours', 'figure'),
     Output('wordcloud-3hours', 'children'),
     Output('tree-plot-3hours', 'figure'),
     Output('spider-plot-3hours', 'figure'),
     Output('dispersion-plot-3hours', 'figure'),
     Output('heatmap-plot-3hours', 'figure'),
     Output('theme-dropdown-3hours', 'options'),
     Output('theme-distribution-3hours', 'figure'),
     Output('theme-scatter-3hours', 'figure'),
     Output('theme-table-3hours', 'children'),
     Output('global-map-3hours', 'figure'),
     Output('negative-summaries-3hours', 'children'),
     Output('positive-summaries-3hours', 'children')],
    [Input('tone-selection-3hours', 'value'),
     Input('interval-3hours', 'n_intervals'),
     Input('theme-dropdown-3hours', 'value')]
)
def update_visualizations_3hours(selected_tone, n_intervals, selected_theme):
    print("Updating visualizations for 3 hours")
    lithium_data = get_cleaned_data()
    
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
    if wordcloud_image is None:
        wordcloud_content = html.Div("No available data", style={'textAlign': 'center', 'color': 'red', 'fontSize': 20})
    else:
        wordcloud_content = html.Img(src=f'data:image/png;base64,{wordcloud_image}')
    
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
    
    # Theme Dropdown Options
    theme_options = [{'label': theme, 'value': theme} for theme in lithium_data['ActualThemes'].unique()]

    # Theme Distribution and Scatter Plot
    if selected_theme:
        theme_data = lithium_data[lithium_data['ActualThemes'] == selected_theme]
        theme_distribution_fig = px.histogram(theme_data, x='V2Tone', title=f'Distribution of V2Tone for {selected_theme}')
        theme_scatter_fig = px.scatter(theme_data, x='DATE', y='V2Tone', title=f'Scatter Plot of V2Tone over time for {selected_theme}')
        theme_table = theme_data[['ActualThemes', 'V2Tone', 'DocumentIdentifier']]
        theme_table_html = generate_table(theme_table)
    else:
        theme_distribution_fig = go.Figure()
        theme_scatter_fig = go.Figure()
        theme_table_html = "Please select a theme to view the data."

    # Global Map
    global_map_fig = generate_global_map(lithium_data)
    
    # Summarize the top 5 most negative and positive V2Tone documents
    top_5_negative = lithium_data.drop_duplicates(subset='V2Tone').nsmallest(5, 'V2Tone')
    top_5_positive = lithium_data.drop_duplicates(subset='V2Tone').nlargest(5, 'V2Tone')
    
    negative_summaries = get_summaries(top_5_negative)
    positive_summaries = get_summaries(top_5_positive)
    
    negative_summaries_content = [html.P(summary) for summary in negative_summaries]
    positive_summaries_content = [html.P(summary) for summary in positive_summaries]

    return (bar_fig, wordcloud_content, tree_fig, radar_fig, dispersion_fig, heatmap_fig, theme_options, 
            theme_distribution_fig, theme_scatter_fig, theme_table_html, global_map_fig, 
            negative_summaries_content, positive_summaries_content)

@app.callback(
    [Output('bar-chart-30minutes', 'figure'),
     Output('wordcloud-30minutes', 'children'),
     Output('tree-plot-30minutes', 'figure'),
     Output('spider-plot-30minutes', 'figure'),
     Output('dispersion-plot-30minutes', 'figure'),
     Output('heatmap-plot-30minutes', 'figure'),
     Output('theme-dropdown-30minutes', 'options'),
     Output('theme-distribution-30minutes', 'figure'),
     Output('theme-scatter-30minutes', 'figure'),
     Output('theme-table-30minutes', 'children'),
     Output('global-map-30minutes', 'figure'),
     Output('negative-summaries-30minutes', 'children'),
     Output('positive-summaries-30minutes', 'children')],
    [Input('tone-selection-30minutes', 'value'),
     Input('interval-30minutes', 'n_intervals'),
     Input('theme-dropdown-30minutes', 'value')]
)
def update_visualizations_30minutes(selected_tone, n_intervals, selected_theme):
    print("Updating visualizations for 30 minutes")
    lithium_data = get_cleaned_data()
    
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
    if wordcloud_image is None:
        wordcloud_content = html.Div("No available data", style={'textAlign': 'center', 'color': 'red', 'fontSize': 20})
    else:
        wordcloud_content = html.Img(src=f'data:image/png;base64,{wordcloud_image}')
    
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
    
    # Theme Dropdown Options
    theme_options = [{'label': theme, 'value': theme} for theme in lithium_data['ActualThemes'].unique()]

    # Theme Distribution and Scatter Plot
    if selected_theme:
        theme_data = lithium_data[lithium_data['ActualThemes'] == selected_theme]
        theme_distribution_fig = px.histogram(theme_data, x='V2Tone', title=f'Distribution of V2Tone for {selected_theme}')
        theme_scatter_fig = px.scatter(theme_data, x='DATE', y='V2Tone', title=f'Scatter Plot of V2Tone over time for {selected_theme}')
        theme_table = theme_data[['ActualThemes', 'V2Tone', 'DocumentIdentifier']]
        theme_table_html = generate_table(theme_table)
    else:
        theme_distribution_fig = go.Figure()
        theme_scatter_fig = go.Figure()
        theme_table_html = "Please select a theme to view the data."

    # Global Map
    global_map_fig = generate_global_map(lithium_data)
    
    # Summarize the top 5 most negative and positive V2Tone documents
    top_5_negative = lithium_data.drop_duplicates(subset='V2Tone').nsmallest(5, 'V2Tone')
    top_5_positive = lithium_data.drop_duplicates(subset='V2Tone').nlargest(5, 'V2Tone')
    
    negative_summaries = get_summaries(top_5_negative)
    positive_summaries = get_summaries(top_5_positive)
    
    negative_summaries_content = [html.P(summary) for summary in negative_summaries]
    positive_summaries_content = [html.P(summary) for summary in positive_summaries]

    return (bar_fig, wordcloud_content, tree_fig, radar_fig, dispersion_fig, heatmap_fig, theme_options, 
            theme_distribution_fig, theme_scatter_fig, theme_table_html, global_map_fig, 
            negative_summaries_content, positive_summaries_content)

def display_link():
    ip = 'localhost'  # Change to your local IP if needed
    port = 8054
    url = f'http://{ip}:{port}'
    display(HTML(f'<a href="{url}" target="_blank">Click here to open the Dash app</a>'))

# Run the app and display the link
if __name__ == '__main__':
    display_link()
    app.run_server(debug=True, host='0.0.0.0', port=8056)
