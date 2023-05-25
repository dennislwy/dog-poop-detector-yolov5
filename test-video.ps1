& "venv/Scripts/Activate.ps1"
python .\yolov5\detect.py --weights '.\yolov5\runs\train\exp4\weights\best.pt' --line-thickness 2 --conf-thres 0.5 --view-img --source 'dataset/tests/test1.mp4'
