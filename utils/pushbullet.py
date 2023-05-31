import os
import logging
from typing import Optional
from pushbullet import Pushbullet


log = logging.getLogger()

from abc import ABC, abstractmethod
from typing import Optional


class INotification(ABC):
    @property
    @abstractmethod
    def title(self):
        raise NotImplementedError()

    @title.setter
    @abstractmethod
    def title(self, value: str):
        raise NotImplementedError()

    @abstractmethod
    def text(self, msg: str, title: Optional[str] = None):
        """
        Send out text notification

        :param msg: message
        :param title: message title
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def file(self, filepath: str, msg: str, title: Optional[str] = None):
        """
        Send a file

        :param filepath: File path of the upload file
        :param msg: message
        :param title: message title
        :return:
        """
        raise NotImplementedError()


class PushbulletNotification(INotification):
    def __init__(self, api_key: str, **kwargs):
        global log
        log = kwargs.get('logger', logging.getLogger())

        self._title = kwargs.get('title', None)
        self._n = Pushbullet(api_key)

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value

    def text(self, msg: str = None, title: Optional[str] = None):
        try:
            self._n.push_note(title=title if title else self._title, body=msg)
        except Exception as e:
            log.error(e, exc_info=True)

    def file(self, filepath: str, msg: str = None, title: Optional[str] = None):
        try:
            with open(filepath, "rb") as f:
                file_data = self._n.upload_file(f, os.path.basename(filepath))

            self._n.push_file(**file_data, title=title if title else self._title, body=msg)
        except Exception as e:
            log.error(e, exc_info=True)
