import os
import threading

from dotenv import load_dotenv

from discord.ext import commands

from cogs.restya_cog import RestyaCog

from services.activity_notification_service import ActivityNotificationService
from services.channel_mapping_service import ChannelMappingService
from services.discord_notification_service import DiscordNotificationService
from services.restya_service import RestyaService


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESTYA_TOKEN = os.getenv('RESTYA_TOKEN')

cog_parameters = {
    'orga_id': int(os.getenv('RESTYA_ORGA_ID')),
    'board_template': os.getenv('RESTYA_BOARD_TEMPLATE'),
    'default_list': os.getenv('RESTYA_BOARD_TEMPLATE').split(',')[0]
}


restya_service = RestyaService(os.getenv('RESTYA_URL'), RESTYA_TOKEN)
channel_mapping = ChannelMappingService('channel_mapping.json')

bot = commands.Bot(command_prefix='!dragon.')
bot.add_cog(RestyaCog(bot, channel_mapping, restya_service, cog_parameters))

discord_notify_service = DiscordNotificationService(bot, channel_mapping)

activity_notification_service = ActivityNotificationService(restya_service, 10)
activity_notification_service.add_activity_notification_listener(discord_notify_service.notify_restya_activity)


@bot.event
async def on_ready():
    if len(bot.guilds) != 1:
        raise ValueError('Not exactly one guild is registered for this bot!')

    print('Discord connected, ready for work :)')


if __name__ == '__main__':
    activity_thread = threading.Thread(target=activity_notification_service.start)
    activity_thread.start()

    # this is a blocking call that is terminated by ctrl-c
    bot.run(DISCORD_TOKEN, bot=True, reconnect=True)

    print("Stopping activity service.")
    activity_notification_service.stop()
    activity_thread.join()
    print("Finished")
