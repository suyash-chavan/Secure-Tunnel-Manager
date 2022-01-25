#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi


while true
do
	./python autossh.py
    wait $!
	sleep 3
done 