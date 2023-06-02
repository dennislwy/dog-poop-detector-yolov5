# Dog Poop Detector using YOLOv5

## Features
- [x] Live detect when dog pooped
    - [x] Play alert sound
    - [x] Send notification via Pushbullet
        - [x] Attach detection image in notification
- [ ] Deployable to Raspberry Pi

## Live Detection
**RTSP Stream**
```bash
python live.py --weights poop.pt --view-img --nosave --notify-img --source rtsp://your_rtsp_url
```

**Testing with MP4 video**
```bash
python live.py --weights poop.pt --view-img --nosave --no-notify --source dataset/tests/test1.mp4
```

### Sample Detection
![alt text](./docs/sample.gif "Live Detection 1")

<video controls>
  <source src="./docs/sample1.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

## Testing from yolov5 CLI
### Inference
```bash
yolov5 detect --conf-thres 0.7 --line-thickness 2 --view-img --weights poop.pt --source dataset/tests/test1.mp4
```
