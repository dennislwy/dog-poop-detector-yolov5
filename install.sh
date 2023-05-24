#!/bin/bash

# create virtual environment
python -m venv venv

# activate virtual environment
source venv/bin/activate

# install pytorch
pip install -r requirements.txt

# install yolov5
git clone https://github.com/ultralytics/yolov5
pip install -r yolov5/requirements.txt
