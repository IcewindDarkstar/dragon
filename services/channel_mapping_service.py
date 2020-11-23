
import json


class ChannelMappingService:

    def __init__(self, mapping_file_name: str):
        self.__mapping_file_name = mapping_file_name
        with open(mapping_file_name) as fp:
            # we have to convert the string keys to integers to have the proper typing later on
            self.__data = json.load(fp)
            self.__channel_mapping = {int(entry["channel_id"]): entry for entry in self.__data}
            self.__board_mapping = {int(entry["board_id"]): entry for entry in self.__data}
            self.__notification_channels = set()
            for entry in self.__data:
                self.__notification_channels.update(entry["notification_channels"])
            self.__notified_boards = {int(entry["board_id"]) for entry in self.__data if len(entry["notification_channels"]) > 0}

    def __write_mapping_to_file(self):
        with open(self.__mapping_file_name, 'w') as fp:
            json.dump(self.__data, fp)

    def has_channel_board(self, channel_id: int):
        return channel_id in self.__channel_mapping

    def has_board_channel(self, board_id):
        return board_id in self.__board_mapping

    def add_board_mapping(self, channel_id: int, board_id: int):
        self.__data.add({'channel_id': channel_id, 'board_id': board_id, 'notification_channels': []})
        self.__board_mapping[board_id] = channel_id
        self.__channel_mapping[channel_id] = board_id
        self.__write_mapping_to_file()

    def get_board_id(self, channel_id):
        return self.__channel_mapping.get(channel_id, {}).get('board_id', None)

    def has_board_notification(self, board_id: int):
        return board_id in self.__notified_boards

    def has_channel_notification(self, channel_id: int):
        return channel_id in self.__notification_channels

    def add_notification_mapping(self, channel_id: int, board_id: int):
        self.__board_mapping[board_id]['notification_channels'].append(channel_id)
        self.__notification_channels.add(channel_id)
        self.__notified_boards.add(board_id)
        self.__write_mapping_to_file()

    def get_notification_channels(self, board_id: int):
        return self.__board_mapping[board_id]['notification_channels']
