import os
import threading
import logging

from discord.ext import commands

from cogs.restya_cog import RestyaCog

from services.activity_notification_service import ActivityNotificationService
from services.channel_mapping_service import ChannelMappingService
from services.discord_notification_service import DiscordNotificationService
from services.restya_service import RestyaService

from services.restya_board_aggregator import RestyaBoardAggregator
from services.discord_message_service import DiscordMessageService

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESTYA_TOKEN = os.getenv('RESTYA_TOKEN')

logging.basicConfig(level=logging.INFO)

channel_mapping = ChannelMappingService('/data/channel_mapping.json')
restya_service = RestyaService(os.getenv('RESTYA_URL'), RESTYA_TOKEN)


cog_parameters = {
    'orga_id': int(os.getenv('RESTYA_ORGA_ID')),
    'board_template': os.getenv('RESTYA_BOARD_TEMPLATE'),
    'default_list': os.getenv('RESTYA_BOARD_TEMPLATE').split(',')[0]
}


bot = commands.Bot(command_prefix='!dragon.')
bot.add_cog(RestyaCog(bot, channel_mapping, restya_service, cog_parameters))

discord_notify_service = DiscordNotificationService(bot, channel_mapping)

activity_notification_service = ActivityNotificationService(restya_service, 60 * 10)  # notify of board activity every 10 minutes
activity_notification_service.add_activity_notification_listener(discord_notify_service.notify_restya_activity)

discord_message_service = DiscordMessageService(bot, channel_mapping)
restya_board_aggregator = RestyaBoardAggregator(restya_service, channel_mapping, 60 * 60 * 24)  # refresh board message every 24 hours
restya_board_aggregator.add_listener(discord_message_service.refresh_messages)

@bot.event
async def on_ready():
    if len(bot.guilds) != 1:
        raise ValueError('Not exactly one guild is registered for this bot!')

    logging.info('Discord connected, ready for work :)')


if __name__ == '__main__':
    activity_thread = threading.Thread(target=activity_notification_service.start)
    activity_thread.start()

    restya_board_thread = threading.Thread(target=restya_board_aggregator.start)
    restya_board_thread.start()

    # this is a blocking call that is terminated by ctrl-c
    bot.run(DISCORD_TOKEN, bot=True, reconnect=True)

    logging.info("Stopping activity service.")
    activity_notification_service.stop()
    activity_thread.join()

    restya_board_aggregator.stop()
    restya_board_thread.join()
    logging.info("Finished")
