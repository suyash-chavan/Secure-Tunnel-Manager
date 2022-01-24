import streamlit as st
import requests
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, time
import os
import json
from dotenv import load_dotenv
import streamlit_authenticator as stauth
from PIL import Image
import math

load_dotenv()

SERVER_URI=os.getenv("SERVER_URI")

wceLogo = Image.open('wce.png')

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

def loggedIn():

    st.sidebar.markdown('Welcome **%s**, <hr />'% (name),unsafe_allow_html=True)

    
    appreq = requests.get(SERVER_URI+"/dashboard/applications")

    apps = {}
    appres = appreq.json()

    for app in appres["applications"]:
        apps[app["applicationName"]] = app["applicationId"]

    selectedApp = st.sidebar.selectbox(
    "Application",
    apps.keys())

    clientReq = requests.post(SERVER_URI+"/dashboard/clients",json = {
            "applicationId": apps[selectedApp]
    })

    clients = {}

    for client in clientReq.json()["clients"]:
        clients[client["clientName"]] = client["clientId"]

    aggr = st.sidebar.checkbox('Data Aggregation')

    if(not aggr):
        devices = st.sidebar.selectbox(
        "Device Name",
        clients.keys())

        devices = [devices]
    else:
        devices = st.sidebar.multiselect(
     'Device Name',
     clients.keys())

    reqClients = []

    for device in devices:
        reqClients.append(clients[device])

    dataReq = requests.post(SERVER_URI+"/dashboard/data",json = {
            "clientId": reqClients,
            "applicationId": apps[selectedApp]
    })

    dataJson = dataReq.json()["data"]

    data = []

    paraReq = requests.post(SERVER_URI+"/dashboard/headers",json = {
            "applicationId": apps[selectedApp]
    })

    appData = paraReq.json()["dataParameters"]

    headers = []
    parameters = []

    for header in appData:
        headers.append(header)
        parameters.append(appData[header])

    for dataPoint in dataJson:
        row = []

        for header in headers:
            if(header in dataPoint.keys()):
                row.append(dataPoint[header])

        data.append(row)

    df = pd.DataFrame(
    data, columns=parameters)

    if(not aggr):
        st.header("Metrics")

        metrics = requests.post(SERVER_URI+"/dashboard/metrics",json = {    
                "clientId": reqClients[0],
                "applicationId": apps[selectedApp]
        })

        metrics = metrics.json()["metrics"]

        metricRows = []

        for i in range(math.ceil(len(metrics)/3)):
            metricRows.append(st.columns(3))

        for i in range(len(metricRows)):
            for j in range(min(3,len(metrics)-(3*i))):
                metricRows[i][j].metric(metrics[i*3+j]["name"], metrics[i*3+j]["value"])

    st.header("Data")

    st.table(df)

    csv = convert_df(df)

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
        st.write("""from inspect import Parameter

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