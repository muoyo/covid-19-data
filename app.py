import streamlit as st

# Import necessary libraries
import pickle
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Import python files we've created to help

# Controls appearance of seaborn plots. Options: paper, notebook, talk, or poster
SEABORN_CONTEXT = 'paper' 
SEABORN_PALETTE = sns.color_palette("bright")
sns.set_palette(SEABORN_PALETTE)
sns.set_style('white')
sns.set_context(SEABORN_CONTEXT)


# st.title('How is your state doing against the curve?')


# POPULATION
df_population = pd.read_csv('PEP_2018_PEPANNRES_with_ann.csv', encoding='latin1')
df_population = df_population.groupby('State', as_index=False)['Population'].sum()
df_population = df_population.rename(columns={"State": "state", "Population": "population"})
df_population['state'] = df_population['state'].apply(lambda state: state.strip())


# HOSPITALS
df_hospitals = pd.read_csv('us-hospitals.csv')
df_hospitals = df_hospitals.rename(columns={"COUNTYFIPS": "fips", "STATE": "state", "BEDS": "beds"})
df_hospitals = df_hospitals.loc[(df_hospitals.beds != -999) & (df_hospitals['fips'] != 'NOT AVAILABLE')]
df_hospitals['fips'] = df_hospitals['fips'].astype(int)


# STATE LOOKUP
state_dict = {
    'CA' : 'California',
    'TX' : 'Texas',
    'FL' : 'Florida',
    'NY' : 'New York',
    'OH' : 'Ohio',
    'PA' : 'Pennsylvania',
    'IL' : 'Illinois',
    'NJ' : 'New Jersey',
    'GA' : 'Georgia',
    'NC' : 'North Carolina',
    'MI' : 'Michigan',
    'TN' : 'Tennessee',
    'MO' : 'Missouri',
    'VA' : 'Virginia',
    'MA' : 'Massachusetts',
    'IN' : 'Indiana',
    'WI' : 'Wisconsin',
    'AL' : 'Alabama',
    'KY' : 'Kentucky',
    'LA' : 'Louisiana',
    'WA' : 'Washington',
    'MN' : 'Minnesota',
    'AZ' : 'Arizona',
    'OK' : 'Oklahoma',
    'SC' : 'South Carolina',
    'MS' : 'Mississippi',
    'IA' : 'Iowa',
    'MD' : 'Maryland',
    'CO' : 'Colorado',
    'AR' : 'Arkansas',
    'KS' : 'Kansas',
    'CT' : 'Connecticut',
    'WV' : 'West Virginia',
    'NV' : 'Nevada',
    'OR' : 'Oregon',
    'NE' : 'Nebraska',
    'PR' : 'Puerto Rico',
    'UT' : 'Utah',
    'NM' : 'New Mexico',
    'ME' : 'Maine',
    'DC' : 'District of Columbia',
    'MT' : 'Montana',
    'RI' : 'Rhode Island',
    'ND' : 'North Dakota',
    'ID' : 'Idaho',
    'SD' : 'South Dakota',
    'NH' : 'New Hampshire',
    'HI' : 'Hawaii',
    'DE' : 'Delaware',
    'WY' : 'Wyoming',
    'AK' : 'Alaska',
    'VT' : 'Vermont'
}


# BEDS PER STATE
beds_per_state = df_hospitals.groupby('state', as_index=False)['beds'].sum().sort_values(by='beds', ascending=False)
beds_per_state['state'] = beds_per_state['state'].apply(lambda abbrev: state_dict.get(abbrev))


# STATES
df_states = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv')
df_states['date'] = pd.to_datetime(df_states['date'])
df_states = df_states.rename(columns={'cases': 'positive_tests'})
df_states = df_states.loc[df_states['date'] > '2020-03-04']
df_states = df_states.merge(df_population, how='left', on='state')
df_states = df_states.merge(beds_per_state, how='left', on='state')
df_states['positive_tests_per_100k_people'] = df_states['positive_tests'] / (df_states['population']/100_000)
df_states['beds_per_100k_people'] = df_states['beds'] / (df_states['population']/100_000)



most_recent_date = df_states['date'].sort_values().unique()[-1]

df_states_latest = df_states.loc[df_states['date'] == most_recent_date].sort_values(by='positive_tests', ascending=False)

group_size = st.sidebar.slider("States per chart", 1, len(df_states_latest), 10)
state_groups = []

# Initialize empty arrays for groups of states
for i in np.arange(0, len(df_states_latest['state']), group_size): 
    state_groups.append([])
    
for i, state in enumerate(df_states_latest['state']):
    state_groups[i // group_size].append(state)


num_groups = len(state_groups)

i = 0 if num_groups < 2 else st.sidebar.slider("Page number", 1, num_groups) - 1
group = state_groups[i]
states_to_plot = df_states.loc[df_states['state'].isin(group)].sort_values(by='positive_tests', ascending=False)
states_to_plot_latest = states_to_plot.loc[states_to_plot['date'] == most_recent_date]
chart_title = f'States #{i*group_size+1}-{i*group_size+len(group)} by total number of positive test results'


if st.sidebar.checkbox("Positive tests per 100,000 people", False): 
    y_val = states_to_plot['positive_tests_per_100k_people']
    page_title = 'COVID-19 Positive Tests per 100,000'

else: 
    y_val = states_to_plot['positive_tests']
    page_title = 'COVID-19 Positive Tests per State'


st.sidebar.subheader(f'Positive tests per state, Page {i+1} of {num_groups}')
    
for j, state in enumerate(zip(states_to_plot_latest['state'], states_to_plot_latest['positive_tests'])):
    st.sidebar.text(f'{i*group_size + j + 1} - {state[0]} - {state[1]} positive_tests')

st.markdown(f'## **{page_title} as of {pd.to_datetime(most_recent_date).strftime("%b %-d, %Y")}**')


sns.lineplot(x=states_to_plot['date'], y=y_val, hue=states_to_plot['state'], linewidth=3, marker='o', ci=False)
plt.xticks(rotation=90);
plt.title(chart_title)
sns.despine()
plt.tight_layout()
st.pyplot()



st.markdown('### **Data source & methodology: [New York Times](https://www.nytimes.com/article/coronavirus-county-data-us.html)**')
st.dataframe(df_states_latest.drop(columns=['date', 'fips']))
