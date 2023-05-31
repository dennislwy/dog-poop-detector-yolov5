import time
import threading
import numpy as np
from datetime import datetime
from utils.decorator import debounce
from utils.value import ValueTracker
from collections import deque
from utils.sound import play_audio_file

CLASS_DOG = 0
CLASS_POOP = 1

class PoopDetector:
    def __init__(self, sound, no_alert, notify_img, no_notify, notifier, logger):
        self.log = logger
        self.notifier = notifier
        self.sound = sound

        self.no_alert = no_alert
        self.no_notify = no_notify

        self.notify_img = notify_img

        self.fps = 5
        self.seconds_to_determine_poop = 3

        self.poop_detect_threshold = 0.75

        self.rolling_avg = ValueTracker(initial_value=0)
        self.poop_detect_queue = deque(maxlen=self.fps*self.seconds_to_determine_poop)
        self.poop_timestamp = time.time()

    def process_detections(self, pred):
        poop_in_detections = self.is_poop_in_detections(pred)
        dog_in_detections = self.is_dog_in_detections(pred)

        print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S")}, Dog: {dog_in_detections}, Poop: {poop_in_detections}')

        self.poop_detect_queue.append(1 if poop_in_detections else 0)

        # time to check rolling average
        if time.time() < self.poop_timestamp + self.seconds_to_determine_poop:
            return

        self.poop_timestamp = time.time()
        if self.check_rolling_average():
            self.poop_detected()

    def is_dog_in_detections(self, pred):
        return CLASS_DOG in pred[0][:, -1]

    def is_poop_in_detections(self, pred):
        return CLASS_POOP in pred[0][:, -1]

    def check_rolling_average(self):
        self.rolling_avg.update(np.mean(self.poop_detect_queue))

        if not self.rolling_avg.changed():
            return False

        self.log.info(f'Poop likelihood: {round(self.rolling_avg.current*100, 2)}%')

        if self.rolling_avg.current <= self.poop_detect_threshold or len(self.poop_detect_queue) != self.fps*self.seconds_to_determine_poop:
            return False

        # clear once poop detected, helps w/ trailing additional poo detections due to filled queue
        self.poop_detect_queue.clear()

        return True

    def poop_detected(self):
        self.log.info("Poop detected")

        # play alert sound on another thread
        if not self.no_alert:
            threading.Thread(target=self.play_alert).start()

        # send notification on another thread
        if not self.no_notify:
            threading.Thread(target=self.send_pushbullet).start()

    @debounce(300) # 5min
    def play_alert(self):
        self.log.info(f"Playing alert '{self.sound}'")
        play_audio_file(self.sound)

    @debounce(1800) # 30mins
    def send_pushbullet(self):
        self.log.info("Sending notification")
        self.notifier.text("Dog pooped!")
