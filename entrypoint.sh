#!/bin/sh

if [ "$APP_MODE" = "grab_cookies" ]; then
    echo "Starting grab_cookies.py (Author: Ugo Fiasconaro)..."
    python -i grab_cookies.py
else
    echo "Starting uvicorn server (send_message.py) (Author: Ugo Fiasconaro)..."
    python send_message.py
fi