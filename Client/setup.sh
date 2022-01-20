#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

ssh-keygen -q -t rsa -N '' <<< $'\ny' >/dev/null 2>&1