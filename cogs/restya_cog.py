from threading import Lock
from typing import Dict

from discord.ext import commands

from services.channel_mapping_service import ChannelMappingService
from services.restya_service import RestyaService


class RestyaCog(commands.Cog):

    def __init__(self,
                 bot: commands.Bot,
                 channel_mapping_service: ChannelMappingService,
                 restya_service: RestyaService,
                 parameters: Dict
                 ):
        self.bot = bot
        self._restya_service = restya_service
        self._channel_mapping = channel_mapping_service
        self.__lock = Lock()
        self._parameters = parameters

    @commands.command(name='list', help='Lists the contents of the associated restya board.')
    @commands.guild_only()
    async def list_board(self, ctx):
        board_id = self._channel_mapping.get_board_id(ctx.channel.id)
        if board_id is None:
            await ctx.send(
                "There is no board for this channel, an admin create one by calling the create_board command!")
        else:
            board = self._restya_service.get_board(board_id)
            ctx.typing()
            output = [f"Board ***{board['name']}*** contains:"]
            for board_list in board['lists']:
                output.append(f"**{board_list['name']}:**")
                if board_list['cards'] is not None:
                    for card in board_list['cards']:
                        output.append(
                            f"\t• [{card['id']}] {card['name']} - {card['description'] if card['description'] is not None else ''}")

            await ctx.send('\n'.join(output))

    @commands.command(name='create_board', help='Creates a new restya board with the name of the current channel and links them.')
    @commands.guild_only()
    async def create_board(self, ctx: commands.Context):
        if ctx.author.guild_permissions.administrator:
            channel_name = ctx.channel.name
            channel_id = ctx.channel.id

            with self.__lock:
                if self._channel_mapping.contains(channel_id):
                    await ctx.send('There is already a board for this channel!')
                else:
                    board = self._restya_service.create_board(channel_name, self._parameters['orga_id'], self._parameters['board_template'])
                    if board is None:
                        await ctx.send('There was a problem creating the board!')
                    else:
                        board_id = board['id']
                        self._channel_mapping.add_mapping(channel_id, board_id)
                        await ctx.send(f"Created a new board for this channel with the name {channel_name}.")
        else:
            await ctx.send(f"I can't let you do that {ctx.author.name}!")

