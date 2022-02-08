import streamlit as st
import requests
import pandas as pd
from pymongo import MongoClient
from datetime import date, datetime, time
import os
import json
from dotenv import load_dotenv
import streamlit_authenticator as stauth
from PIL import Image
from streamlit_echarts import st_echarts
import math
import base64

load_dotenv()

SERVER_URI=os.getenv("SERVER_URI")
API_KEY = os.getenv("API_KEY")

wceLogo = Image.open('wce.png')
wce75 = Image.open('75_wce.png')

st.set_page_config(page_title="IoT Dashboard & Management", page_icon="WCE_PNG.png", layout="wide")

@st.cache
def convert_df(df):
    return df.to_csv().encode('utf-8')

def show_sidebar():

    cols = st.sidebar.columns([2,1])

    # with cols[0]:
    st.sidebar.markdown('''<h1>Welcome,</h1>
<h3>%s</h3>'''%(name),unsafe_allow_html=True)
        # st.sidebar.markdown('**%s** <hr />'% (name),unsafe_allow_html=True)

    # with cols[1]:
    #     st.image(wce75)

    st.sidebar.markdown('<hr />',unsafe_allow_html=True)

    page = st.sidebar.selectbox("Navigate", ("Dashboard", "Register Application"))

    st.sidebar.markdown("<hr />",unsafe_allow_html=True)

    appreq = requests.get(SERVER_URI+"/dashboard/applications",json = {
        "apiKey": API_KEY
    })

    apps = {}
    appres = appreq.json()

    for app in appres["applications"]:
        appsAvailable = True
        apps[app["applicationName"]] = app["applicationId"]

    appsShow = list(apps.keys())
    print(appsShow)

    if(page=="Register Application"):
        appsShow = ["New Application"] + appsShow

    selectedApp = st.sidebar.selectbox(
    "Application",
    appsShow)

    if(page=="Dashboard"):

        clientReq = requests.post(SERVER_URI+"/dashboard/clients",json = {
                "applicationId": apps[selectedApp],
                "apiKey": API_KEY
        })

        clients = {}

        for client in clientReq.json()["clients"]:
            clients[client["clientName"]] = client["clientId"]

        # aggr = st.sidebar.checkbox('Data Aggregation')
        aggr = False
        
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
            if(device!=None):
                reqClients.append(clients[device])

        st.sidebar.markdown("<hr />",unsafe_allow_html=True)

    with st.sidebar.expander("About"):
        st.write("""
         IoT Management System
     """)
    with st.sidebar.expander("Report Bug"):
        st.write("""
        Mailto: suyashc222@gmail.com
     """)

    if(page=="Dashboard"):
        return reqClients, devices[0], selectedApp, apps[selectedApp], aggr, page
    
    if(selectedApp=="New Application"):
        return None, None, None, None, None, page

    return None, devices[0], selectedApp, apps[selectedApp], None, page

def show_data(clients, deviceName, applicationName, applicationId, aggr):

    
    st.markdown("<h3 style='text-align: center; color: black'>%s - %s</h3>"%(applicationName, deviceName), unsafe_allow_html=True)

    st.markdown("<h5 style='text-align: right; color: black'>Date: %s</h5>"%(str(datetime.now()).split()[0]), unsafe_allow_html=True)
        # st.markdown("**Date:** "+str(datetime.now()).split()[0])


    dataReq = requests.post(SERVER_URI+"/dashboard/data",json = {
            "clientId": clients,
            "applicationId": applicationId,
            "apiKey": API_KEY
    })

    dataJson = dataReq.json()["data"]

    data = []

    paraReq = requests.post(SERVER_URI+"/dashboard/headers",json = {
            "applicationId": applicationId,
            "apiKey": API_KEY
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

        if(len(clients)==0):
            st.error("No Metrics Found!")
        else:
            metrics = requests.post(SERVER_URI+"/dashboard/metrics",json = {    
                    "clientId": clients[0],
                    "applicationId": applicationId,
                    "apiKey": API_KEY
            })

            metrics = metrics.json()
            print(metrics)

            if(len(metrics.keys())==0):
                st.error("No Metrics Found!")
            else:
                metricRows = []

                rowSize = 6

                rem = len(metrics["metrics"])%rowSize

                for i in range(len(metrics["metrics"])//rowSize):
                    metricRows.append(st.columns(rowSize))

                metricRows.append(st.columns(rowSize))

                for i in range(len(metricRows)):
                    for j in range(min(rowSize,len(metrics["metrics"])-(rowSize*i))):
                        metricRows[i][j].metric(list(metrics["metrics"].keys())[i*rowSize+j], metrics["metrics"][list(metrics["metrics"].keys())[i*rowSize+j]])
                        if(list(metrics["metrics"].keys())[i*rowSize+j] in metrics["images"].keys()):
                            metricRows[i][j].image(metrics["images"][list(metrics["metrics"].keys())[i*rowSize+j]])

    st.header("Data Analysis")

    options = {
        "xAxis": {
            "type": "category",
            "data": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        },
        "yAxis": {"type": "value"},
        "series": [
            {"data": [820, 932, 901, 934, 1290, 1330, 1320], "type": "line"}
        ],
    }


    st_echarts(options=options)

    st.header("Data")
    if(df.empty):
        st.error("No Data Found!")
    else:
        st.table(df)

        csv = convert_df(df)

        st.sidebar.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='data.csv',
            mime='text/csv',
        )

def registerApplication(applicationId):
    st.header("Register Application")

    if(applicationId==None):      
        applicationName = st.text_input('Application Name')

        dataParameters = st.text_area("Data Parameters", value=json.dumps({"timestamp": "Timestamp"}, sort_keys=True, indent=4))

        metricParameters = st.text_area("Metric Parameters", value=json.dumps({"timestamp": "Timestamp"}, sort_keys=True, indent=4))
    else:
        applicationReq = requests.post(SERVER_URI+"/dashboard/application/info",json={
            "apiKey":API_KEY,
            "applicationId": applicationId
        })

        applicationRes = applicationReq.json()["applicationInfo"]

        applicationName = st.text_input('Application Name', value=applicationRes["applicationName"])

        dataParameters = st.text_area("Data Parameters", value=json.dumps(applicationRes["dataParameters"], sort_keys=True, indent=4))

        metricParameters = st.text_area("Metric Parameters", value=json.dumps(applicationRes["metricParameters"], sort_keys=True, indent=4))

    submitToggle = st.button("Submit")
        
    if(submitToggle):

        if(applicationName.strip()==""):
            st.error("Application Name cannot be blank!")
            return

        try:
            dataParameters = json.loads(dataParameters)
        except Exception as e:
            st.error("Data Parametres must be JSON!")
            return

        try:
            metricParameters = json.loads(metricParameters)
        except Exception as e:
            st.error("Metric Parametres must be JSON!")
            return
        
        if(applicationId==None):
            applicationRegistrationReq = requests.post(SERVER_URI + "/dashboard/application/register", json = {
                "apiKey": API_KEY,
                "applicationName": applicationName,
                "dataParameters": dataParameters,
                "metricParameters": metricParameters
            })

            applicationRegistrationRes = applicationRegistrationReq.json()
            
            if(applicationRegistrationRes["status"]=="Success"):
                st.success("Successfully Registered Application!")
            else:
                st.success("Failed to Register Application!")
        else:

            applicationRegistrationReq = requests.post(SERVER_URI + "/dashboard/application/update", json = {
                "apiKey": API_KEY,
                "applicationId": applicationId,
                "applicationName": applicationName,
                "dataParameters": dataParameters,
                "metricParameters": metricParameters
            })

            applicationRegistrationRes = applicationRegistrationReq.json()
            
            if(applicationRegistrationRes["status"]=="Success"):
                st.success("Successfully Updated Application!")
            else:
                st.success("Failed to Update Application!")


def loggedIn():

    clients, deviceName, applicationName, applicationId, aggr, page = show_sidebar()

    if(page=="Dashboard"):        
        show_data(clients, deviceName, applicationName, applicationId, aggr)
    elif(page=="Register Application"):
        registerApplication(applicationId)
    else:
        show_data(clients, deviceName, applicationName, applicationId, aggr)

client = MongoClient(os.getenv('MONGO_URI'))

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

names = eval(os.getenv('NAMES'))
usernames = eval(os.getenv('USERNAMES'))
passwords = eval(os.getenv('PASSWORDS'))

hashed_passwords = stauth.hasher(passwords).generate()

authenticator = stauth.authenticate(names,usernames,hashed_passwords,
    'some_cookie_name','some_signature_key',cookie_expiry_days=30)

# @st.cache(allow_output_mutation=True)
# def get_base64_of_bin_file(bin_file):
#     with open(bin_file, 'rb') as f:
#         data = f.read()
#     return base64.b64encode(data).decode()

# def set_png_as_page_bg(png_file):
#     bin_str = get_base64_of_bin_file(png_file)
#     page_bg_img = '''<style>
# .stApp {
#     background-image: url("data:image/png;base64,%s");
#     background-size: cover;
# }
# </style>'''%bin_str
    
#     st.markdown(page_bg_img, unsafe_allow_html=True)

# set_png_as_page_bg('background.png')

padding_top = 2
padding_side = 4
padding_bottom = 2
st.markdown(f""" <style>
    .main .block-container{{
        padding-top: {padding_top}rem;
        padding-right: {padding_side}rem;
        padding-left: {padding_side}rem;
        padding-bottom: {padding_bottom}rem;
    }} </style> """, unsafe_allow_html=True)

cols = st.columns([1,6,1])

with cols[0]:
    st.image(wce75)

with cols[1]:
    st.markdown("<h1 style='text-align: center; color: red'>Walchand College of Engineering, Sangli</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: blue'>Department of Computer Science and Engineering</h3>", unsafe_allow_html=True)


with cols[2]:
    st.image(wceLogo)

st.markdown("<h2 style='text-align: center;'>AI IoT Dashboard</h2>", unsafe_allow_html=True)
name, authentication_status = authenticator.login('Login','main')

if authentication_status: 
    loggedIn()    
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')