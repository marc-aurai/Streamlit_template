#!/bin/bash

sudo systemctl daemon-reload
sudo systemctl start streamlit.service    # starts up the service
sudo systemctl status streamlit.service   # prints the status to the log