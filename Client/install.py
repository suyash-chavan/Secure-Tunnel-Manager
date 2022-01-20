import requests
import json

with open('config.json') as f:
    CONFIG = json.load(f)

device_name = input("Enter Name of the device: ")

public_key = ''

with open('/root/.ssh/id_rsa.pub', 'r') as file:
    public_key = public_key + file.read().replace('\n', '')

x = requests.post('http://' + CONFIG["WATCHMAN_IP"] + ":" + CONFIG["WATCHMAN_PORT"] + "/client/register", json= {
    "clientName": device_name,
    "clientKey": public_key 
});

res = x.json()

for key in res.keys():
    CONFIG[key] = res[key]

with open('config.json', 'w') as f:
    json.dump(CONFIG, f)