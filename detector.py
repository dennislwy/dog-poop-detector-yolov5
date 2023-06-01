import os
import time
import math
import threading
import numpy as np
from datetime import datetime
from utils.value import ValueTracker
from collections import deque
from utils.sound import play_audio_file
from utils.pushbullet import INotification
from yolov5.utils.general import cv2

CLASS_DOG = 0 # dog detection class
CLASS_POOP = 1 # poop detection class

class PoopDetector:
    def __init__(self, sound, no_alert, notify_img, no_notify, notifier: INotification, logger):
        self.log = logger
        self.notifier = notifier
        self.sound = sound

        self.no_alert = no_alert
        self.no_notify = no_notify

        self.notify_img = notify_img

        self.fps = 3
        self.seconds_to_confirm_poop = 3

        self.poop_confirm_threshold = 0.75

        # poop detection rolling window
        queue_length = math.ceil(self.fps*self.seconds_to_confirm_poop)
        self.poop_detect_queue = deque([0] * queue_length, maxlen=queue_length)

        # poop detection rolling average
        self.rolling_avg = ValueTracker(initial_value=0)

        self.last_poop_check_time = time.time()

        self.alert_grace_period_seconds = 900 # 15 minutes (in seconds)

        self.last_poop_confirmed_time = 0

    def process_detection(self, pred, im0):
        poop_in_detections = self.is_poop_in_detections(pred)
        dog_in_detections = self.is_dog_in_detections(pred)

        print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S.%f")[:-3]}, Dog: {dog_in_detections}, Poop: {poop_in_detections}')

        # add poop in detection to rolling window
        self.poop_detect_queue.append(1 if poop_in_detections else 0)

        # is time to check rolling average?
        if time.time() < self.last_poop_check_time + self.seconds_to_confirm_poop:
            return

        # update last poop check time
        self.last_poop_check_time = time.time()

        # confirm got poop?
        if self.check_poop_confirmation():
            # poop confirmed
            self.poop_confirmed(im0)

    def is_dog_in_detections(self, pred):
        return CLASS_DOG in pred[0][:, -1]

    def is_poop_in_detections(self, pred):
        return CLASS_POOP in pred[0][:, -1]

    def check_poop_confirmation(self):
        # update poop detection rolling average
        self.rolling_avg.update(np.mean(self.poop_detect_queue))

        # return if average value no change or queue yet fully fill
        if not self.rolling_avg.changed() or len(self.poop_detect_queue) != self.fps*self.seconds_to_confirm_poop:
            return False

        # log poop likelihood
        self.log.info(f'Poop likelihood: {round(self.rolling_avg.current*100, 2)}%')

        # poop confirmed when poop detection rolling average >= poop confirmation threshold
        if self.rolling_avg.current < self.poop_confirm_threshold:
            return False

        # clear once poop confirmed, helps w/ trailing additional poop detections due to filled queue
        self.poop_detect_queue.clear()

        # poop confirmed
        return True

    def poop_confirmed(self, im0):
        self.log.info("Poop confirmed")

        # calculate elapsed time (in seconds) since last poop confirmation
        last_poop_confirmed_elapsed_seconds = time.time() - self.last_poop_confirmed_time

        # update poop last confirmed time
        self.last_poop_confirmed_time = time.time()

        # sound alert & send notification if exceeded alert grace period since last poop confirmed time
        if last_poop_confirmed_elapsed_seconds >= self.alert_grace_period_seconds:

            # play alert sound on another thread
            if not self.no_alert:
                threading.Thread(target=self.play_alert).start()

            # send notification on another thread
            if not self.no_notify:
                if self.notify_img:
                    threading.Thread(target=self.push_text_img, args=(im0,)).start()
                else:
                    threading.Thread(target=self.push_text).start()

    def play_alert(self):
        self.log.info(f"Playing alert '{self.sound}'")
        play_audio_file(self.sound)

    def push_text(self):
        self.log.info("Pushing text")
        now_str = datetime.now().strftime("%I:%M:%S %p")
        self.notifier.text(f'{now_str} - Dog pooped!')

    def push_file(self, filepath, msg = None, title = None):
        self.log.info("Pushing text & image")
        self.notifier.file(filepath, msg, title)

    def push_text_img(self, im0):
        filepath = self.save_image(im0)
        now_str = datetime.now().strftime("%I:%M:%S %p")
        self.push_file(filepath, f'{now_str} - Dog pooped!')

    def save_image(self, im0):
        # use current time as output filename with the .jpg extension
        filename = f'poop-{datetime.now().strftime("%Y%m%d-%H%M%S")}.jpg'

        # Specify the path to the temporary folder
        folder_path = 'temp/'

        # Create the folder if it doesn't exist
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, filename)

        # save image
        cv2.imwrite(file_path, im0)

        return file_path
