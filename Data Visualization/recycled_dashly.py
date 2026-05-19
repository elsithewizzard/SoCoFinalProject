from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go



df = pd.read_csv("meteo_wop_10min.csv")
variable_dict = {
    'RH10m': 'Relative humidity in %',
    'p10m': 'Pressure in hPa at 10 m above ground', 
    'p_NN10m': 'Pressure in hPa at 10m above sea level',
    "T10m": "Temperature at 10m"
    }

# Initializing App:
app = Dash()

app.layout = html.Div([
    #page title
    html.H3('Davos Weather Station'),
    # Dropdown: Select graph
    html.Label('Select graph type: '), 
    dcc.Dropdown(
        options = [
            {'label': 'Scatter Plot', 'value': 'scatter'},
            {'label': 'Histogram', 'value': 'histogram'},
        ],
        value = 'scatter', #start value
        id = 'graph-selector'
    ),

    # Radio Button: Select Y Variable 
    html.Label('Select a variable: '),
    dcc.RadioItems(
        options =[
            {'label': 'Relative humidity in %', 'value': 'RH10m'},
            {'label': 'Pressure in hPa at 10 m above ground', 'value': 'p10m'},
            {'label': 'Pressure in hPa at 10m above sea level', 'value': 'p_NN10m'},
            {'label': 'Temperature at 10m', 'value': 'T10m'},
        ],
        value = 'RH10m', #start value
        id = 'variable-selector',
    ),
    #checklist mean / median
    dcc.Checklist(options = [
        {'label' :'Mean', 'value': 'mean'},
        {'label': 'Median', 'value': 'median'}
        ],
        value = ['mean'],
        id = 'descr-stats-checklist'
    ),


    # graph :)) 
    dcc.Graph(id='output-graph'),

    ################
    # range-sliders
    ################        
    # range-slider-humidity
    html.Label('Select a relative humidity (%) range:'),
    dcc.RangeSlider(min=round(df['RH10m'].min(),2),
                    max=round(df['RH10m'].max(),2),
                    value =[round(df['RH10m'].min(),2), round(df['RH10m'].max(),2)], #default range
                    id='humidity-range-slider',
                          allowCross=False,
                          updatemode='drag',
                          tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-humidity-range-slider'),

    # range-slider-ground-level-pressure
    html.Label('Select a pressure 10 m above ground level (hPa) range:'),
    dcc.RangeSlider(min=round(df['p10m'].min(),2),
                    max=round(df['p10m'].max(),2),
                    value =[round(df['p10m'].min(),2), round(df['p10m'].max(),2)], #default range
                    id='pressure-ground-range-slider',
                          allowCross=False,
                          updatemode='drag',
                          tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-pressure-ground-range-slider'),

    # range-slider-sea-level-pressure
    html.Label('Select a pressure 10m above sea level (hPa) range:'),
    dcc.RangeSlider(min=round(df['p_NN10m'].min(),2),
                    max=round(df['p_NN10m'].max(),2),
                    value =[round(df['p_NN10m'].min(),2), round(df['p_NN10m'].max(),2)], #default range
                    id='pressure-sea-range-slider',
                          allowCross=False,
                          updatemode='drag',
                          tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-pressure-sea-range-slider'),

    #range slider temperature
    html.Label('Select a temperature at 10m range:'),
    dcc.RangeSlider(min=round(df['T10m'].min(),2),
                    max=round(df['T10m'].max(),2),
                    value =[round(df['T10m'].min(),2), round(df['T10m'].max(),2)], #default range
                    id='temperature-range-slider',
                          allowCross=False,
                          updatemode='drag',
                          tooltip={"placement": "bottom", "always_visible": True}),

    html.Div(id='output-container-temperature-range-slider'),

    ])


#filter data with mask!
def filter_df(df, slider_range_hum, slider_range_gro,slider_range_sea,slider_range_temp):
    low_hum, high_hum = slider_range_hum
    low_gro, high_gro = slider_range_gro
    low_sea, high_sea = slider_range_sea
    low_temp, high_temp = slider_range_temp
    mask = (
            (df['RH10m'] >= low_hum) & (df['RH10m'] <= high_hum) & \
            (df['p10m'] >= low_gro) & (df['p10m'] <= high_gro) & \
            (df['p_NN10m'] >= low_sea) & (df['p_NN10m'] <= high_sea) & \
            (df['T10m'] >= low_temp) & (df['T10m'] <= high_temp) 
            )
    filtered_df = df[mask]
    return filtered_df

#app.callback decorator for interactive features
@app.callback(
    Output('output-graph', 'figure'), #is influenced by input1 (variable) & input2 (graph-type)
    #graph type selector inputs
    Input('variable-selector', 'value'),
    Input('graph-selector','value'),

    #slider inputs
    Input('humidity-range-slider', 'value'),
    Input('pressure-ground-range-slider', 'value'),
    Input('pressure-sea-range-slider', 'value'),
    Input('temperature-range-slider', 'value'),

    # descriptive stats
    Input('descr-stats-checklist', 'value')
)
#corresponding function: Updates graph type using callback elements
def update_graph(selected_variable,graph_type, slider_range_hum, slider_range_gro,slider_range_sea,slider_range_temp,descr_stats):    
    ylab = variable_dict[selected_variable] #label from the dictionary of variables
    filtered_df = filter_df(df, slider_range_hum, slider_range_gro,slider_range_sea,slider_range_temp) 

    if graph_type == 'scatter':
        fig = px.scatter(filtered_df, 
                         x = filtered_df['date'], 
                         y = selected_variable,
                         labels={'date':'Date', selected_variable: ylab}) 
                         
    elif graph_type == 'histogram':
        fig = px.histogram(filtered_df,
                           x='date',  
                           y=selected_variable,  
                           histfunc='avg', 
                           title=f'Histogram of {ylab} over time',
                           labels={'date': 'Date', selected_variable: ylab})
        
    if 'mean' in descr_stats:
        mean_val = filtered_df[selected_variable].mean()
        fig.add_trace(go.Scatter(x=filtered_df['date'], 
                                 y=[mean_val]*len(filtered_df), #so the df dimensions match
                                 mode='lines',
                                 name='Mean',
                                 line_color= 'red'
                                 ))
        

    if 'median' in descr_stats:
        median_val = filtered_df[selected_variable].median()
        fig.add_trace(go.Scatter(x=filtered_df['date'], 
                                 y=[median_val]*len(filtered_df), #so the df dimensions match
                                 mode='lines',
                                 name='Median',
                                 line_color= 'green'
                                 ))       
    return fig




if __name__ == '__main__':
    app.run(debug = True)