import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import streamlit_authenticator as stauth
from PIL import Image
import math

load_dotenv()

class Sidebar:
    def __init__(self, SERVER_URI, API_KEY):

        self.st = st

        # Variables containing
        self.username = ""
        self.applicationsShow = True
        self.applications = []
        self.dataAggregationToggle = False
        self.clientsShow = True
        self.clients = []
        self.registerToggle = False
        self.about = ""
        self.reportBug = ""
        self.applicationsDropdown = []
        self.clientsDropdown = []
        self.dataAggregationCheckBox = False
        self._SERVER_URI = SERVER_URI
        self._API_KEY = API_KEY

    def updateUI(self):
        self.username_label = self.st.sidebar.markdown(
            'Welcome **%s**, <hr />' % (self.username), unsafe_allow_html=True)

        if(self.applicationsShow):
            self.applicationsDropdown = self.st.sidebar.selectbox(
                "Application", self.applications, key = 'applicationDropdown')
            self.dataAggregationCheckBox = self.st.sidebar.checkbox(
                'Data Aggregation')

            if(self.dataAggregationCheckBox):
                self.clientsDropdown = self.st.sidebar.multiselect(
                    'Device Name', self.clients)
            else:
                self.clientsDropdown = self.st.sidebar.selectbox(
                    "Device Name", self.clients)

            self.downloadContainer =  self.st.sidebar.container()

        self.st.sidebar.markdown("<hr />", unsafe_allow_html=True)

        with self.st.sidebar.expander("More Options"):
            self.registerToggle = self.st.button("Register Application")

        with self.st.sidebar.expander("About"):
            self.st.write(self.about)

        with self.st.sidebar.expander("Report Bug"):
            self.st.write(self.reportBug)

    def updateData(self):
        applicationsReq = requests.get(self._SERVER_URI+"/dashboard/applications", json={
            "apiKey": self._API_KEY
        })

        applicationsRes = applicationsReq.json()

        applications = {}

        for app in applicationsRes["applications"]:
            applications[app["applicationName"]] = app["applicationId"]

        # Update Applications
        self.applications = applications.keys()

        clientsReq = requests.post(self._SERVER_URI+"/dashboard/clients", json={
            "applicationId": applications[self.applicationsDropdown],
            "apiKey": self._API_KEY
        })

        clientsRes = clientsReq.json()

        clients = {}

        for cli in clientsRes["clients"]:
            clients[cli["clientName"]] = cli["clientId"]

        # Update Clients
        self.clients = clients.keys()

    def update(self):
        self.updateData()
        self.updateUI()

class Dashboard:

    def __init__(self):
        self.st = st
        self.sidebarToggle = True

        self._SERVER_URI = os.getenv("SERVER_URI")
        self._API_KEY = os.getenv("API_KEY")
        self.state = "dashboard"
        self.sidebar = Sidebar(self._SERVER_URI, self._API_KEY)

        if(self._SERVER_URI == None or self._API_KEY == None):
            print("[ERROR] Environment Variables Missing!")
            exit(1)

    def displayRegister():
        pass

    def convert_df(self, dataframe):
        return dataframe.to_csv().encode('utf-8')

    def displayData(self):

        if(not self.sidebar.dataAggregationCheckBox):

            self.st.header("Metrics")

            if(len(self.sidebar.clients) == 0):
                self.st.error("No Metrics Found!")
            else:
                metricsReq = requests.post(self._SERVER_URI + "/dashboard/metrics", json={
                    "clientId": self.sidebar.clientsDropdown,
                    "applicationId": self.sidebar.applicationsDropdown,
                    "apiKey": self._API_KEY
                })

                metricsRes = metricsReq.json()

                metrics = metricsRes["metrics"]

                if(len(metrics) == 0):
                    self.st.error("No Metrics Found!")
                else:
                    metricRows = []

                    for i in range(math.ceil(len(metrics)/3)):
                        metricRows.append(self.st.columns(3))

                    for i in range(len(metricRows)):
                        for j in range(min(3, len(metrics)-(3*i))):
                            metricRows[i][j].metric(
                                metrics[i*3+j]["name"], metrics[i*3+j]["value"])

        self.st.header("Data")

        dataParaReq = requests.post(self._SERVER_URI+"/dashboard/headers",json = {
            "applicationId": self.sidebar.applications,
            "apiKey": self._API_KEY
        })

        dataParaRes = dataParaReq.json()
        dataPara = dataParaRes["dataParameters"]

        columnHeaders = dataPara.keys()
        
        dataReq = requests.post(self._SERVER_URI+"/dashboard/data",json = {
            "clientId": self.sidebar.clientsDropdown,
            "applicationId": self.sidebar.applicationsDropdown,
            "apiKey": self._API_KEY
        })

        dataRes = dataReq.json()

        data = dataRes["data"]

        table = []

        for dataPoint in data:
            row = []

            for header in columnHeaders:
                if(header in dataPoint.keys()):
                    row.append(dataPoint[header])
                else:
                    row.append("-")

            table.append(row)
        
        dataframe = pd.DataFrame(data, columns=columnHeaders)

        if(dataframe.empty):
            self.st.error("No Data Found!")
        else:
            self.st.table(dataframe)

            csv = self.convert_df(dataframe)

            with self.sidebar.downloadContainer:
                self.st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name='data.csv',
                    mime='text/csv',
                )

    def updateHeader(self):
        cols = self.st.columns([2, 1, 2])

        wceLogo = Image.open('wce.png')

        with cols[1]:
            self.st.image(wceLogo)

        self.st.markdown(
            "<h2 style='text-align: center;'>IoT Dashboard & Management</h2>", unsafe_allow_html=True)

    def displayDahboard(self):
        if(self.sidebarToggle):
            self.sidebar.update()

        if(self.state=="register"):
            self.displayRegister()
        else:
            self.displayData()

    def update(self):

        self.updateHeader()

        self.username, self.loginStatus = authenticator.login('Login', 'main')

        if self.loginStatus:
            self.displayDahboard()
        elif self.loginStatus == False:
            self.st.error('Username/password is incorrect')
        elif self.loginStatus == None:
            self.st.warning('Please enter your username and password')

if __name__=="__main__":
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

    dashboard = Dashboard()
    dashboard.update()