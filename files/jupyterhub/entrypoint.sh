#!/bin/bash

USER_LIST="/srv/jupyterhub/user_list.txt"
if [ -f $USER_LIST ]; then
  while read l; do
    USERNAME="$(cut -d':' -f1 <<< $l)"
    PASSWORD="$(cut -d':' -f2 <<< $l)"
    getent passwd $USERNAME  2> /dev/null
    if [ $? -ne 0 ]; then
      echo "Adding user ${USERNAME}"
      useradd -m $USERNAME
      echo "$USERNAME:$PASSWORD" | chpasswd
    fi
  done < $USER_LIST
fi

jupyterhub
