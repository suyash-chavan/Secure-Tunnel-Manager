#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

apt install python3 openssh-server openssh-client autossh

FILE=/root/.ssh/id_rsa
if [ ! -f "$FILE" ]; then
    ssh-keygen -q -t rsa -N '' <<< $'\ny' >/dev/null 2>&1
    echo "Created Keys !"
fi