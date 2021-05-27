import asyncio
import logging

from discord.ext import commands

from services.channel_mapping_service import ChannelMappingService


class DiscordMessageService:

    def __init__(self, discord_bot: commands.Bot, channel_mapping_service: ChannelMappingService):
        self._discord_bot = discord_bot
        self._channel_mapping_service = channel_mapping_service

    def refresh_messages(self, boards: dict):
        channel_mapping = self._channel_mapping_service.get_channel_mapping()
        refresh_future = asyncio.run_coroutine_threadsafe(self.refresh_messages_for_channels(boards, channel_mapping), self._discord_bot.loop)
        refresh_future.result()
        logging.info('DiscordMessageService.refresh_messages: Refreshed all board messages')

    async def refresh_messages_for_channels(self, boards: dict, channel_mapping: dict):
        for key, value in channel_mapping.items():
            if not (value['board_id'] and value['message_id']):
                logging.info('DiscordMessageService.refresh_messages_for_channels: '
                    + 'could not find board_id or message_id for channel ' + str(key))
                continue

            await self.refresh_message(key, value['message_id'], boards[str(value['board_id'])])

    async def refresh_message(self, channel_id: int, message_id: int, board: dict):
        channel = self._discord_bot.get_channel(channel_id)

        if channel is None:
            # Directly after startup Bot.get_channel() returns None, so the call is repeated once after a few seconds
            await asyncio.sleep(5)
            channel = self._discord_bot.get_channel(channel_id)

            if channel is None:
                logging.info('DiscordMessageService.refresh_message: Channel is none for channel_id ' + str(channel_id))
                return

        message = await channel.fetch_message(message_id)

        if message is None:
            logging.info('DiscordMessageService.refresh_message: Message is none for message_id ' + str(message_id))
            return

        new_content = self.create_board_message(board)
        logging.info('DiscordMessageService.refresh_message: New content will be ' + str(new_content))
        await message.edit(content=str('\n'.join(new_content)))

    def create_board_message(self, board: dict):
        board_url = f"https://restya.indes.ninja/#/board/{board['id']}"
        message = [f"Board **[{board['id']}] {board['name']}** contains ({board_url}):"]

        for board_list in board['lists']:
            if board_list['is_archived']:
                continue

            message.append(f"\n**{board_list['name']}**:")

            if board_list['cards'] is None:
                continue

            for board_card in board_list['cards']:
                if board_card['is_archived']:
                    continue

                message.append(f"\t• [{board_card['id']}] {board_card['name']}")

        return message
