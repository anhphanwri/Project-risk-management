import pandas as pd
import streamlit as st
import plotly.express as px
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import os

# get the absolute path to the directory contain the .csv file
dir_name = os.path.abspath(os.path.dirname(__file__))

# join the project_risk_management_dashboard_data.csv to directory to get file path
location = os.path.join(dir_name, 'project_risk_management_dashboard_data.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(location)

# Set pandas display options to show all columns and rows
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_colwidth', None)

# Set page configuration
st.set_page_config(
    page_title="Project Risk Management Tool",
    layout="wide"
)

# Drop unwanted columns
columns_to_drop = ['Portfolio Name', 'Portfolio ID', 'Project ID', 'Risk ID', 'Link to the risk']
df = df.drop(columns_to_drop, axis=1)


# Define custom CSS styles
def local_css(file_name, **kwargs):
    with open(file_name) as f:
        css_content = f.read()
        for key, value in kwargs.items():
            css_content = css_content.replace('{{' + key + '}}', value)
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)

# Apply custom CSS with provided options
local_css("style.css",
          primaryColor="#F63366",
          backgroundColor="#FFFFFF",
          secondaryBackgroundColor="#F0F2F6",
          textColor="#262730",
          font="sans-serif")

# Sidebar filters
st.sidebar.title("Data Filters")


wri_program = list(df['WRI Program'].drop_duplicates())
office = list(df['Office'].drop_duplicates())
project_life_cycle_phase = list(df['Project Life Cycle Phase'].drop_duplicates())
risk_likelihood =  list(df['Risk Likelihood'].drop_duplicates())
risk_impact_level = list(df['Risk Impact Level'].drop_duplicates())
risk_assessment = list(df['Risk Assessment'].drop_duplicates())
risk_budget = list(df['Risk Budget'].drop_duplicates())
risk_status = list(df['Risk Status'].drop_duplicates())

wri_program_choice = st.sidebar.multiselect(
    'Choose WRI Program:', wri_program, default=[])
office_choice = st.sidebar.multiselect(
    'Choose Office:', office, default=[])
project_life_cycle_phase_choice = st.sidebar.multiselect(
    'Choose project life cycle phase:', project_life_cycle_phase, default=[])
risk_likelihood_choice = st.sidebar.multiselect(
    'Choose risk_likelihood:', risk_likelihood, default=[])
risk_impact_level_choice = st.sidebar.multiselect(
    'Choose risk_impact_level:', risk_impact_level, default=[])
risk_assessment_choice = st.sidebar.multiselect(
    'Choose risk_assessment:', risk_assessment, default=[])
risk_status_choice = st.sidebar.multiselect(
    'Choose risk_status:', risk_status, default=[])

budget_choice = st.sidebar.slider(
    'Budget:', min_value=int(min(risk_budget)), max_value=int(max(risk_budget)), step=100, value=int(max(risk_budget)))

# Filter data
# Create a list of tuples containing the filter options and their corresponding DataFrame columns
filter_options = [
    (wri_program_choice, 'WRI Program'),
    (office_choice, 'Office'),
    (project_life_cycle_phase_choice, 'Project Life Cycle Phase'),
    (risk_likelihood_choice, 'Risk Likelihood'),
    (risk_impact_level_choice, 'Risk Impact Level'),
    (risk_assessment_choice, 'Risk Assessment'),
    (risk_status_choice, 'Risk Status')
]

# Filter DataFrame based on selected options
#filtered_conditions = [df[col].isin(choices) for choices, col in filter_options if choices]

# Iterate through each filter option and its corresponding column
filtered_conditions = []
for choices, col in filter_options:
    # Check if there are any choices selected
    if choices:
        # Create a filtering condition based on the selected choices and corresponding column
        condition = df[col].isin(choices)
        # Add this condition to the list of filtering conditions
        filtered_conditions.append(condition)

# Filter by budget if selected
if budget_choice:
    filtered_conditions.append(df['Risk Budget'] <= budget_choice)

# Combine filtering conditions using logical AND
if filtered_conditions:
    combined_condition = pd.DataFrame(filtered_conditions).all()
    filtered_df = df[combined_condition]
else:
    filtered_df = df


# Search functionality
search_term = st.sidebar.text_input("Search by Risk Name")

if search_term:
    filtered_df = filtered_df[filtered_df['Risk Name'].str.contains(search_term, case=False)]

# Display filtered data
st.title("Project Risk Management Knowledge")

# Search functionality
search_term = st.sidebar.text_input("Search by Keyword")

if search_term:
    # Create a mask that checks if any column contains the search term
    mask = filtered_df.apply(lambda row: any(row.astype(str).str.contains(search_term, case=False)), axis=1)
    # Filter the DataFrame using the mask
    filtered_df = filtered_df[mask]

#Tabs
tab1, tab2, tab3 = st.tabs(["Data by offices and divisions", "Budget related content", "Combined content"])

#Tab1
office_distribution_chart = go.Figure()
office_distribution_chart.add_trace(go.Pie(labels=filtered_df['Office'].value_counts().index, values=filtered_df['Office'].value_counts().values))
office_distribution_chart.update_layout(title="Office Distribution")

program_distribution_chart = go.Figure()
program_distribution_chart.add_trace(go.Pie(labels=filtered_df['WRI Program'].value_counts().index, values=filtered_df['WRI Program'].value_counts().values))
program_distribution_chart.update_layout(title="WRI Program Distribution")

with tab1:
    col1, col2 = st.columns(2)
    # Office Distribution chart
    with col1:
        st.subheader("Office Distribution")
        st.plotly_chart(office_distribution_chart, use_container_width=True)
        
    # Program Distribution chart
    with col2:
        st.subheader("WRI Program Distribution")
        st.plotly_chart(program_distribution_chart, use_container_width=True)

    # Accompanied table showing the data
    st.subheader("Data Table")
    st.write(filtered_df)

#Tab2
fig_budget_distribution = px.histogram(filtered_df, x='Risk Budget', nbins=20, title='Budget Distribution', labels={'Risk Budget': 'Risk Budget', 'count': 'Frequency'})
fig_budget_distribution.update_layout(xaxis_title='Risk Budget', yaxis_title='Frequency')

fig_budget_impact = px.box(filtered_df, x='Risk Impact Level', y='Risk Budget', title='Budget by Impact Level', labels={'Risk Impact Level': 'Risk Impact Level', 'Risk Budget': 'Budget'})
fig_budget_impact.update_layout(xaxis_title='Risk Impact Level', yaxis_title='Risk Budget')

fig_budget = px.bar(filtered_df, x='Risk Impact Level', y='Risk Budget', labels={'Risk Impact Level': 'Impact Level', 'Risk Budget': 'Budget Amount'})
fig_budget.update_layout(xaxis_title='Risk Impact Level', yaxis_title='Risk Budget')

fig_budget_by_office = px.bar(filtered_df, x='Office', y='Risk Budget', title='Budget by Office', labels={'Office': 'Office', 'Risk Budget': 'Budget'})
fig_budget_by_office.update_layout(xaxis_title='Office', yaxis_title='Budget')

fig_budget_by_program = px.bar(filtered_df, x='WRI Program', y='Risk Budget', title='Budget by WRI Program', labels={'WRI Program': 'WRI Program', 'Risk Budget': 'Budget'})
fig_budget_by_program.update_layout(xaxis_title='WRI Program', yaxis_title='Budget')

with tab2:
    st.subheader("Budget related content")
    st.plotly_chart(fig_budget_distribution)
    st.plotly_chart(fig_budget_impact)
    st.plotly_chart(fig_budget)
    st.plotly_chart(fig_budget_by_office)
    st.plotly_chart(fig_budget_by_program)

    st.subheader("Data Table")
    st.write(filtered_df)

with tab3:
    # Column chart
    if st.checkbox("Column Chart: Risk by Phase", value=True):
        st.subheader("Risk Count by Project Life Cycle Phase")
        fig = px.bar(filtered_df['Project Life Cycle Phase'].value_counts().reset_index(), x='Project Life Cycle Phase', y='count', 
                    labels={'index': 'Project Life Cycle Phase', 'count': 'Count'})
        st.plotly_chart(fig)

    # Create columns for layout
    col1, col2 = st.columns(2)

    # Pie chart - Risk Distribution by Likelihood
    if st.checkbox("Pie Chart: Risk Distribution by Likelihood", value=True):
        with col1:
            st.subheader("Risk Distribution by Likelihood")
            fig_likelihood, ax_likelihood = plt.subplots()
            filtered_df['Risk Likelihood'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax_likelihood)
            st.pyplot(fig_likelihood)

    # Pie chart - Risk Distribution by Impact Level
    if st.checkbox("Pie Chart: Risk Distribution by Impact Level", value=True):
        with col2:
            st.subheader("Risk Distribution by Impact Level")
            fig_impact_level, ax_impact_level = plt.subplots()
            filtered_df['Risk Impact Level'].value_counts().plot.pie(autopct='%1.1f%%', ax=ax_impact_level)
            st.pyplot(fig_impact_level)

    st.subheader("Data Table")
    st.write(filtered_df)

# Use a text_input to get the keywords to filter the dataframe
text_search = st.text_input("Search by risk, project, WRI program, or office", value="")
# Filter the dataframe
if text_search:
    # Create a mask that checks if any of the specified columns contain the search term
    options = (df['Risk Name'].str.contains(text_search, case=False) |
            df['Project Name'].str.contains(text_search, case=False) |
            df['WRI Program'].str.contains(text_search, case=False) |
            df['Office'].str.contains(text_search, case=False))
    filtered_df = df[options]

# Check if any choice option is not selected
if text_search:
        st.write(filtered_df)
else:
    if (len(wri_program_choice) == 0 and
        len(office_choice) == 0 and
        len(project_life_cycle_phase_choice) == 0 and
        len(risk_likelihood_choice) == 0 and
        len(risk_impact_level_choice) == 0 and
        len(risk_assessment_choice) == 0 and
        len(risk_status_choice) == 0):
        pass
       #st.write(filtered_df.reset_index(drop=True))


# Drill-down table
#if st.checkbox("Show Pivot Table", value=True):
#    st.subheader("Filtering data by your preferences")
#    drill_down_cols = st.multiselect("Choose one or many columns to view:", filtered_df.columns)
#    if drill_down_cols:
#        # Filter the DataFrame to include only the selected columns
#        drill_down_df = filtered_df[drill_down_cols]
#        # Perform the aggregation
#        drill_down_df = drill_down_df.groupby(drill_down_cols).agg(lambda x: list(x)).reset_index()
#        st.write(drill_down_df)


