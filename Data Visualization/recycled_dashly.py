from dash import Dash, dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 1. DATA LOADING & MERGING

df_reddit = pd.read_csv("games_reddit.csv") 
df_steam = pd.read_csv("steam_data.csv") # The file with price, recommendations, and playtime

# Merging on app_id
df = pd.merge(df_reddit, df_steam, on='app_id', suffixes=('', '_steam'))

# 2. PREPROCESSING FOR H1-H3
def preprocess_gaming_data(df):
    # Categorize Price for H3 (F2P vs B2P)
    df['price_category'] = df['price'].apply(lambda x: 'F2P' if x == 0 else 'B2P')
    
    # Log transformation for skewed data (essential for gaming metrics!)
    df['log_peak_ccu'] = np.log1p(df['peak_players'])
    df['log_engagement'] = np.log1p(df['engagement'])
    
    return df

df = preprocess_gaming_data(df)

# Visual Encoding Maps
price_color_map = {'F2P': 'rgba(0, 150, 255, 0.7)', 'B2P': 'rgba(255, 100, 0, 0.7)'}

# Initializing App
app = Dash(__name__)

app.layout = html.Div([
    html.H3('Steam Stats & Reddit Hype Correlation Explorer'),
    html.P('Interactive tool for analyzing the relationship between Reddit eWoM and Steam player behavior.'),

    # Master Scatter Plot (Static Target for Lasso)
    dcc.Graph(id='main-scatter-plot'),

    html.Div([
        html.Label("Select X-Axis Metric:"),
        dcc.Dropdown(
            options=[
                {'label': 'Reddit Engagement (Total Score)', 'value': 'log_engagement'},
                {'label': 'Reddit Valence (Upvote Ratio)', 'value': 'valence'},
                {'label': 'Number of Posts', 'value': 'n_posts'}
            ],
            value='log_engagement',
            id='xaxis-dropdown'
        ),

        html.Label("Filter by Pricing Model (H3):"),
        dcc.Dropdown(
            options=[{'label': i, 'value': i} for i in ['All', 'F2P', 'B2P']],
            value='All',
            id='price-dropdown'
        ),
    ], style={'width': '30%', 'padding': '20px'}),

    # Interactive Plot
    dcc.Graph(id='interactive-gaming-scatter')
])

# CALLBACK 1: Update Interactive Plot
@app.callback(
    Output('interactive-gaming-scatter', 'figure'),
    Input('xaxis-dropdown', 'value'),
    Input('price-dropdown', 'value')
)
def update_interactive_scatter(xaxis_col, price_filter):
    dff = df.copy()
    if price_filter != 'All':
        dff = dff[dff['price_category'] == price_filter]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dff[xaxis_col],
        y=dff['log_peak_ccu'],
        mode='markers',
        hovertext=dff['game_name'],
        marker=dict(
            color=[price_color_map[cat] for cat in dff['price_category']],
            size=10,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        showlegend=False
    ))

    # Add dummy legend for F2P/B2P
    for cat, color in price_color_map.items():
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers',
                                 marker=dict(color=color), name=cat))

    fig.update_layout(
        title=f"Correlation: {xaxis_col} vs Peak CCU (Log Scale)",
        xaxis_title=xaxis_col,
        yaxis_title="Peak CCU (Log Scale)",
        template='plotly_white',
        dragmode='lasso'
    )
    return fig

# CALLBACK 2: Lasso Selection Logic
@app.callback(
    Output('main-scatter-plot', 'figure'),
    Input('interactive-gaming-scatter', 'selectedData'),
    Input('xaxis-dropdown', 'value')
)
def update_side_scatter(selected_data, xaxis_col):
    # Base Plot (H1 default: Engagement vs CCU)
    fig = px.scatter(df, x=xaxis_col, y="log_peak_ccu", 
                     hover_name="game_name", color="price_category",
                     color_discrete_map=price_color_map,
                     title="Global Overview (High Opacity = Selected)")
    
    fig.update_traces(marker=dict(size=8, opacity=0.1)) # Default low opacity

    if selected_data and selected_data.get('points'):
        selected_names = [p['hovertext'] for p in selected_data['points']]
        # Highlight selected points
        fig.add_trace(go.Scatter(
            x=df[df['game_name'].isin(selected_names)][xaxis_col],
            y=df[df['game_name'].isin(selected_names)]['log_peak_ccu'],
            mode='markers',
            marker=dict(color='yellow', size=12, line=dict(width=2, color='black')),
            name='Selected Games'
        ))

    fig.update_layout(template='plotly_white')
    return fig

if __name__ == '__main__':
    app.run(debug=True)