
import os
from threading import Lock
from dotenv import load_dotenv

from discord.ext import commands

from restya_service import RestyaService
from channel_mapping_service import ChannelMappingService


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESTYA_TOKEN = os.getenv('RESTYA_TOKEN')

restya_service = RestyaService(os.getenv('RESTYA_URL'), RESTYA_TOKEN)
channel_mapping = ChannelMappingService('channel_mapping.json')

orga_id = int(os.getenv('RESTYA_ORGA_ID'))
board_template = os.getenv('RESTYA_BOARD_TEMPLATE')


bot = commands.Bot(command_prefix='!dragon.')
lock = Lock()


@bot.command(name='list', help='Lists the contents of the associated restya board.')
async def list_board(ctx):
    board_id = channel_mapping.get_board_id(ctx.channel.id)
    if board_id is None:
        await ctx.send("There is no board for this channel, an admin create one by calling the create_board command!")
    else:
        board = restya_service.get_board(board_id)
        ctx.typing()
        output = [f"Board ***{board['name']}*** contains:"]
        for board_list in board['lists']:
            output.append(f"**{board_list['name']}:**")
            if board_list['cards'] is not None:
                for card in board_list['cards']:
                    output.append(f"\t• [{card['id']}] {card['name']} - {card['description'] if card['description'] is not None else ''}")

        await ctx.send('\n'.join(output))


@bot.command(name='create_board', help='Creates a new restya board with the name of the current channel and links them.')
async def create_board(ctx: commands.Context):
    if ctx.author.guild_permissions.administrator:
        channel_name = ctx.channel.name
        channel_id = ctx.channel.id

        with lock:
            if channel_mapping.contains(channel_id):
                await ctx.send('There is already a board for this channel!')
            else:
                board = restya_service.create_board(channel_name, orga_id, board_template)
                if board is None:
                    await ctx.send('There was a problem creating the board!')
                else:
                    board_id = board['id']
                    channel_mapping.add_mapping(channel_id, board_id)
                    await ctx.send(f"Created a new board for this channel with the name {channel_name}.")
    else:
        await ctx.send(f"I can't let you do that {ctx.author.name}!")


@bot.event
async def on_ready():
    if len(bot.guilds) != 1:
        raise ValueError('Not exactly one guild is registered for this bot!')

    print('Discord connected, ready for work :)')


bot.run(DISCORD_TOKEN)
