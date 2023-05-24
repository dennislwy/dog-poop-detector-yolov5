& "venv/Scripts/Activate.ps1"
python yolov5/detect.py --weights 'yolov5/runs/train/exp2/weights/best.pt' --img 2304 --view-img --source 'data/tests/test.mp4'
