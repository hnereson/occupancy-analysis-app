import pandas as pd
import numpy as np
from plots import Plots
import streamlit as st
from sql_queries import run_sql_query, facilities_sql, all_tenants
from utils import grab_s3_file, password_authenticate, blank
from Home import enter_password 

plots = Plots()
page_title="Occupancy Tool - ECRIs"
st.set_page_config(page_title=page_title, page_icon="📈", layout= "wide")

st.subheader("ECRI Analysis")

with st.sidebar:
    # Display the image and title always
    st.image('red_dot.png', width=200)
    st.title(page_title)
# Need to come back to password authentication 
#     if not st.session_state.get('valid_password', False):
#         st.info("Please login from the Home page and try again.")

# if st.session_state['valid_password'] == True:

    # if selected_tab == 'ECRIs':

    # ----- Data grab and prep -----
    # prep to be moved to another file eventually
    # st.cache()
try:
    ecris = grab_s3_file('ecri/master_ecris.csv', 'rev-mgt')
    ecri_occs = grab_s3_file('ecri/occupancies.csv', 'rev-mgt')
except Exception as e:
    st.error('Error retrieving ECRI data.')

ecris['notification_date'] = pd.to_datetime(ecris['notification_date'])
ecris['increase_date'] = pd.to_datetime(ecris['increase_date'])
ecris['moved_out_date'] = pd.to_datetime(ecris['moved_out_date'])
ecris['event_occurred'] = (~ecris['moved_out_date'].isnull()).astype(int)

# Explicit datetime conversion
min_date = ecris['notification_date'].min().to_pydatetime()
max_date = ecris['notification_date'].max().to_pydatetime()

all_possible_dates = pd.date_range(start=min_date, end=max_date).date.tolist()
six_months_ago = (pd.Timestamp.now() - pd.DateOffset(months=6)).date()
default_range = (six_months_ago, max_date.date())

ecris_pending = ecris[ecris['ecri_pending']==True].shape[0]
increase_amount_pending = ecris['pending_increase_amount'].sum()
increase_amount_pending = "${:,.0f}".format(increase_amount_pending)

# ----- UI -----
with st.form("Filters"):
    form1= st.columns([2,1,1,4])
    range = form1[0].select_slider(
        "Choose Notification Dates", 
        options=all_possible_dates, 
        value=default_range
    )
    start_date, end_date = range
    formatted_start_date = start_date.strftime('%Y-%m-%d')
    formatted_end_date = end_date.strftime('%Y-%m-%d')

    # option = form1[1].selectbox(
    #     'Choose Start Time Column',
    #     ['notification_date', 'increase_date'])
    submitted = form1[2].form_submit_button("Confirm Selection")
    if submitted:
        st.write('Date Range selected:', f'{formatted_start_date} to {formatted_end_date}')
    

# Filter based on the selected range
start_date, end_date = range
filtered_ecris = ecris[(ecris['notification_date'].dt.date >= start_date) & 
                (ecris['notification_date'].dt.date <= end_date)]

# option = form1[1].selectbox(
#     'Choose Start Time Column',
#     ['notification_date', 'increase_date'])

blank()
row1=st.columns([2,1,2,1,2])
with row1[1]:
    st.metric("ECRIs Pending", ecris_pending)
with row1[2]:
    st.metric("Increase $ Pending", increase_amount_pending)

blank()

row2=st.columns([3,2,2])
with row2[0]:
    # plot_survival_curve_altair(filtered_ecris, 'notification_date')
    plots.plot_altair_chart(filtered_ecris, 'notification_date', 'Survival by Model')

end_row = st.columns([1,5,5])
with end_row[0]:
    csv_data = filtered_ecris.to_csv(index=False)
    st.download_button("Download Data", data=csv_data, file_name=f'ecris_{min_date.date()} to {max_date.date()}.csv', mime="text/csv")

