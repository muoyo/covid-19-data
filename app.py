import streamlit as st

# Import necessary libraries
import pickle
import datetime
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from pandas.tseries.offsets import DateOffset

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
df_population = df_population.append(pd.DataFrame([['Puerto Rico', 3_193_400],
                                                   ['Guam', 165_768],
                                                   ['Virgin Islands', 104_680],
                                                   ['Northern Mariana Islands', 56_882]], columns=['state', 'population']))


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


dates_sorted = df_states['date'].sort_values().unique()

earliest_date = dates_sorted[0]
most_recent_date = dates_sorted[-1]


# df_states['positive_tests_daily'] = 0
# df_states.loc[df_states['date'] < most_recent_date]


df_states_latest = df_states.loc[df_states['date'] == most_recent_date].sort_values(by='positive_tests', ascending=False)

group_size = st.sidebar.slider("States per chart", 1, len(df_states_latest), 10)
state_groups = []
state_names = df_states_latest['state']



# Initialize empty arrays for groups of states
for i in np.arange(0, len(state_names), group_size): 
    state_groups.append([])
    
for i, state in enumerate(state_names):
    state_groups[i // group_size].append(state)


num_groups = len(state_groups)

i = 0 if num_groups < 2 else st.sidebar.slider("Page number", 1, num_groups) - 1
group = state_groups[i]
states_to_plot = df_states.loc[df_states['state'].isin(group)].sort_values(by='positive_tests', ascending=False)
states_to_plot_latest = states_to_plot.loc[states_to_plot['date'] == most_recent_date]

state_string = f'State {i+1}' if group_size < 2 else f'States {i*group_size+1}-{i*group_size+len(group)}'
chart_title = f'{state_string} by total number of positive test results'

chart_type = st.radio('Choose your chart:', ['Cumulative', 'Per 100,000', 'Daily Increase'])

# if st.sidebar.checkbox("Positive tests per 100,000 people", False): 
if chart_type == 'Per 100,000':
    y_val = states_to_plot['positive_tests_per_100k_people']
    page_title = 'COVID-19 Positive Tests per 100,000'

elif chart_type == 'Cumulative': 
    y_val = states_to_plot['positive_tests']
    page_title = 'COVID-19 Positive Tests per State'

else:
    state_pivot = pd.pivot_table(df_states, values='positive_tests', index=['state'],
                    columns=['date'], aggfunc=np.sum, fill_value=0)

    for j in range(len(state_pivot.index)):
        for k in range(len(state_pivot.columns)-1, -0, -1):
            state_pivot.iat[j, k] = state_pivot.iat[j, k] - state_pivot.iat[j, k-1]
           
    page_title = 'Daily Increase in COVID-19 Positive Tests per State'



st.sidebar.subheader(f'Positive tests per state, Page {i+1} of {num_groups}')

state_is_hidden = []
    
for j, state in enumerate(zip(states_to_plot_latest['state'], states_to_plot_latest['positive_tests'])):
    if not st.sidebar.checkbox(f'{i*group_size + j + 1} - {state[0]} - {state[1]}', value=True):
        state_is_hidden.append(state[0])

st.markdown(f'## **{page_title} as of {pd.to_datetime(most_recent_date).strftime("%b %-d, %Y")}**')

if chart_type == 'Daily Increase':
    for s in group:
        states_to_plot = state_pivot.loc[s]

        if not s in state_is_hidden:
            if group_size - len(state_is_hidden) > 1:
                sns.lineplot(x=state_pivot.columns, y=states_to_plot, label=s, linewidth=3, marker='o', ci=False)
            
            else:
                sns.barplot(x=state_pivot.columns, y=states_to_plot, label=s, color=SEABORN_PALETTE[0], ci=False)
        
    plt.ylabel('Positive Tests per Day')

else:
    states_to_plot = states_to_plot.loc[states_to_plot['state'].isin(state_is_hidden) == False]
    
    if group_size - len(state_is_hidden) > 1:
        sns.lineplot(x=states_to_plot['date'], y=y_val, hue=states_to_plot['state'], linewidth=3, marker='o', ci=False)
    
    else:
        sns.barplot(x=states_to_plot['date'], y=y_val, hue=states_to_plot['state'], ci=False)

plt.xticks(rotation=90);
plt.title(chart_title)
plt.legend()
sns.despine()
plt.tight_layout()
st.pyplot()



st.markdown('### **Data source & methodology: [New York Times](https://www.nytimes.com/article/coronavirus-county-data-us.html)**')
st.dataframe(df_states_latest.drop(columns=['date', 'fips']))
