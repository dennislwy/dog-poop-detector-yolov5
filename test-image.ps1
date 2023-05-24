& "venv/Scripts/Activate.ps1"
python yolov5/detect.py --weights 'yolov5/runs/train/exp2/weights/best.pt' --view-img --source 'data/tests/test.jpg'
