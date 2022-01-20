#!/bin/bash

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [[ -z "${WATCHMAN_PASSWORD}" ]]; then
  echo "You need to set env variable WATCHMAN_PASSWORD first."
  exit
fi

usermod watchman
 
usermod --password $(echo "$WATCHMAN_PASSWORD" | openssl passwd -1 -stdin) watchman

FILE=/home/watchman/.ssh/authorized_keys

if [ -f "$FILE" ]; then
    echo "$FILE exists."
else 
    touch $FILE
fi
