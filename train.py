import os
import time
import argparse
from PIL import Image
from yolov5 import train

def elapsed_time(elapsed_sec):
  hours = int(elapsed_sec // 3600)
  minutes = int((elapsed_sec % 3600) // 60)
  seconds = int(elapsed_sec % 60)

  # Display the execution time
  print(f"Execution time: {hours}hr {minutes}min {seconds}sec")

def find_latest_exp(path):
  exp_folders = [folder for folder in os.listdir(path) if folder.startswith('exp')]

  if exp_folders:
      latest_exp = max(exp_folders, key=lambda x: 0 if x=='exp' else int(x[3:]))
      print("Latest experiment number:", latest_exp)
  else:
      print("No 'exp' folders found.")
      latest_exp = 'exp'

  return latest_exp

def run(weights,
        data,
        epochs,
        batch_size,
        imgsz,
        workers
    ):

    # delete label cache
    label_cache_path = 'dataset/labels.cache'
    if os.path.isfile(label_cache_path):
        os.remove(label_cache_path)

    # measure execution time
    start_time = time.time()

    # start training
    train.run(imgsz=imgsz, batch_size=batch_size, epochs=epochs, data=data, weights=weights, workers=workers)

    elapsed_time(time.time() - start_time)

    # get latest experiment
    train_path = 'runs/train'
    latest_exp = find_latest_exp(train_path)

    # Visualize training result
    image_path = f'{train_path}/{latest_exp}/results.png'
    image = Image.open(image_path)

    # Display the image
    image.show()

def parse_opt():
    parser = argparse.ArgumentParser(description='YOLOv5 model training tool')
    parser.add_argument('--weights', type=str, default='yolov5s.pt', help='initial weights path')
    parser.add_argument('--data', type=str, default='dataset.yaml', help='dataset.yaml path')
    parser.add_argument('--epochs', type=int, default=100, help='total training epochs')
    parser.add_argument('--batch-size', type=int, default=16, help='total batch size for all GPUs, -1 for autobatch')
    parser.add_argument('--imgsz', '--img', '--img-size', type=int, default=640, help='train, val image size (pixels)')
    parser.add_argument('--workers', type=int, default=8, help='max dataloader workers (per RANK in DDP mode)')
    opt = parser.parse_args()
    return opt

def main(opt):
    run(**vars(opt))

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)
