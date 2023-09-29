import pandas as pd
import numpy as np
from plots import Plots
import streamlit as st
from sql_queries import run_sql_query, facilities_sql, all_tenants
from utils import grab_s3_file, password_authenticate, blank

plots = Plots()
page_title="Occupancy Tool - Move Ins"
st.set_page_config(page_title="Move Ins", page_icon="📈", layout= "wide")

st.subheader("Move Ins")

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