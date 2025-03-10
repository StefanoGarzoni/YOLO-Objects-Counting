#!/bin/bash

app_name="mainOUT.py"

if pgrep -f "$app_name" >/dev/null; then
    pkill -f "$app_name"
    sleep 3  #Optional
fi

#echo "Starting $app_name..."
python3 mainOUT.py &

#echo "$app_name was started."

