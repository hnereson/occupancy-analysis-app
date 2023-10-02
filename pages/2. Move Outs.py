import pandas as pd
import numpy as np
from plots import HeatmapPlot, HistogramPlot, ScatterPlot
import streamlit as st
from sql_queries import run_sql_query, move_outs, occupants, facilities_sql
from utils import grab_s3_file, password_authenticate, blank

page_title="Occupancy Tool - Move Outs"
st.set_page_config(page_title=page_title, page_icon="📈", layout= "wide")

heatmap_plot = HeatmapPlot()
histogram = HistogramPlot()
scatter = ScatterPlot()

st.subheader("Move Out Analysis")


with st.sidebar:
    # Display the image and title always
    st.image('red_dot.png', width=200)
    st.title(page_title)

# Need to come back to password authentication 
#     if not st.session_state.get('valid_password', False):
#         # Display the password input field
#         enter_password = st.text_input("Password", type='password')
        
#         # Check for password authentication
#         if password_authenticate(enter_password) == "Admin":
#             st.session_state['valid_password'] = True
#         else:
#             st.warning("Please Enter Valid Password in the Sidebar")

# if st.session_state['valid_password'] == True:
#     st.write('Hello')

move_out_monthly = run_sql_query(move_outs)
occs = run_sql_query(occupants)

st.cache(ttl= 60*60*24)
def prep_data(move_out_monthly, occs):
    move_out_df = occs.merge(move_out_monthly, how="left", on=["date", "site_code"])
    move_out_df['% moved out'] = round(100 * move_out_df['move_outs'] / move_out_df['occupants'], 2)
    move_out_df['date'] = pd.to_datetime(move_out_df['date'])

    # Extract year and month from the date
    move_out_df['year'] = move_out_df['date'].dt.year
    move_out_df['month'] = move_out_df['date'].dt.month

    # Group by year and month, then sum 'occupants' and 'move_outs'
    monthly_summary = move_out_df.groupby(['year', 'month'])[['occupants', 'move_outs']].sum().reset_index()

    # Recalculate the '% moved out'
    monthly_summary['% moved out'] = round(100 * monthly_summary['move_outs'] / monthly_summary['occupants'], 2)
    heatmap_data = monthly_summary.pivot(index='year', columns='month', values='% moved out')
    return move_out_df, monthly_summary, heatmap_data

st.cache(ttl= 60*60*24)
def date_ranges(occs):
    min_date = occs['date'].min()
    max_date = occs['date'].max()
    one_month_ago = (pd.Timestamp.now() - pd.DateOffset(months=1)).date()
    default_range = (one_month_ago, max_date)
    return min_date, max_date, one_month_ago, default_range

min_date, max_date, one_month_ago, default_range = date_ranges(occs)
move_out_df, monthly_summary, heatmap_data = prep_data(move_out_monthly, occs)
# ----- UI -----
with st.form("Filters"):
    form1= st.columns([2,1,1,4]) 
    range = form1[0].slider("Select a Date Range", min_date, max_date, default_range)
    # range = form1[0].select_slider(
    #     "Choose Notification Dates", 
    #     options=all_possible_dates, 
    #     value=default_range
    # )
    start_date, end_date = range
    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')

    # option = form1[1].selectbox(
    #     'Choose Start Time Column',
    #     ['notification_date', 'increase_date'])
    submitted = form1[2].form_submit_button("Confirm Selection")
    if submitted:
        st.write('Date Range selected:', f'{formatted_start_date} to {formatted_end_date}')

blank()

row2=st.columns([2,2,2])
with row2[0]: # not working
    # display histogram of yoy move outs
    prepped_histo = histogram.prepare_histogram_data(move_out_df, start_date, end_date)
    histogram.plot_altair_histogram(prepped_histo, x_field="yoy_change", title_text="Distribution of Y/Y Changes in % Moved Out")

with row2[2]:
    # Use the display_heatmap method to display the heatmap in Streamlit
    heatmap_plot.display_heatmap(data=heatmap_data, x_field='month', y_field='year', color_field='% moved out', title_text='% Moved Out by Year and Month')

