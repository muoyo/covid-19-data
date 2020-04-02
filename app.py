import streamlit as st

# Import necessary libraries
import pickle
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Import python files we've created to help

# Controls appearance of seaborn plots. Options: paper, notebook, talk, or poster
SEABORN_CONTEXT = 'poster' 
SEABORN_PALETTE = sns.color_palette("bright")
sns.set_context(SEABORN_CONTEXT)



# Load the small English model
# nlp = en_core_web_sm.load()

st.subheader('COVID-19 Cases in the United States')

df_states = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
df_states['date'] = pd.to_datetime(df_states['date'])
df_states = df_states.loc[df_states['date'] > '2020-03-04']
# df_states = df_states.merge(df_population, how='left', on='state')
# df_states = df_states.merge(beds_per_state, how='left', on='state')
# df_states['cases_per_100k_people'] = df_states['cases'] / (df_states['population']/100_000)
# df_states['beds_per_100k_people'] = df_states['beds'] / (df_states['population']/100_000)

# most_recent_date = df_states['date'].sort_values().unique()[-1]

# df_states_latest = df_states.loc[df_states['date'] == most_recent_date].sort_values(by='cases', ascending=False)

plt.figure(figsize=(30,25))
sns.lineplot(x=df_states['date'], y=df_states['cases'], hue=df_states['state'], linewidth=6, markersize=14, marker='o', ci=False)
plt.title(f'Confirmed COVID-19 Cases per US State')
plt.xticks(rotation=90);
sns.despine()

st.pyplot()
