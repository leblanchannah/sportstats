import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from src.race_data import SportStatsApi, convert_segment_time
import json

@st.cache_data
def load_data():
    api = SportStatsApi()
    event_id = api.search_event("ottawa", 2, 0).data[1]['eid'] # gives eid - event id, will need slug
    print(event_id)
    mid, ottawa_races = (api.get_races_at_event('ottawa-race-weekend'))

    json_string = [ob.__dict__ for ob in api.get_leaderboard_results('140564', event_id, '1370', page_size=100, max_amount=-1)]

    df = pd.DataFrame(pd.json_normalize(json_string))
    df['race_data.381034.rt'] = convert_segment_time(df['race_data.381034.rt'])
    return df


st.title('Ottawa Race Weekend Results')
data = load_data()

option = st.selectbox(
    "Bib lookup",
    (x for x in data['bib'].astype(str)))
st.write("You selected:", option)

fig = go.Figure()
fig.add_trace(
    go.Histogram(
        x=data[data['gender']=='f']['race_data.381034.rt'],
        name='F'
    )
)
fig.add_trace(
    go.Histogram(
        x=data[data['gender']=='m']['race_data.381034.rt'],
        name='M'
    )
)

# Reduce opacity to see both histograms
fig.update_traces(opacity=0.75)

fig.update_layout(
    barmode='overlay',
    title="10k Race Times",
    xaxis_title="Time (mins)",
    yaxis_title="Count",
    legend_title="Gender"
)
st.plotly_chart(fig)