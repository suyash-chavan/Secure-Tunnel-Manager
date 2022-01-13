import streamlit as st
import requests
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, time
import socket
import os
import json
from dotenv import load_dotenv
import streamlit_authenticator as stauth
from PIL import Image

load_dotenv()

wceLogo = Image.open('wce.png')

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

def loggedIn():

    st.sidebar.markdown('Welcome **%s** <hr />'% (name),unsafe_allow_html=True)

    

    application = st.sidebar.selectbox(
    "Application",
    ("Mask Detection", "Fall Detection"))

    aggr = st.sidebar.checkbox('Data Aggregation')

    if(not aggr):
        device = st.sidebar.selectbox(
        "Device Name",
        ("CSE Dept", "ELN Dept"))
    else:
        options = st.sidebar.multiselect(
     'Device Name',
     ["CSE Dept", "ELN Dept"])

    csv = convert_df(pd.DataFrame(list()))

    st.sidebar.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )

    st.sidebar.markdown("<hr />",unsafe_allow_html=True)

    with st.sidebar.expander("About"):
        st.write("""
         The chart above shows some numbers I picked for you.
         I rolled actual dice for these, so they're *guaranteed* to
         be random.
     """)
    with st.sidebar.expander("Report Bug"):
        st.write("""
         The chart above shows some numbers I picked for you.
         I rolled actual dice for these, so they're *guaranteed* to
         be random.
     """)

client = MongoClient(os.getenv('MONGO_URI'))


names = json.loads(os.getenv('NAMES'))
usernames = json.loads(os.getenv('USERNAMES'))
passwords = json.loads(os.getenv('PASSWORDS'))

hashed_passwords = stauth.hasher(passwords).generate()

authenticator = stauth.authenticate(names,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=30)

col1, col2,col3 = st.columns([2,1,2])


with col2:
    st.image(wceLogo)

st.markdown("<h2 style='text-align: center;'>IoT Dashboard & Management</h2>", unsafe_allow_html=True)
name, authentication_status = authenticator.login('Login','main')

if authentication_status:
    loggedIn()    
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')