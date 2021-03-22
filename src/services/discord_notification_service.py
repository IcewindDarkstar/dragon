from typing import List

from discord.ext import commands

from services.channel_mapping_service import ChannelMappingService


class DiscordNotificationService:

    STRING_REPLACEMENTS = {
        'USER_NAME': 'full_name',
        'CARD_LINK': 'card_id'
    }

    def __init__(self, discord_bot: commands.Bot, channel_mapping: ChannelMappingService):
        self.__channel_mapping = channel_mapping
        self.__discord_bot = discord_bot

    def notify_restya_activity(self, activities: List):
        for activity in activities:
            full_comment = self._create_full_comment(activity)

            if self.__channel_mapping.has_board_notification(activity['board_id']):
                notification_channel_ids = self.__channel_mapping.get_notification_channels(activity['board_id'])
                for channel_id in notification_channel_ids:
                    channel = self.__discord_bot.get_channel(channel_id)
                    if channel is None:
                        print(f"Could not find linked channel with id {channel_id}?!")
                    else:
                        self.__discord_bot.loop.create_task(channel.send(full_comment))

    def _create_full_comment(self, activity):
        comment = activity['comment']
        for key, value_key in DiscordNotificationService.STRING_REPLACEMENTS.items():
            comment = comment.replace(f"##{key}##", str(activity[value_key]))
        return comment
