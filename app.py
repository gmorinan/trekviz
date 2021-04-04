# main app
# >>> streamlit run app.py

import pandas as pd
import numpy as np

import streamlit as st 
import streamlit.components.v1 as components

import altair as alt
import networkx as nx
from pyvis.network import Network

from config import col_dict, clock12, snames


# FUNCTION TO PARSE DATA
def parse_ts(df, yvalue_bool, xlab, ylab, desired_char1, desired_char2):

    if yvalue_bool == False:
        # last entry will always be all series
        nline1 = df.loc[desired_char1,'total_lines'].values[:-1]
        nline2 = df.loc[desired_char2,'total_lines'].values[:-1]
        nlinex = df.loc[desired_char1,desired_char2].values[:-1]
        nlines = df.loc[desired_char1,'title'].values[:-1]
        xlines = df.loc[desired_char1,'ep'].values[:-1].astype(int) + 1
    
    else:
        nline1 = df.loc[desired_char1].iloc[:-1].groupby('season')['total_lines'].mean().round(1)
        nline2 = df.loc[desired_char2].iloc[:-1].groupby('season')['total_lines'].mean().round(1)
        nlinex = df.loc[desired_char1].iloc[:-1].groupby('season')[desired_char2].mean().round(1)
        xlines = nline1.index
        nlines = ['Season ' + str(i) for i in xlines]


    n = len(nline1)
    nline = pd.DataFrame(columns=['Character',ylab,xlab,'Name'])

    cvec = ([desired_char1]*n) + ([desired_char2]*n) + (['interactions']*n)
    lvec = list(nline1) + list(nline2) + list(nlinex)
    ivec = list(range(1,n+1)) + list(range(1,n+1)) + list(range(1,n+1))
    svec = list(xlines) + list(xlines) + list(xlines)
    nvec = list(nlines) + list(nlines) + list(nlines)

    nline['Character'] = cvec
    nline[ylab] = lvec
    nline[xlab + ' Number'] = svec
    nline[xlab] = nvec
    nline['Rand'] = np.random.random(len(nline))

    return nline



# START SIDEBAR
st.sidebar.markdown('# TREK VIZUALISER')
desired_series = st.sidebar.selectbox('Select series:', 
                    list(snames.values()),
                    key='series', index=1)

st.sidebar.markdown('*****')
# st.sidebar.markdown('### TIME SERIES')

yvalue_bool = st.checkbox(
                'Season Average',
                key='check', value=False)
xlab = 'Season' if yvalue_bool else 'Episode'
ylab = 'Lines per Episode' if yvalue_bool else 'Lines'



# GET RELATIONSNIPS
snames_r = {v:k for k,v in snames.items()}
df = pd.read_csv(f'data/{snames_r[desired_series]}_interactions.csv',index_col=0)
chars = list(df[df['ep']=='all']['total_lines'].sort_values(ascending=False).index)
pos_dict = {chars[i]:clock12[i] for i in range(len(chars))}
relationships = df[df['ep']=='all'].iloc[:,:12]
rs = relationships.stack().to_frame()
rs.columns = ['weight']
rs['from'] = [i[0] for i in rs.index]
rs['to'] = [i[1] for i in rs.index]


# get ordered character list 
c1 = chars[0]
c2 = chars[1]
chars_sorted = np.sort(chars)
i1 = int(np.argmax(chars_sorted==c1))
i2 = int(np.argmax(chars_sorted==c2))

# CREATE SIDEBAR = part 2
desired_char1 = st.sidebar.selectbox( label='Select first character:',
                            options=chars_sorted,
                            key='char1', 
                            index=int(np.argmax(chars_sorted==c1))
                            )
chars_reduced = [c for c in chars_sorted if c !=desired_char1]
desired_char2 = st.sidebar.selectbox('Select second character:', 
                            chars_sorted,
                            key='char2', 
                            index=int(np.argmax(chars_sorted==c2))
                            )
st.sidebar.markdown('*****')
#st.sidebar.markdown('### INTERACTIONS')



#### TIME SERIES CHART 
nline = parse_ts(df, yvalue_bool, xlab, ylab, desired_char1, desired_char2)
xmax = int(nline.shape[0]/3)
ymax = 1.025*(nline[ylab].max())
selection = alt.selection_single(fields=['Character'], bind='legend')
color = alt.condition(selection,
                      alt.Color('Character:O', legend=None, 
                      scale=alt.Scale(scheme='category10')),
                      alt.value('lightgray'),
                      legend=alt.Legend(orient='top'))

A = alt.Chart(nline, width=750, height=500).encode(
    alt.Y(ylab,
            scale=alt.Scale(paddingOuter=0.1)
            ),
    alt.X(xlab + ' Number', 
            axis=alt.Axis(tickMinStep=1),
            scale=alt.Scale(paddingInner=1)
            ),
    color=alt.Color('Character', legend=alt.Legend(orient="top")),
    tooltip=[xlab,"Character",ylab]
).add_selection(selection).interactive()
st.altair_chart(A.mark_line(color='firebrick', point=True))



### INTERACTIONS PLOT
interactions = st.sidebar.slider("Number of interactions", 4, 8, 12, 4)
colorscheme = st.sidebar.radio('Interactions node colors:', 
                    ['Default','Random','None'],
                    key='colors', index=0)

name2node = {}
node2name = {}
nx_graph = nx.cycle_graph(interactions)
chars_subset = chars[:interactions]

for idx, c in enumerate(chars_subset):
    name2node[c] = idx
    node2name[idx] = [c]
    nx_graph.nodes[idx]['label'] = c
    nx_graph.nodes[idx]['mass'] = 10
    nx_graph.nodes[idx]['physics'] = False
    nx_graph.nodes[idx]['shape'] = 'box'
    nx_graph.nodes[idx]['borderWidth'] = 1
    nx_graph.nodes[idx]['borderWidthSelected'] = 10
    nx_graph.nodes[idx]['x'] = (pos_dict[c][0]-0.5)*1.5*500
    nx_graph.nodes[idx]['y'] = (0.5-pos_dict[c][1])*500

    if colorscheme == 'Default':
        nx_graph.nodes[idx]['color'] = col_dict[snames_r[desired_series]][c]
    elif colorscheme == 'Random':
        r,g,b = np.random.randint(0, high=360, size=3)
        nx_graph.nodes[idx]['color'] = f'rgb({r},{g},{b})'
    else:
        nx_graph.nodes[idx]['color'] = 'gray'
    

for wt, fr, to in rs.values:
    if (to in chars_subset) & (fr in chars_subset):
        if fr!=to:
            nx_graph.add_edge(
                name2node[fr], 
            name2node[to], 
            width=wt/300,
            color='rgb(50,50,50)')
            
labels = nx.draw_networkx_labels(nx_graph, pos=nx.spring_layout(nx_graph))
nt = Network('500px', '750px', font_color='white')
nt.from_nx(nx_graph)
nt.show('nx.html')
HtmlFile = open("nx.html", 'r', encoding='utf-8')
source_code = HtmlFile.read() 
components.html(source_code, height = 900,width=900)