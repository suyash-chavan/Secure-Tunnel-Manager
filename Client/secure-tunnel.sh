#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


while true
do
	/usr/bin/python3 /root/Secure-Tunnel/autossh.py
    wait $!
	sleep 3
done 