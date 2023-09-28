import pandas as pd
import numpy as np
from plots import Plots
import streamlit as st
from sql_queries import run_sql_query, facilities_sql, all_tenants
from utils import grab_s3_file, style_plot

#---------------SETTINGS--------------------
page_title = "Occupancy Analysis Tool"
page_icon = ":red-circle:"  #https://www.webfx.com/tools/emoji-cheat-sheet/
layout= "wide"
initial_sidebar_state="collapsed"
#-------------------------------------------

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout, initial_sidebar_state=initial_sidebar_state)

# --- HIDE STREAMLIT STYLE ---
hide_st_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# ----- FUNCTIONS -----
def blank(): return st.write('') 

def password_authenticate(pwsd):

    if pwsd in st.secrets["ADMIN"]:
        return "Admin"

plots = Plots()

tenants = run_sql_query(all_tenants)
facilities = run_sql_query(facilities_sql)

list_rds = facilities['rd'].tolist()
geocoded_rds = facilities[['rd', 'latitude', 'longitude', 'acq_date']]

st.sidebar.image('red_dot.png', width=200)
enter_password = st.sidebar.text_input("Password", type = 'password')

if password_authenticate(enter_password):
    st.session_state['valid_password'] = True
else: 
    st.warning("Please Enter Valid Password in the Sidebar")
    st.session_state['valid_password'] = False

st.title(page_title)

password = password_authenticate(enter_password)

if password == "Admin":

    tabs = ['Move Ins', 'Move Outs', 'ECRIs']
    
    selected_tab = st.sidebar.selectbox('Select a page', tabs)

    selected_region = st.sidebar.selectbox("Select region", ['All', 'North', 'Central', 'South'])

    facility_options = facilities['rd'].unique()

    
    if selected_tab == 'Move Ins':
        print('Hello')

    


    # if selected_tab == 'Move Outs':




    
    if selected_tab == 'ECRIs':
        st.subheader("ECRI Analysis")

        # st.cache()
        try:
            ecris = grab_s3_file('ecri/master_ecris.csv', 'rev-mgt')
            ecri_occs = grab_s3_file('ecri/occupancies.csv', 'rev-mgt')
        except Exception as e:
            st.error('Error retrieving ECRI data.')

        ecris['notification_date'] = pd.to_datetime(ecris['notification_date'])
        ecris['increase_date'] = pd.to_datetime(ecris['increase_date'])
        ecris['moved_out_date'] = pd.to_datetime(ecris['moved_out_date'])

        # Explicit datetime conversion
        min_date = ecris['notification_date'].min().to_pydatetime()
        max_date = ecris['notification_date'].max().to_pydatetime()

        # with st.form("entry_form", clear_on_submit=False):
        #     row1= st.columns([1,2,2])
        #     # range = col1.select_slider("Choose Notification Dates", options = [ecris['notification_date']], value =(min_date, max_date))
        #     submitted = st.form_submit_button("Submit")

        # if submitted:

        ecris['event_occurred'] = (~ecris['moved_out_date'].isnull()).astype(int)

        # Use the above function in Streamlit
        all_possible_dates = pd.date_range(start=min_date, end=max_date).date.tolist()
        six_months_ago = (pd.Timestamp.now() - pd.DateOffset(months=6)).date()
        default_range = (six_months_ago, max_date.date())

        row1= st.columns([2,1,4])
        range = row1[0].select_slider(
            "Choose Notification Dates", 
            options=all_possible_dates, 
            value=default_range
        )

        # Filter based on the selected range
        start_date, end_date = range
        filtered_ecris = ecris[(ecris['notification_date'].dt.date >= start_date) & 
                       (ecris['notification_date'].dt.date <= end_date)]

        # option = row1[1].selectbox(
        #     'Choose Start Time Column',
        #     ['notification_date', 'increase_date'])
        blank()
        row2=st.columns([3,2,2])
        with row2[0]:
            # plot_survival_curve_altair(filtered_ecris, 'notification_date')
            plots.plot_altair_chart(filtered_ecris, 'notification_date', 'Survival by Model from 0 - 180 Days')

        end_row = st.columns([1,5,5])
        with end_row[0]:
            csv_data = filtered_ecris.to_csv(index=False)
            st.download_button("Download Data", data=csv_data, file_name=f'ecris_{min_date.date()} to {max_date.date()}.csv', mime="text/csv")



