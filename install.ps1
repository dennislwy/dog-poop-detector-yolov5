# create virtual environment
python -m venv venv

# activate virtual environment
& "venv/Scripts/Activate.ps1"

# install pytorch
pip install -r requirements.txt

# install yolov5
git clone https://github.com/ultralytics/yolov5
pip install -r yolov5/requirements.txt
