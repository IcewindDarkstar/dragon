from threading import Lock
from typing import Dict
import logging

from discord.ext import commands

from services.channel_mapping_service import ChannelMappingService
from services.restya_service import RestyaService
from services.discord_message_service import DiscordMessageService


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
            await self.print_board(ctx, board_id)

    @commands.command(name='create_board', help='Creates a new restya board with the name of the current channel and links them.')
    async def create_board(self, ctx: commands.Context, organization_id: int = None):
        channel_name = ctx.channel.name
        channel_id = ctx.channel.id

        orga_id = self._parameters['orga_id'] if organization_id is None else organization_id

        with self.__lock:
            if self._channel_mapping.has_channel_board(channel_id):
                await ctx.send('There is already a board for this channel!')
            else:
                board = self._restya_service.create_board(channel_name, orga_id, self._parameters['board_template'])
                if board is None:
                    await ctx.send('There was a problem creating the board!')
                else:
                    board_id = int(board['id'])
                    self._channel_mapping.add_board_mapping(channel_id, board_id)
                    await self.create_board_message(ctx)

    @commands.command(name='add_board_notify', help="Adds the current channel to the specified board's list of notification channels.")
    async def add_board_notify(self, ctx: commands.Context, board_id: int):
        channel_id = ctx.channel.id
        if self._channel_mapping.has_board_notification(board_id):
            await ctx.send("The given board already has a notification set!")
        elif self._channel_mapping.has_channel_notification(channel_id):
            await ctx.send("This channel already has a notification set, please remove it first with remove_board_notify!")
        else:
            self._channel_mapping.add_notification_mapping(channel_id, board_id)
            board = self._restya_service.get_board(board_id)
            await ctx.send(f"Set this channel as a notification for the board **{board['name']}** [**{board_id}**]!")

    @commands.command(name='remove_board_notify', help="Adds the current channel to the specified board's list of notification channels.")
    async def remove_board_notify(self, ctx: commands.Context):
        await ctx.send(f"Sorry not implemented!")
   
    @commands.command(name='add_ticket', help='Adds a new support request to the board associated with this channel in the first list.')
    @commands.guild_only()
    async def add_ticket(self, ctx: commands.Context, *, title: str):
        ctx.typing()
        with self.__lock:
            user_title = f"({ctx.author.display_name}) {title}"
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

    @commands.command(name='create_board_message', help='Creates and pins a new board message for this channel while deleting the old message.')
    async def create_board_message(self, ctx: commands.Context):
        board_id = self._channel_mapping.get_board_id(ctx.channel.id)

        if board_id is None:
            await ctx.send('There is no board for this channel, an admin can create one by calling the create_board command!')
            return

        old_message_id = self._channel_mapping.get_message_id(ctx.channel.id)
        old_message = None
        
        if old_message_id is not None:
            old_message = await ctx.fetch_message(old_message_id) 
            await old_message.unpin()
       
        new_message = await self.print_board(ctx, board_id)
        self._channel_mapping.set_message_mapping(ctx.channel.id, new_message.id)
        await new_message.pin()

        if old_message_id is not None:
            await old_message.delete()

    @commands.command(name='refresh_board', help='Refreshes the board message in this channel.')
    async def refresh_board(self, ctx: commands.Context):
        board_id = self._channel_mapping.get_board_id(ctx.channel.id)

        if board_id is None:
            await ctx.send('There is no board for this channel, an admin create one by calling the create_board command!')
            return

        board = self._restya_service.get_board(board_id)
        message_id = self._channel_mapping.get_message_id(ctx.channel.id)
        await DiscordMessageService(self.bot, self._channel_mapping).refresh_message(ctx.channel.id, message_id, board)
 
    async def print_board(self, ctx: commands.Context, board_id: int):
        board = self._restya_service.get_board(board_id)
        board_message = DiscordMessageService(self.bot, self._channel_mapping).create_board_message(board)
        ctx.typing()
        message = await ctx.send('\n'.join(board_message))
        return message
