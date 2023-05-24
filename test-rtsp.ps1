& "venv/Scripts/Activate.ps1"
python yolov5/detect.py --weights 'yolov5/runs/train/exp2/weights/best.pt' --line-thickness 2 --conf-thres 0.5 --source 'rtsp://your_rtsp_url'
