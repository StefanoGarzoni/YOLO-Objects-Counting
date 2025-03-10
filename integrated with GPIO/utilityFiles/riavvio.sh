#!/bin/bash

app_name="main.py"

if pgrep -f "$app_name" >/dev/null; then
    pkill -f "$app_name"
    sleep 3  # Opzionale
fi

python3 main.py &

echo "$app_name è stato avviato."

