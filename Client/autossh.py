#!/usr/bin/env python3

import re
import subprocess
import json
import requests

config_file = open("./config.json")

CONFIG = json.load(config_file)

config_file.close()

def run_autossh():
    try:
        ssh_command= "autossh -f -N -R {}:localhost:22 {}@{}".format(CONFIG["clientDedicatedPort"], CONFIG["WATCHMAN_USERNAME"], CONFIG["WATCHMAN_IP"])
        ssh_output = subprocess.check_output(ssh_command, shell=True)
        if not ssh_output:
            print("Successful")
    except subprocess.CalledProcessError as e:
        print("Failed. Please check your config file.")

def awake():
    x = requests.post('http://' + CONFIG["WATCHMAN_IP"] + ":" + CONFIG["WATCHMAN_PORT"] + "/awake", json= {
        "clientName": CONFIG["CLIENT_NAME"],
        "clientId": CONFIG["clientId"], 
    });

if __name__=="__main__":
    run_autossh()
