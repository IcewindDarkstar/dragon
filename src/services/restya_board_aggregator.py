from threading import Event

from typing import Callable, Dict

from services.restya_service import RestyaService
from services.channel_mapping_service import ChannelMappingService


class RestyaBoardAggregator:

    def __init__(self, restya_service: RestyaService, channel_mapping_service: ChannelMappingService, interval_s: int = 60 * 60):
        self._restya_service = restya_service
        self._channel_mapping_service = channel_mapping_service
        self._stop_event = Event()
        self._interval_s = interval_s
        self._listeners = set()

    def add_listener(self, listener: Callable[[Dict], None]):
        self._listeners.add(listener)

    def start(self):
        while not self._stop_event.is_set():
            boards = self.get_boards()

            for listener in self._listeners:
                listener(boards)

            self._stop_event.wait(self._interval_s)

    def stop(self):
        self._stop_event.set()

    def get_boards(self):
        channel_mapping = self._channel_mapping_service.get_channel_mapping()
        boards = {}

        for key, value in channel_mapping.items():
            if not (value['board_id'] and value['message_id']):
                continue

            board_id = value['board_id']
            board = self._restya_service.get_board(board_id)

            board.pop('activities', '')
            board.pop('acl_links', '')
            board.pop('board_user_roles', '')
            board.pop('organization_users', '')

            boards[str(board_id)] = board

        return boards
