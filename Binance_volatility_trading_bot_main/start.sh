#!/bin/bash

# Start the first process
(cd UI ; streamlit run streamlit_page.py) &
# Start the second process
python BinanceDetectMoonings.py

