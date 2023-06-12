import os
import time
import math
import threading
import numpy as np
from datetime import datetime
from collections import Counter
from utils.value import ValueTracker
from collections import deque
from utils.sound import play_audio_file
from utils.pushbullet import INotification
from yolov5.utils.general import cv2

CLASS_POOP_LABEL = 'poop' # poop class label
MIN_QUEUE_LENGTH = 3

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
                 alert_snooze_sec = 300, # alert snooze period (in seconds)
        ):

        self.log = logger
        self.notifier = notifier
        self.sound = sound

        # for alert & notification
        self.no_alert = no_alert
        self.no_notify = no_notify
        self.notify_img = notify_img
        self._alert_snooze_period_seconds = alert_snooze_sec

        # for measuring fps
        self.fps = 0.0
        self._fps_cnt = 0
        self._fps_measure_start = 0
        self._fps_refresh_sec = 10

        # for class count
        self._detected_class_count = ValueTracker(initial_value={})

        # for poop confirmation
        self._poop_confirm_seconds = confirm_sec
        self._poop_confirm_threshold = confirm_thres

        # for poop detection rolling window
        self._queue_length = ValueTracker(initial_value=0)
        self._poop_detect_queue = deque([0] * MIN_QUEUE_LENGTH, maxlen=MIN_QUEUE_LENGTH)

        # for poop detection rolling average
        self._rolling_avg = ValueTracker(initial_value=0)
        self._last_poop_check_time = time.time()
        self._last_poop_confirmed_time = 0

    def process_detection(self, model, pred, im0):
        # measure detection processing speed (in fps)
        self.measure_fps()

        # dynamically adjust detect queue length
        if self._queue_length.current == 0 and self.fps > 0:
            self.reset_queue()

        # counts the number of detected objects for each class in the given prediction
        self._detected_class_count.update(self.detected_class_counts(model, pred))
        detected_class_and_counts_text = ', '.join([f"{class_label}: {count}" for class_label, count in self._detected_class_count.current.items()])

        # log when detected class count changed
        if self._detected_class_count.changed() and len(detected_class_and_counts_text) > 0:
            self.log.info(detected_class_and_counts_text)

        # if self.fps > 0:
        #     print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S.%f")[:-3]}, {detected_class_and_counts_text}, fps: {self.fps:.2f}')
        # else:
        #     print(f'{datetime.now().strftime("%Y%m%d %H:%M:%S.%f")[:-3]}, {detected_class_and_counts_text}')

        # add poop in detection to rolling window
        self._poop_detect_queue.append(1 if CLASS_POOP_LABEL in self._detected_class_count.current else 0)

        # is time to check rolling average?
        if time.time() < self._last_poop_check_time + self._poop_confirm_seconds:
            return

        # update last poop check time
        self._last_poop_check_time = time.time()

        # confirm got poop?
        if self.check_poop_confirmation():
            # poop confirmed
            self.poop_confirmed(im0.copy())

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

        if elapsed > self._fps_refresh_sec:  # If more than 10 seconds have passed
            self.fps = self._fps_cnt / elapsed # Calculate FPS by dividing frame count by elapsed time
            self._fps_cnt = 0  # Reset frame count for the next measurement

        return self.fps  # Return the current FPS value

    def detected_class_counts(self, model, pred):
        """
        Counts the number of detected objects for each class in the given prediction.

        Args:
            model: The object detection model used for prediction.
            pred: The prediction result from the model.

        Returns:
            A Counter object that maps each class label to the number of detected objects.
        """

        # Get the class labels from the model
        class_labels = model.names

        # Initialize a dictionary to store the counts of each class
        class_counts_dict = Counter()

        # Iterate over the detected objects in the prediction
        for obj in pred[0]:
            # Extract the class ID and label for the current object
            class_id = int(obj[5])
            class_label = class_labels[class_id]

            # Update the class counts by incrementing the count for the detected class
            class_counts_dict[class_label] += 1

        return class_counts_dict

    def reset_queue(self):
        self._queue_length.update(max(MIN_QUEUE_LENGTH, math.ceil(self.fps*self._poop_confirm_seconds)))
        if self._queue_length.changed():
            self.log.info(f"FPS: {self.fps:2f}, queue length adjusted to {self._queue_length.current}")

        self._poop_detect_queue = deque([0] * self._queue_length.current , maxlen=self._queue_length.current)

    def check_poop_confirmation(self):
        # update poop detection rolling average
        self._rolling_avg.update(np.mean(self._poop_detect_queue))

        # return if average value no change or queue yet fully fill
        if not self._rolling_avg.changed():
            return False

        # log poop likelihood
        self.log.info(f'Poop likelihood: {round(self._rolling_avg.current*100, 2)}%')

        # poop confirmed when poop detection rolling average >= poop confirmation threshold
        if self._rolling_avg.current < self._poop_confirm_threshold:
            return False

        # clear once poop confirmed, helps w/ trailing additional poop detections due to filled queue
        # self._poop_detect_queue.clear()
        self.reset_queue()

        # poop confirmed
        return True

    def poop_confirmed(self, im):
        self.log.info("Poop confirmed")

        # calculate elapsed time (in seconds) since last poop confirmation
        last_poop_confirmed_elapsed_seconds = time.time() - self._last_poop_confirmed_time

        # update poop last confirmed time
        self._last_poop_confirmed_time = time.time()

        # sound alert & send notification if exceeded alert snooze period since last poop confirmed time
        if last_poop_confirmed_elapsed_seconds >= self._alert_snooze_period_seconds:

            # play alert sound on another thread
            if not self.no_alert:
                threading.Thread(target=self.play_alert).start()

            # send notification on another thread
            if not self.no_notify:
                if self.notify_img:
                    threading.Thread(target=self.push_text_img, args=(im,)).start()
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
