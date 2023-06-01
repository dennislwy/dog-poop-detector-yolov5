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
    def __init__(self,
                 sound,
                 no_alert,
                 notify_img,
                 no_notify,
                 notifier: INotification,
                 logger,
                 confirm_sec = 3, # time to confirm if there is poop
                 confirm_thres = 0.75, # poop confirmation threshold
                 alert_grace_sec = 900, # alert grace period (in seconds)
        ):

        self.log = logger
        self.notifier = notifier
        self.sound = sound

        # for alert & notification
        self.no_alert = no_alert
        self.no_notify = no_notify
        self.notify_img = notify_img
        self._alert_grace_period_seconds = alert_grace_sec

        # for measuring fps
        self.fps = 0.0
        self._fps_cnt = 0
        self._fps_measure_start = 0

        # for poop confirmation
        self._poop_confirm_seconds = confirm_sec
        self._poop_confirm_threshold = confirm_thres

        # for poop detection rolling window
        self._queue_length = 0
        self._poop_detect_queue = deque([0] * 2, maxlen=2)

        # for poop detection rolling average
        self._rolling_avg = ValueTracker(initial_value=0)
        self._last_poop_check_time = time.time()
        self._last_poop_confirmed_time = 0

    def process_detection(self, pred, im0):
        fps = self.measure_fps()

        # dynamically adjust detect queue length
        if self._queue_length  == 0 and fps > 0:
            self._queue_length  = max(6, math.ceil(fps*self._poop_confirm_seconds))
            self._poop_detect_queue = deque([0] * self._queue_length , maxlen=self._queue_length)
            self.log.info(f"Queue length adjusted to {self._queue_length}")

        poop_in_detections = self.is_poop_in_detections(pred)
        dog_in_detections = self.is_dog_in_detections(pred)

        if fps > 0:
            print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S.%f")[:-3]}, Dog: {dog_in_detections}, Poop: {poop_in_detections}, fps: {fps}')

        # add poop in detection to rolling window
        self._poop_detect_queue.append(1 if poop_in_detections else 0)

        # is time to check rolling average?
        if time.time() < self._last_poop_check_time + self._poop_confirm_seconds:
            return

        # update last poop check time
        self._last_poop_check_time = time.time()

        # confirm got poop?
        if self.check_poop_confirmation():
            # poop confirmed
            self.poop_confirmed(im0)

    def measure_fps(self) -> float:
        """
        Measures frames per second (FPS) of a process.

        Returns:
            float: Current FPS value.
        """
        self._fps_cnt += 1  # Increment frame count by 1

        if self._fps_cnt == 1:  # If it's the first frame
            self._fps_measure_start = time.time()  # Start measuring time

        elapsed = time.time() - self._fps_measure_start  # Calculate elapsed time since measurement started

        if elapsed > 10:  # If more than 10 seconds have passed
            self.fps = round(self._fps_cnt / elapsed, 2)  # Calculate FPS by dividing frame count by elapsed time
            self._fps_cnt = 0  # Reset frame count for the next measurement

        return self.fps  # Return the current FPS value

    def is_dog_in_detections(self, pred):
        return CLASS_DOG in pred[0][:, -1]

    def is_poop_in_detections(self, pred):
        return CLASS_POOP in pred[0][:, -1]

    def check_poop_confirmation(self):
        # update poop detection rolling average
        self._rolling_avg.update(np.mean(self._poop_detect_queue))

        # return if average value no change or queue yet fully fill
        if not self._rolling_avg.changed() or len(self._poop_detect_queue) != self.fps*self._poop_confirm_seconds:
            return False

        # log poop likelihood
        self.log.info(f'Poop likelihood: {round(self._rolling_avg.current*100, 2)}%')

        # poop confirmed when poop detection rolling average >= poop confirmation threshold
        if self._rolling_avg.current < self._poop_confirm_threshold:
            return False

        # clear once poop confirmed, helps w/ trailing additional poop detections due to filled queue
        self._poop_detect_queue.clear()

        # poop confirmed
        return True

    def poop_confirmed(self, im0):
        self.log.info("Poop confirmed")

        # calculate elapsed time (in seconds) since last poop confirmation
        last_poop_confirmed_elapsed_seconds = time.time() - self._last_poop_confirmed_time

        # update poop last confirmed time
        self._last_poop_confirmed_time = time.time()

        # sound alert & send notification if exceeded alert grace period since last poop confirmed time
        if last_poop_confirmed_elapsed_seconds >= self._alert_grace_period_seconds:

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
