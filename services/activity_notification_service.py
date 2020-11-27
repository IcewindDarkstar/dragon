import time
import pytz
import dateutil.parser
from threading import Event

from typing import Callable, List

from services.restya_service import RestyaService


class ActivityNotificationService:

    def __init__(self, restya_service: RestyaService):
        self._restya_service = restya_service
        self.__activity_listeners = set()
        self._stop_event = Event()

    def add_activity_notification_listener(self, listener: Callable[[List], None]):
        self.__activity_listeners.add(listener)

    def start(self):
        last_update = None

        while not self._stop_event.is_set():
            activities = self._restya_service.get_activities()
            for ac in activities:
                ac['create_datetime'] = pytz.UTC.localize(dateutil.parser.parse(ac['created']))

            if last_update is not None:
                new_activities = [activity for activity in activities if activity['create_datetime'] > last_update]

                for listener in self.__activity_listeners:
                    listener(new_activities)

            last_update = activities[0]['create_datetime']
            self._stop_event.wait(60)

    def stop(self):
        self._stop_event.set()

