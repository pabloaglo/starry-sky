# Import packages
from dash import Dash, html, dash_table, dcc, callback, Output, Input, State
from functions import *

# Initialize the app
app = Dash()

# App layout
app.layout = [
    html.H2('Sky generator',style={"textAlign": "center"}),
    html.Hr(),
    dcc.Input(id='seed-in', type='text', placeholder='Seed (optional)',
              style={"textAlign": "center"}, debounce=True),
    html.Button('Generate sky', id='generate-button', n_clicks=0, style={"textAlign": "center"}),
    html.Br(),
    html.Label('Seed:', htmlFor='seed-out', style={"textAlign": "center"}),
    html.Div(id='seed-out', style={'margin-top': '20px',
                                   'font-weight': 'bold',
                                   'textAlign': 'center'}),
    html.Hr(),
    dash_table.DataTable(id='df-out', page_size=10, sort_action='native'),
    html.Hr(),
    html.Label('Select a map:', htmlFor='plot-select', style={'textAlign': 'center'}),
    dcc.RadioItems(options=['Star chart', 'Celestial sphere'], value='', id='plot-select',
                   style={'textAlign': 'center'}),
    html.Br(),
    html.Label('Select the limiting magnitude:', htmlFor='slide-mags',
               style={'textAlign': 'center'}),
    dcc.Slider(0, 8, 1, value=6,  id='slide-mags'),
    dcc.Graph(figure={}, id='selected-plot', style={'textAlign': 'center'}),
    html.Hr(),
    html.Label('Download your sky!   ', htmlFor='download-button', style={'textAlign': 'center'}),
    html.Button('Download sky', id='download-button', n_clicks=0, style={'textAlign': 'center'}),
    dcc.Download(id='download-sky'),
]

# Callbacks

@callback(
    [Output('df-out', 'data'),
     Output('seed-out', 'children')],
    [Input('generate-button', 'n_clicks'),
     Input('seed-in', 'value')],
    prevent_initial_call=False
)
def update_df(n_clicks, seed_in):
    if seed_in:
        seed = int(seed_in)
    else:
        seed = None

    df, seed_val = Generator(seed)
    df_data = df.to_dict('records')
        
    return df_data, seed_val

@callback(
    Output('selected-plot', 'figure'),
    [Input('plot-select', 'value'),
     Input('slide-mags', 'value')],
    State('df-out', 'data')
    )
def update_plot(plot, mag_lim, df_data):
    if df_data is None:
        return {}
    
    df_sky = pd.DataFrame(df_data)
    if plot=='Star chart':
        fig = starChart(df_sky, mag_lim)

    elif plot=='Celestial sphere':
        fig = celestialSphere(df_sky, mag_lim)

    return fig

@callback(
    Output('download-sky', 'data'),
    Input('download-button', 'n_clicks'),
    State('df-out', 'data'),
    State('seed-out', 'children')
    )
def download_sky(n_clicks, df_data, seed):
    if n_clicks > 0:
        csv = (pd.DataFrame(df_data)).to_csv(index=False)
        return dict(content=csv, filename=f'sky_{seed}.csv')
    else:
        return None
    
    

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
