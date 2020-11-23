from threading import Lock
from typing import Dict

from discord.ext import commands

from services.channel_mapping_service import ChannelMappingService
from services.restya_service import RestyaService


class RestyaCog(commands.Cog, name='Support'):

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
            await ctx.send('There is no board for this channel, an admin create one by calling the create_board command!')
        else:
            board = self._restya_service.get_board(board_id)
            ctx.typing()
            output = [f"Board ***{board['name']} [{board_id}]*** contains:"]
            for board_list in board['lists']:
                output.append(f"**{board_list['name']}:**")
                if board_list['cards'] is not None:
                    for card in board_list['cards']:
                        output.append(
                            f"\t• [{card['id']}] {card['name']} - {card['description'] if card['description'] is not None else ''}")

            await ctx.send('\n'.join(output))

    @commands.command(name='create_board', help='Creates a new restya board with the name of the current channel and links them.')
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
            await ctx.send(f"I can't let you do that {ctx.author.display_name}!")

    @commands.command(name='add_ticket', help='Adds a new support request to the board associated with this channel in the first list.')
    @commands.guild_only()
    async def add_ticket(self, ctx: commands.Context, *, title: str):
        ctx.typing()
        with self.__lock:
            user_title = f"{ctx.author.display_name}: {title}"
            board_id = self._channel_mapping.get_board_id(ctx.channel.id)
            if board_id is None:
                await ctx.send('There is no board for this channel, an admin create one by calling the create_board command!')
            else:
                card = self._restya_service.add_card(board_id, user_title, self._parameters['default_list'])
                await ctx.send(f"Your ticket with id {card['id']} was created, you can add a description with the set_description command.")

    @add_ticket.error
    async def add_ticket_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Could not find the required argument "title", please provide a title for your ticket!')
            await ctx.send_help(self.add_ticket)


