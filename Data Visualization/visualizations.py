import pandas as pd
import os
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Load dataset
basepath = os.getcwd()
file_path = os.path.join(basepath, "Analysis", "data", "games_clean_summary.csv")
df = pd.read_csv(file_path)

variable_dict = {
    'peak_players': 'Historical Peak Concurrent Players (Month)',
    'avg_players': 'Average Monthly Players', 
    'engagement': 'r/gaming Engagement Volume (Score)',
    'n_posts': 'Number of Reddit Posts (r/gaming)'
}

# Initializing App:
app = Dash()

app.layout = html.Div([
    html.H3('Steam & r/gaming Hype Dashboard'),
    
    html.Label('Select graph type: '), 
    dcc.Dropdown(
        options = [
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Histogram', 'value': 'histogram'},
        ],
        value = 'scatter', 
        id = 'graph-selector'
    ),

    html.Label('Select a variable: '),
    dcc.RadioItems(
        options =[
            {'label': 'Historical Peak Concurrent Players (Month)', 'value': 'peak_players'},
            {'label': 'Average Monthly Players', 'value': 'avg_players'},
            {'label': 'r/gaming Engagement Volume (Score)', 'value': 'engagement'},
            {'label': 'Number of Reddit Posts (r/gaming)', 'value': 'n_posts'},
        ],
        value = 'peak_players', 
        id = 'variable-selector',
    ),

    dcc.Checklist(options = [
        {'label' :'Mean', 'value': 'mean'},
        {'label': 'Median', 'value': 'median'}
        ],
        value = ['mean'],
        id = 'descr-stats-checklist'
    ),

    dcc.Graph(id='output-graph'),

    # range-slider-peak-players
    html.Label('Select a Peak Players range:'),
    dcc.RangeSlider(min=round(df['peak_players'].min(),2),
                    max=round(df['peak_players'].max(),2),
                    value =[round(df['peak_players'].min(),2), round(df['peak_players'].max(),2)], 
                    id='peak-players-range-slider',
                    allowCross=False,
                    updatemode='drag',
                    tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-peak-players-range-slider'),

    # range-slider-avg-players
    html.Label('Select an Average Players range:'),
    dcc.RangeSlider(min=round(df['avg_players'].min(),2),
                    max=round(df['avg_players'].max(),2),
                    value =[round(df['avg_players'].min(),2), round(df['avg_players'].max(),2)], 
                    id='avg-players-range-slider',
                    allowCross=False,
                    updatemode='drag',
                    tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-avg-players-range-slider'),

    # range-slider-engagement
    html.Label('Select an (r/gaming) Engagement Score range:'),
    dcc.RangeSlider(min=round(df['engagement'].min(),2),
                    max=round(df['engagement'].max(),2),
                    value =[round(df['engagement'].min(),2), round(df['engagement'].max(),2)], 
                    id='engagement-range-slider',
                    allowCross=False,
                    updatemode='drag',
                    tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-engagement-range-slider'),

    # range-slider-n-posts
    html.Label('Select a Post Count range:'),
    dcc.RangeSlider(min=round(df['n_posts'].min(),2),
                    max=round(df['n_posts'].max(),2),
                    value =[round(df['n_posts'].min(),2), round(df['n_posts'].max(),2)], 
                    id='n-posts-range-slider',
                    allowCross=False,
                    updatemode='drag',
                    tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-n-posts-range-slider'),

])

def filter_df(df, slider_range_peak, slider_range_avg, slider_range_eng, slider_range_posts):
    low_peak, high_peak = slider_range_peak
    low_avg, high_avg = slider_range_avg
    low_eng, high_eng = slider_range_eng
    low_posts, high_posts = slider_range_posts
    mask = (
            (df['peak_players'] >= low_peak) & (df['peak_players'] <= high_peak) & \
            (df['avg_players'] >= low_avg) & (df['avg_players'] <= high_avg) & \
            (df['engagement'] >= low_eng) & (df['engagement'] <= high_eng) & \
            (df['n_posts'] >= low_posts) & (df['n_posts'] <= high_posts) 
            )
    filtered_df = df[mask]
    return filtered_df

@app.callback(
    Output('output-graph', 'figure'), 
    Input('variable-selector', 'value'),
    Input('graph-selector','value'),
    Input('peak-players-range-slider', 'value'),
    Input('avg-players-range-slider', 'value'),
    Input('engagement-range-slider', 'value'),
    Input('n-posts-range-slider', 'value'),
    Input('descr-stats-checklist', 'value')
)

def update_graph(selected_variable, graph_type, slider_range_peak, slider_range_avg, slider_range_eng, slider_range_posts, descr_stats):    
    ylab = variable_dict[selected_variable] 
    filtered_df = filter_df(df, slider_range_peak, slider_range_avg, slider_range_eng, slider_range_posts) 

    # SAFETY CHECK: If sliders filter out everything, return an empty figure so it doesn't crash
    if filtered_df.empty:
        return go.Figure(layout=go.Layout(title="No data matches current slider filters."))

    if graph_type == 'scatter':
        # FIX: Put Engagement on X, Selected Variable on Y, and use hover to show the game name!
        fig = px.scatter(filtered_df, 
                         x = 'engagement', 
                         y = selected_variable,
                         hover_name = 'game_name',
                         labels={'engagement': 'r/gaming Engagement Volume (Score)', selected_variable: ylab},
                         title=f'r/gaming Engagement vs {ylab}') 
                         
    elif graph_type == 'histogram':
        # FIX: Show the distribution of the metric itself rather than charting by game name
        fig = px.histogram(filtered_df,
                           x = selected_variable,  
                           nbins = 30,
                           title = f'Overall Distribution of {ylab}',
                           labels = {selected_variable: ylab})
        
    # Stats overlays require a continuous numeric index to span across cleanly
    if 'mean' in descr_stats and graph_type == 'scatter':
        mean_val = filtered_df[selected_variable].mean()
        fig.add_trace(go.Scatter(x=filtered_df['engagement'], 
                                 y=[mean_val]*len(filtered_df), 
                                 mode='lines',
                                 name='Mean',
                                 line=dict(color='red', dash='dash')))
        
    if 'median' in descr_stats and graph_type == 'scatter':
        median_val = filtered_df[selected_variable].median()
        fig.add_trace(go.Scatter(x=filtered_df['engagement'], 
                                 y=[median_val]*len(filtered_df), 
                                 mode='lines',
                                 name='Median',
                                 line=dict(color='green', dash='dot'))).update_layout(hovermode='closest')       
    return fig

if __name__ == '__main__':
    app.run(debug = True)