import os
import requests
import json
import string
import secrets
import crypt

with open('config.json') as f:
    CONFIG = json.load(f)

device_name = input("Enter Name of the device: ")

public_key = ''

with open('/root/.ssh/id_rsa.pub', 'r') as file:
    public_key = public_key + file.read().replace('\n', '')

passwd = ''.join(secrets.choice(string.ascii_letters + string.digits) for x in range(32))

try:
    x = requests.post('http://' + CONFIG["WATCHMAN_IP"] + ":" + CONFIG["WATCHMAN_PORT"] + "/client/register", json= {
        "clientName": device_name,
        "clientKey": public_key,
        "clientPassword": passwd
    });
except Exception as e:
    print("Check internet connection and confirm Server Status!")
    exit(0)

if(x.status_code != 200):
    print("Make sure if client is connected to Internet!")
    exit(0)

passHash = crypt.crypt(passwd)

res = x.json()

for key in res.keys():
    CONFIG[key] = res[key]

CONFIG["CLIENT_NAME"] = device_name

with open('config.json', 'w') as f:
    json.dump(CONFIG, f)

os.system("mkdir /root/Secure-Tunnel/")
os.system("cp secure-tunnel.service /etc/systemd/system")
os.system("cp autossh.py /root/Secure-Tunnel/")
os.system("cp config.json /root/Secure-Tunnel/")
os.system("`echo 'root:{}' | chpasswd -e`".format(passHash))
os.system('echo "PermitRootLogin yes" >> /etc/ssh/sshd_config')
os.system("systemctl restart sshd.service")
os.system("systemctl daemon-reload")
os.system("systemctl start secure-tunnel.service")
