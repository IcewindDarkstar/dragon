
import os
from dotenv import load_dotenv

from discord.ext import commands

from restya_service import RestyaService


load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
RESTYA_TOKEN = os.getenv('RESTYA_TOKEN')


restya_service = RestyaService(os.getenv('RESTYA_URL'), RESTYA_TOKEN)
bot = commands.Bot(command_prefix='!dragon.')

channel_board_dict = {
    'restya-1': {
        'channel_name': 'restya-1'
    }
}


@bot.command(name='list', help='Lists the contents of the associated restya board.')
async def list_board(ctx):
    await ctx.send("Sorry this is not implemented right now")


@bot.event
async def on_ready():
    if len(bot.guilds) != 1:
        raise ValueError('Not exactly one guild is registered for this bot!')

    for role in bot.guilds[0].roles:
        print(role, role.id)
    #TODO: find channels
    print('Discord connected...')


print('Mapping boards')

nr_of_boards = 0
boards = restya_service.get_boards()
for board in boards:
    board_entry = channel_board_dict.get(board['name'], None)
    if board_entry is not None:
        nr_of_boards = nr_of_boards + 1
        board_entry['board_id'] = board['id']
        board_entry['restya_board'] = board

print(f"Mapped {nr_of_boards} board(s)!")

bot.run(DISCORD_TOKEN)
