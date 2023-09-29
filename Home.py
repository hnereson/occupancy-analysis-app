import pandas as pd
import numpy as np
from plots import Plots
import streamlit as st
from sql_queries import run_sql_query, facilities_sql, all_tenants
from utils import grab_s3_file, password_authenticate

#---------------SETTINGS--------------------
page_title = "Occupancy Analysis Tool"
page_icon = ":red-circle:"  #https://www.webfx.com/tools/emoji-cheat-sheet/
layout= "wide"
initial_sidebar_state="auto"
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
plots = Plots()

# tenants = run_sql_query(all_tenants)
# facilities = run_sql_query(facilities_sql)

# list_rds = facilities['rd'].tolist()

#------SIDEBAR-------
with st.sidebar:
    # Display the image and title always
    st.image('red_dot.png', width=200)
    st.title(page_title)

    # Handle password input and validation
    enter_password = st.text_input("Password", type='password')

    if password_authenticate(enter_password):
        st.session_state['valid_password'] = True
    else: 
        st.warning("Please Enter Valid Password in the Sidebar")
        st.session_state['valid_password'] = False

# if password_authenticate(enter_password) == "Admin":

    # if password == "Admin":
    # # if 'valid_password' in st.session_state and st.session_state['valid_password']:
    #     page_names_to_funcs = {
    #         "Home": 'intro',
    #         "Move Ins": 'Move Ins',
    #         "ECRIs": 'ECRIs'
    #     }

    #     demo_name = st.sidebar.selectbox("Choose a page", page_names_to_funcs.keys())
    #     page_names_to_funcs[demo_name]()


    # tabs = ['Move Ins', 'Move Outs', 'ECRIs']
    # for i in tabs:
    #     selected_tab = st.sidebar.button(i)
    # # selected_tab = st.sidebar.selectbox('Select a page', tabs)

    # selected_region = st.sidebar.selectbox("Select region", ['All', 'North', 'Central', 'South'])
    
    # if selected_tab == 'Move Ins':
    #     st.subheader("Move Ins")

    


    # if selected_tab == 'Move Outs':
    #     st.subheader("Move Outs")




    
    # if selected_tab == 'ECRIs':
    #     st.subheader("ECRI Analysis")
    #     # ----- Data grab and prep -----
    #     # prep to be moved to another file eventually
    #     # st.cache()
    #     try:
    #         ecris = grab_s3_file('ecri/master_ecris.csv', 'rev-mgt')
    #         ecri_occs = grab_s3_file('ecri/occupancies.csv', 'rev-mgt')
    #     except Exception as e:
    #         st.error('Error retrieving ECRI data.')

    #     ecris['notification_date'] = pd.to_datetime(ecris['notification_date'])
    #     ecris['increase_date'] = pd.to_datetime(ecris['increase_date'])
    #     ecris['moved_out_date'] = pd.to_datetime(ecris['moved_out_date'])
    #     ecris['event_occurred'] = (~ecris['moved_out_date'].isnull()).astype(int)

    #     # Explicit datetime conversion
    #     min_date = ecris['notification_date'].min().to_pydatetime()
    #     max_date = ecris['notification_date'].max().to_pydatetime()

    #     all_possible_dates = pd.date_range(start=min_date, end=max_date).date.tolist()
    #     six_months_ago = (pd.Timestamp.now() - pd.DateOffset(months=6)).date()
    #     default_range = (six_months_ago, max_date.date())
        
    #     ecris_pending = ecris[ecris['ecri_pending']==True].shape[0]
    #     increase_amount_pending = ecris['pending_increase_amount'].sum()
    #     increase_amount_pending = "${:,.0f}".format(increase_amount_pending)
        
    #     # ----- UI -----
    #     with st.form("Filters"):
    #         form1= st.columns([2,1,1,4])
    #         range = form1[0].select_slider(
    #             "Choose Notification Dates", 
    #             options=all_possible_dates, 
    #             value=default_range
    #         )
    #         start_date, end_date = range
    #         formatted_start_date = start_date.strftime('%Y-%m-%d')
    #         formatted_end_date = end_date.strftime('%Y-%m-%d')

    #         # option = form1[1].selectbox(
    #         #     'Choose Start Time Column',
    #         #     ['notification_date', 'increase_date'])
    #         submitted = form1[2].form_submit_button("Confirm Selection")
    #         if submitted:
    #             st.write('Date Range selected:', f'{formatted_start_date} to {formatted_end_date}')
            

    #     # Filter based on the selected range
    #     start_date, end_date = range
    #     filtered_ecris = ecris[(ecris['notification_date'].dt.date >= start_date) & 
    #                    (ecris['notification_date'].dt.date <= end_date)]

    #     # option = form1[1].selectbox(
    #     #     'Choose Start Time Column',
    #     #     ['notification_date', 'increase_date'])
        
    #     blank()
    #     row1=st.columns([2,1,2,1,2])
    #     with row1[1]:
    #         st.metric("ECRIs Pending", ecris_pending)
    #     with row1[2]:
    #         st.metric("Increase $ Pending", increase_amount_pending)

    #     blank()

    #     row2=st.columns([3,2,2])
    #     with row2[0]:
    #         # plot_survival_curve_altair(filtered_ecris, 'notification_date')
    #         plots.plot_altair_chart(filtered_ecris, 'notification_date', 'Survival by Model')

    #     end_row = st.columns([1,5,5])
    #     with end_row[0]:
    #         csv_data = filtered_ecris.to_csv(index=False)
    #         st.download_button("Download Data", data=csv_data, file_name=f'ecris_{min_date.date()} to {max_date.date()}.csv', mime="text/csv")



