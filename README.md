# Dog Poop Detector using YOLOv5

## Features
- [x] Live detect when dog pooped
    - [x] Play alert sound
    - [x] Send notification via Pushbullet
        - [ ] Attach detection image in notification
- [ ] Deployable on Raspberry Pi

## Live Detection Sample
![alt text](./docs/sample.gif "Live Detection 1")

## Use from yolov5 CLI
### Inference
```powershell
yolov5 detect --conf-thres 0.7 --line-thickness 2 --view-img --weights model.pt --source .\dataset\tests\test1.mp4
```
