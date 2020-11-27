import os
import threading

from dotenv import load_dotenv

from discord.ext import commands

from cogs.restya_cog import RestyaCog

from services.activity_notification_service import ActivityNotificationService
from services.restya_service import RestyaService
from services.channel_mapping_service import ChannelMappingService


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESTYA_TOKEN = os.getenv('RESTYA_TOKEN')

restya_service = RestyaService(os.getenv('RESTYA_URL'), RESTYA_TOKEN)
channel_mapping = ChannelMappingService('channel_mapping.json')


cog_parameters = {
    'orga_id': int(os.getenv('RESTYA_ORGA_ID')),
    'board_template': os.getenv('RESTYA_BOARD_TEMPLATE'),
    'default_list': os.getenv('RESTYA_BOARD_TEMPLATE').split(',')[0]
}

bot = commands.Bot(command_prefix='!dragon.')

bot.add_cog(RestyaCog(bot, channel_mapping, restya_service, cog_parameters))


def notify_new_activities(activities):
    print(len(activities))


activity_notification_service = ActivityNotificationService(restya_service)
activity_notification_service.add_activity_notification_listener(notify_new_activities)


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
