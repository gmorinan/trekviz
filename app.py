# main app
# >>> streamlit run app.py

import pandas as pd #
import numpy as np 
import streamlit as st 
import streamlit.components.v1 as components
import altair as alt
import networkx as nx
from pyvis.network import Network

from param import col_dict, snames
from util import  parse_data, parse_ts, clock12, clock8, rc


#####################
### INITIAL SETUP ###
#####################

# styling 
st.set_page_config(page_title='TrekViz', page_icon="🖖")

st.markdown(""" <style> 
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;} 
        </style> """, unsafe_allow_html=True) 

padding = 0
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding}rem;
        padding-right: {padding}rem;
        padding-left: {padding}rem;
        padding-bottom: {padding}rem;
    }} </style> """, unsafe_allow_html=True)


st.sidebar.markdown('# STAR TREK VIZUALISER')

# for selecting series
series_pick = st.sidebar.selectbox('Select series:', 
                    list(snames.values()),
                    key='series', index=1)
snames_r = {v:k for k,v in snames.items()}
series_code = snames_r[series_pick] # for later use

# initial parse data
df, chars, relationships = parse_data(series_code)
chars_sorted = np.sort(chars) # for ordered dropbox



###########################
#### INTERACTIONS CHART ###
###########################

# define options in sidebar
st.sidebar.markdown('## NETWORK OPTIONS')
physics_bool = st.sidebar.checkbox('Add physics engine', key='phys', value=False)
box_bool = st.sidebar.checkbox('Make nodes boxes', key='boxb', value=True)
col_bool = st.sidebar.checkbox('Random colors', key='colb', value=False)
interactions = st.sidebar.slider("Number of Nodes", 4, 8, 12, 4)

st.markdown(
'''#### INTERACTION NETWORK
Wider lines = more interactions. 
Click and drag nodes to rearrange the network.
''')

nx_graph = nx.cycle_graph(interactions) # create initial dummy graph
chars_subset = chars[:interactions] # select characer subset

clockface = clock8 if interactions==8 else clock12 # positions depend on number of interactions
pos_dict = {chars[i]:clockface[i] for i in range(interactions)} # positions for character
name2node = {} # for mapping from node idx to character name


# add each character node
for idx, c in enumerate(chars_subset):
    name2node[c] = idx
    for k,v in {'label':c,
                'mass':10,
                'physics':physics_bool,
                'x':(pos_dict[c][0])*1.6*500,
                'y':(pos_dict[c][1])*1.1*500,
                'size':20,
                'shape': 'box' if box_bool else 'dot',
                'color': f'rgb({rc()},{rc()},{rc()})' if col_bool 
                            else col_dict[series_code][c]
                }.items():
        nx_graph.nodes[idx][k] = v

# add each interaction edge 
for wt, fr, to in relationships.values:
    if (to in chars_subset) & (fr in chars_subset) & (fr!=to):
        nx_graph.add_edge(name2node[fr], name2node[to], 
                        width=wt/300,
                        color='rgb(100,100,100)')
            
# translate to pyvis network
h, w  =  500, 750
nt = Network(f'{h}px', f'{w}px', 
            font_color='white' if box_bool else 'black')
nt.from_nx(nx_graph)
path = f'network.html'
nt.show(path)
HtmlFile = open(path, 'r', encoding='utf-8')
source_code = HtmlFile.read() 
components.html(source_code, height=h*1.1, width=w*1.1)



##########################
#### TIME SERIES CHART ###
##########################
st.sidebar.markdown('### TIME-SERIES OPTIONS')

st.markdown(
'''#### TIME-SERIES
Click on the legend to view one time-series only. 
Double click on the graph to reset the view.
''')

# for switching to season averages
season_bool = st.sidebar.checkbox('Season average', key='check', value=False)
xlab = 'Season' if season_bool else 'Episode'
ylab = 'Lines per Episode' if season_bool else 'Lines'

# for selecting characters
char_pick1 = st.sidebar.selectbox(label='Select first character:',
                            options=chars_sorted, key='char1', 
                            index=int(np.argmax(chars_sorted==chars[0])))
char_pick2 = st.sidebar.selectbox(label = 'Select second character:', 
                            options = chars_sorted, key='char2', 
                            index=int(np.argmax(chars_sorted==chars[1])))

# parse data for ts
line_count, ilabel = parse_ts(df, season_bool, xlab, ylab, char_pick1, char_pick2)

# for updating graph based on legend selection
selection = alt.selection_single(encodings=['color'], bind='legend')
color = alt.condition(selection,
                      alt.Color('Character:N', legend=None),
                      alt.value('lightgray')
                      )

# main chart code
ts_chart = alt.Chart(line_count, width=750, height=500).encode(
    alt.Y(ylab,
            scale=alt.Scale(paddingOuter=0.1)
            ),
    alt.X(xlab + ' Number', 
            axis=alt.Axis(tickMinStep=1),
            scale=alt.Scale(paddingInner=1)
            ),
    color=alt.Color('Character', 
        legend=alt.Legend(orient="top",title=None, labelLimit=300), 
        sort=[char_pick1, char_pick2],
        scale=alt.Scale(
            domain=[char_pick1, char_pick2, ilabel],
            range=['rgb(150,20,150)','rgb(150,100,0)','rgb(70,70,100)'])
            ),
    tooltip=[xlab,"Season","Character",ylab]
).add_selection(selection).transform_filter(selection).interactive()

# add to app
st.altair_chart(ts_chart.mark_line(color='firebrick', point=True))

st.markdown(
'''
#### NOTES 
* Interactions = the number of consecutive lines the two characters shared.
* Transcripts of episodes were used, hence "Episode Number" is actually transcript number.
* Some transcripts covered 2-parters, hence why there are less transcripts that aired episodes.
* Recent series (Discovery, Picard, Lower Decks) are not included due to lack of online transcripts. 
''')



###############
#### ABOUT ####
###############

st.sidebar.markdown('''
## ABOUT
Author: [@gmorinan](https://www.linkedin.com/in/gmorinan/) ([source code](https://github.com/gmorinan/trekviz))\n
Data source: [chakoteya.net](http://www.chakoteya.net/)\n
StarTrek rights owner: [ViacomCBS](https://www.viacomcbs.com/)\n
Tools: [Streamlit](https://streamlit.io/), [Altair](https://altair-viz.github.io/), [Networkx](https://networkx.org/) & [Pyvis](https://pyvis.readthedocs.io/en/latest/)
''')