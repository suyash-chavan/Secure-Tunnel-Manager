import requests
import json

config_file = open("config.json")

CONFIG = json.load(config_file)

config_file.close()

device_name = input("Enter Name of the device: ")

public_key = ''

with open('~/.ssh/id_rsa.pub', 'r') as file:
    public_key = public_key + file.read().replace('\n', '')

x = requests.post('https://' + CONFIG.WATCHMAN_IP + ":" + CONFIG.WATCHMAN_PORT + "/register", data= {
    "device_name": device_name,
    "device_key": public_key, 
});

