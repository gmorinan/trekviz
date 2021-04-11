# store for util functions used in app.py

import pandas as pd
import numpy as np
import math
import streamlit as st 


# FUNCTION TO PARSE RELATIONAL DATA
@st.cache
def parse_data(series_code):
    '''
    Parses raw data into a usable parts

    Parameters:
    ----------
    df: str, series_pick

    Returns:
    -------
    Dataframe containing columns needed for the altair chart
    '''

    df = pd.read_csv(f'data/{series_code}_interactions.csv',index_col=0)
    chars = list(df[df['ep']=='all']['lines'].sort_values(ascending=False).index)
    relationships = df[df['ep']=='all'].iloc[:,:12]
    relationships = relationships.stack().to_frame()
    relationships.columns = ['weight']
    relationships['from'] = [i[0] for i in relationships.index]
    relationships['to'] = [i[1] for i in relationships.index]

    return df, chars, relationships



# FUNCTION TO PARSE TIME SERIES DATA
@st.cache
def parse_ts(df, yvalue_bool, xlab, ylab, char_pick1, char_pick2):
    '''
    Parses raw data into a usable time series

    Parameters:
    ----------
    df: Dataframe, containing the raw data
    yvalue_bool: bool, whether to average across seasons or not
    xlab: str, label for x-axis
    ylab: str, label for y-axis
    char_pick1: str, first character to plot
    char_pick2: str, second character to plot

    Returns:
    -------
    Dataframe containing columns needed for the altair chart
    '''

    # remote the rows that correspond to totals
    df1 = df[df['ep']!='all']

    # create output dataframe
    line_count = pd.DataFrame(columns=['Character',ylab,xlab,'Name'])

    # label for interaction
    ilabel = f'Interactions({char_pick1},{char_pick2})'

    # calculations depend on whether we are averaging over seasons or not
    if yvalue_bool:
        y1 = df1.loc[char_pick1].groupby('season')['lines'].mean().round(1)
        y2 = df1.loc[char_pick2].groupby('season')['lines'].mean().round(1)
        y3 = df1.loc[char_pick1].groupby('season')[char_pick2].mean().round(1)
        x1a = y1.index
        x1b = [str(i) for i in x1a]
    else:
        y1 = df1.loc[char_pick1,'lines']
        y2 = df1.loc[char_pick2,'lines']
        y3 = df1.loc[char_pick1,char_pick2]
        x1a = df1.loc[char_pick1,'ep'].astype(int) + 1
        x1b = df1.loc[char_pick1,'title']
        line_count['Season'] = list(df1.loc[char_pick1,'season']) * 3
    
    n = len(y1)
    line_count[ylab] = list(y1)+list(y2)+list(y3)
    line_count['Character'] = ([char_pick1]*n) + ([char_pick2]*n) + ([ilabel]*n)
    line_count[xlab + ' Number'] = list(x1a) * 3
    line_count[xlab] = list(x1b) * 3

    return line_count, ilabel

# used to generate random colors
def rc():
    return np.random.randint(0, high=120)


## clockface co-ordinates 
def rect(r, theta):
    """theta in degrees

    returns tuple; (float, float); (x,y)
    """
    x = r * math.cos(math.radians(theta))
    y = r * math.sin(math.radians(theta))
    return np.array([x,y]).round(2)


clock12 = {i: rect(0.4, r) for i, r in enumerate([270, 90, 0, 180, 300, 210, 30, 120, 240, 330, 60, 150]) }
clock8 = {i: rect(0.4, r) for i, r in enumerate([270, 90, 0, 180, 315, 135, 45, 225]) }

