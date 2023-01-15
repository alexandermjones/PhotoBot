"""
Class for PhotoBot, which handles photo retrieving and sending from Discord.
"""

# Standard library imports.
import json
from pathlib import Path
from typing import Any

# Third party imports.
from discord.ext import commands



class PhotoBot(commands.Bot):
    """
    Class for a Photo Discord Bot.
    
    Inherits from a Discord bot with commands for handling photo and video upload.

    Non-inherited public attributes:
        
    """
    def __init__(self,
                 command_prefix: str='!'):
        """
        Initialises the Queue_Bot.
        Args:
            command_prefix (str, default='!'): The character which identifies a message as a command.
        """
        super().__init__(command_prefix=command_prefix,
                         intents=Intents.default(),
                         help_command=commands.DefaultHelpCommand(no_category='Commands'))
        self.command_prefix = command_prefix
        # Create a db directory if one doesn't exist already
        self.__game_dict_fpath.parent.mkdir(exist_ok=True)
        # Create a game dictionary if one isn't present already
        if not self.__game_dict_fpath.exists():
            with open(self.__game_dict_fpath, 'w') as f:
                json.dump({}, f)
        with open(self.__game_dict_fpath) as f:
            self.game_dict = json.load(f)
        self.add_events()


    """
    Private class methods to support events.
    """


    
    """
    Behaviour for events happening to the bot.
    """
    def add_events(self) -> None:
        """
        Add new events to the bot.
        """
        @ self.event
        async def on_message(self, message):
            """
            Overwrite default class behaviour for when a message is sent.
            """
            # Ignore if the Bot is the messager, so we don't enter into a recursive loop
            if message.author == self.user:
                return

            # Get the attachments
            url = message.attachments[0].url

            if not url:
                pass

            else:
                message.channel.send(f'Url sent was: {url}')


        @self.event
        async def on_command_error(ctx: commands.Context, error: Any) -> str:
            """
            Error handling for errors with a command.

            Args:
                ctx (commands.Context): The context of the command.
                error (Any): A commands error.
            Returns:
                str: The response message to post in the Discord channel the error was received in.
            """
            if isinstance(error, commands.CommandNotFound):
                await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
            if isinstance(error, commands.MissingRequiredArgument):
                await ctx.send('**Please pass in all requirements to use the command. Try using** `help`**!**')
            if isinstance(error, commands.MissingPermissions):
                await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")
            if isinstance(error, commands.errors.CommandInvokeError):
                await ctx.send("**There was a connection error somewhere, why don't you try again now?**")


        @self.event
        async def on_ready(self) -> None:
            """
            Message to print in the terminal when the bot is created to confirm its ready.
            """
            print(f"Bot created as: {self.user.name}")


        # on_message = client.event(on_message)