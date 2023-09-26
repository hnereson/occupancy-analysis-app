import streamlit as st
from sql_queries import run_sql_query, facilities_sql, all_tenants

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




    
    # if selected_tab == 'ECRIS':



