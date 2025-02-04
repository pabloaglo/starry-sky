# Libraries

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import plotly.graph_objects as go

from plotly.subplots import make_subplots

# Constants

best_lambda = 1.1421
scale = 1/best_lambda

max_mag_rand = 8

# Functions

def haminsec(x):
    ''' Write a sexagesimal angle in format HH/MM/SS'''
    k1= int(x/15)
    k2= (abs(x/15)-abs(k1))*60
    k3= int(k2)
    k4= (abs(k2)-abs(k3))*60
    return (str(k1)+"h "+str(k3)+"m "+str(f'{k4:.2f}')+"s ")

def gaminsec(x):
    ''' Write a sexagesimal angle in format ° / ' / " '''
    k1=int(x)
    k2=(abs(x)-abs(k1))*60
    k3=int(k2)
    k4=(abs(k2)-abs(k3))*60
    return (str(k1)+"° "+str(k3)+"' "+str(f'{k4:.2f}')+"'' ")

def Generator(seed=None):
    '''
    Generates a catalogue with random equatorial coordinates. 
    The apparent magnitudes follow the same exponential distribution as
    the stars on out sky (the best scale value was obtained with an 
    exponential fit of the stars with mag < 8 on the Hipparcos catalogue.

    '''
    No = int(4e4)
    if seed == None:
        seed=np.random.randint(1000000000000,9999999999999)

    rng = np.random.default_rng(seed)

    RAs = np.degrees(rng.uniform(0,2*np.pi, No))
    DECs = [np.degrees(np.arccos(1-2*xi))-90 for xi in rng.uniform(0,1,No)]
    Vmags = rng.exponential(scale, No)*(-1) + max_mag_rand
    ids = np.arange(1,No+1,1)
    
    df = pd.DataFrame({'ID': ids, 'RA': RAs, 'DEC': DECs, 'Vmag': Vmags})
    
    return df, seed

# Plots

def starChart(df, mag_lim=6):
    cond_mag = df.Vmag < mag_lim
    cond_north = df.DEC > 0
    cond_south = df.DEC < 0

    hover_text = pd.Series([f'RA: {haminsec(ra)}<br>DEC: {gaminsec(dec)}<br>mag: {mag:.2f}'
                           for ra, dec, mag in zip(df.RA, df.DEC, df.Vmag)])

    min_mag = np.min(df.Vmag) # Minimum apparent mag in your data
    max_mag = np.max(df.Vmag)

    sizes = (max_mag-df.Vmag)/(max_mag-min_mag)*5
    
    # Create subplots with polar domains explicitly
    fig = make_subplots(
        rows=1,
        cols=2,
        specs=[[{'type': 'polar'}, {'type': 'polar'}]],
        subplot_titles=('Northern Hemisphere', 'Southern Hemisphere'),
        horizontal_spacing = 0.0,
    )

    fig.add_trace(
        go.Scatterpolar(
        theta=df.RA[cond_north][cond_mag],
        r=np.abs(90 - np.abs(df.DEC[cond_north][cond_mag])),
        mode='markers',
        marker=dict(
            size=sizes[cond_north][cond_mag],
            color='white',
        ),
        showlegend=False,
        hoverinfo='text',
        hovertext=hover_text[cond_north][cond_mag],
        ), row=1, col=1
    )

    fig.add_trace(
        go.Scatterpolar(
        theta=df.RA[cond_south][cond_mag],
        r=np.abs(90 - np.abs(df.DEC[cond_south][cond_mag])),
        mode='markers',
        marker=dict(
            size=sizes[cond_south][cond_mag],
            color='white',
        ),
        showlegend=False,
        hoverinfo='text',
        hovertext=hover_text[cond_south][cond_mag],
        ), row=1, col=2
    )

    fig.update_layout(
        polar1=dict(
            domain=dict(x=[0, 0.5]),  # Left half
            bgcolor='black',
            angularaxis=dict(
                tickmode='array',
                tickvals=np.arange(0, 360, 45),
                ticktext=[f'{tick} h' for tick in np.arange(0, 24, 3)],
                direction="clockwise",
                rotation=00,
                gridcolor='#2f2f2f',
                gridwidth=0.5,
            ),
            radialaxis=dict(
                range=[0, 90],
                showline=False,
                ticks='',
                tickvals=np.arange(10, 91, 10),
                ticktext=[str(abs(int(tick) - 90)) for tick in np.arange(10, 91, 10)],
                showticklabels=False,
                gridcolor='#2f2f2f',
                gridwidth=0.5
            ),
        ),
        polar2=dict(
            domain=dict(x=[0.5, 1]),  # Right half
            bgcolor='black',
            angularaxis=dict(
                tickmode='array',
                tickvals=np.arange(0, 360, 45),
                ticktext=[f'{tick} h' for tick in np.arange(0, 24, 3)],
                direction="counterclockwise",
                rotation=180,
                gridcolor='#2f2f2f',
                gridwidth=0.5
            ),
            radialaxis=dict(
                range=[0, 90],
                showline=False,
                ticks='',
                tickvals=np.arange(10, 91, 10),
                ticktext=[str(abs(int(tick) - 90)) for tick in np.arange(10, 91, 10)],
                showticklabels=False,
                gridcolor='#2f2f2f',
                gridwidth=0.5,
            )
        ),showlegend=False, width=1920, height=1100,
    )
    
    return fig


def celestialSphere(df, mag_lim=6):
    cond_mag = df.Vmag < mag_lim

    hover_text = pd.Series([f'RA: {haminsec(ra)}<br>DEC: {gaminsec(dec)}<br>mag: {mag:.2f}<extra></extra>'
                            for ra, dec, mag in zip(df.RA, df.DEC, df.Vmag)])

    min_mag = np.min(df.Vmag[cond_mag])
    max_mag = np.max(df.Vmag[cond_mag])

    sizes = (max_mag-df.Vmag[cond_mag])/(max_mag-min_mag)*10
    
    # RA-Dec to Cartesian 
    xs = np.cos(np.radians(df.DEC[cond_mag])) * np.cos(np.radians(df.RA[cond_mag]))
    ys = np.cos(np.radians(df.DEC[cond_mag])) * np.sin(np.radians(df.RA[cond_mag]))
    zs = np.sin(np.radians(df.DEC[cond_mag]))
    
    
    # Create circular surface (disk)
    theta = np.linspace(0, 2 * np.pi, 100)
    r = np.linspace(0, 1, 50)
    r, theta = np.meshgrid(r, theta)
    
    x_surf = r * np.cos(theta)
    y_surf = r * np.sin(theta)
    z_surf = np.zeros_like(x_surf)
    
    fig = go.Figure(data=[
        go.Scatter3d(x=xs, y=ys, z=zs, mode='markers',
            marker=dict(size=sizes, color='blue'),
            hovertemplate=hover_text[cond_mag]),
        
        go.Surface(x=x_surf, y=y_surf, z=z_surf,
                   colorscale=[[0, 'white'], [1, 'white']],
                   showscale=False, hoverinfo='skip')
    ])
        
                                      
    fig.update_layout(scene=dict(
        xaxis_title='',
        yaxis_title='',
        zaxis_title='',
        xaxis = dict(showbackground=False,
                    showticklabels=False),
        yaxis = dict(showbackground=False,
                    showticklabels=False),
        zaxis = dict(showbackground=False,
                    showticklabels=False),
        aspectmode='data'
        ), height=800, width=800,
        title='Celestial sphere'
    )
        
    return fig
