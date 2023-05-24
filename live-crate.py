import os
import torch
import numpy as np
import cv2


def find_latest_exp(path):
  exp_folders = [folder for folder in os.listdir(path) if folder.startswith('exp')]

  if exp_folders:
      latest_exp = max(exp_folders, key=lambda x: 0 if x=='exp' else int(x[3:]))
      print("Latest exp number:", latest_exp)
  else:
      print("No 'exp' folders found.")
      latest_exp = 'exp'

  return latest_exp

train_path = 'yolov5/runs/train'
latest_exp = find_latest_exp(train_path)

model_path = f'{train_path}/{latest_exp}/weights/best.pt'

print(f"Loading model '{model_path}'")
model = torch.hub.load('ultralytics/yolov5', 'custom', path=model_path, force_reload=True)

# stream url
stream_url = 'rtsp://administrator:venger814@reflexpointkr.asuscomm.com:50005/stream1'

# start live detection
cap = cv2.VideoCapture(stream_url)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Make detections
    results = model(frame)

    cv2.imshow('Dog Poop Detector', np.squeeze(results.render()))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
