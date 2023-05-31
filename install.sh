#!/bin/bash

# create virtual environment
python -m venv venv

# activate virtual environment
source venv/bin/activate

# install packages
pip install -r requirements.txt
