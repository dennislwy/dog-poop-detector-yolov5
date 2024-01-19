#!/bin/bash

# create virtual environment
echo "Creating virtual environment"
python3 -m venv .venv

# activate virtual environment
echo "Activating virtual environment"
source .venv/bin/activate

# install packages
echo "Installing packages"
pip install -r requirements.txt
