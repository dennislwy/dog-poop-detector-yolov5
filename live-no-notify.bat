@echo off

call venv\Scripts\activate
python live.py --weights poop.pt --cfg config-private.json --view-img --nosave --no-notify --source rtsp://administrator:venger814@reflexpointkr.asuscomm.com:50005/stream1
