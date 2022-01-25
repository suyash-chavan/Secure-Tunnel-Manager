#!/usr/bin/env python

import re
import subprocess
import json
import requests

config_file = open("config.json")

CONFIG = json.load(config_file)

config_file.close()

def autossh_running():
    try:    
        out = subprocess.check_output("pgrep -x ssh", shell=True)
        print(out)
    except subprocess.CalledProcessError as e:
        print("Running and activating ssh. Please wait for 1 minute...")
    run_autossh()

def run_autossh():
    try:
        ssh_command= "autossh -M 22 -R {}:localhost:22 {}@{}".format(CONFIG["clientDedicatedPort"], CONFIG["WATCHMAN_USERNAME"], CONFIG["WATCHMAN_IP"])
        ssh_output = subprocess.check_output(ssh_command, shell=True)
        if not ssh_output:
            print("Successful")
    except subprocess.CalledProcessError as e:
        print("Failed. Please check your config file.")

def awake():
    x = requests.post('http://' + CONFIG["WATCHMAN_IP"] + ":" + CONFIG["WATCHMAN_PORT"] + "/register", json= {
        "clientName": CONFIG["CLIENT_NAME"],
        "clientId": CONFIG["clientId"], 
    });

if __name__=="__main__":
    awake()
    autossh_running()