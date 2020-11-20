
import os
from dotenv import load_dotenv

from discord.ext import commands

from cogs.restya_cog import RestyaCog

from services.restya_service import RestyaService
from services.channel_mapping_service import ChannelMappingService


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESTYA_TOKEN = os.getenv('RESTYA_TOKEN')

restya_service = RestyaService(os.getenv('RESTYA_URL'), RESTYA_TOKEN)
channel_mapping = ChannelMappingService('channel_mapping.json')


cog_parameters = {
    'orga_id': int(os.getenv('RESTYA_ORGA_ID')),
    'board_template': os.getenv('RESTYA_BOARD_TEMPLATE')
}

bot = commands.Bot(command_prefix='!dragon.')

bot.add_cog(RestyaCog(bot, channel_mapping, restya_service, cog_parameters))


@bot.event
async def on_ready():
    if len(bot.guilds) != 1:
        raise ValueError('Not exactly one guild is registered for this bot!')

    print('Discord connected, ready for work :)')


bot.run(DISCORD_TOKEN, bot=True, reconnect=True)
