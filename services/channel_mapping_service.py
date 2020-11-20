
import json


class ChannelMappingService:

    def __init__(self, mapping_file_name: str):
        self.__mapping_file_name = mapping_file_name
        with open(mapping_file_name) as fp:
            # we have to convert the string keys to integers to have the proper typing later on
            self._channel_mapping = {int(channel_id): int(board_id) for channel_id, board_id in json.load(fp).items()}

    def __write_mapping_to_file(self):
        with open(self.__mapping_file_name, 'w') as fp:
            json.dump(self._channel_mapping, fp)

    def contains(self, channel_id: int):
        return channel_id in self._channel_mapping

    def add_mapping(self, channel_id: int, board_id):
        self._channel_mapping[channel_id] = board_id
        self.__write_mapping_to_file()

    def get_board_id(self, channel_id):
        return self._channel_mapping.get(channel_id, None)
