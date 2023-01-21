"""
Class for PhotoBot, which handles photo retrieving and sending from Discord.
"""

# Standard library imports.
import requests
from pathlib import Path
from typing import Any

# Third party imports.
from discord import Intents
from discord.ext import commands

# Add the message_content intent to manage Attachments
INTENTS = Intents.default()
INTENTS.message_content = True


class PhotoBot(commands.Bot):
    """
    Class for a Photo Discord Bot.
    
    Inherits from a Discord bot with commands for handling photo and video upload.

    Non-inherited public attributes:
        
    """
    def __init__(self,
                 photo_url: str,
                 command_prefix: str='!'):
        """
        Initialises the Queue_Bot.
        Args:
            command_prefix (str, default='!'): The character which identifies a message as a command.
        """
        super().__init__(command_prefix=command_prefix,
                         intents=INTENTS,
                         help_command=commands.DefaultHelpCommand(no_category='Commands'))
        self.photo_url = photo_url
        self.command_prefix = command_prefix
        self.image_suffixes = ['.jpg', '.jpeg', '.webp', '.png', '.gif']
        self.add_events()

    
    def handle_image(self, image_url):
        '''
        Handle an image URL.
        '''
        r = requests.post(url=self.photo_url, data=image_url)
        print(r)


    '''
    Behaviour for events happening to the bot.
    '''
    async def on_message(self, message):
        '''
        Get all the URLs for images sent in the channel and send these to self.handle_image().
        '''
        # Ignore if the Bot is the messager, so we don't enter into a recursive loop
        if message.author == self.user:
            return

        # Exit if the message didn't contain an attachment
        if not message.attachments:
            return

        # Get all image urls in the message
        image_urls = []
        for attachment in message.attachments:
            if Path(attachment.filename).suffix.lower() in self.image_suffixes:
                image_urls.append(attachment.url)
    
        # Handle these URLs
        for image_url in image_urls:
            self.handle_image(image_url)


    async def on_command_error(self, ctx: commands.Context, error: Any) -> str:
        '''
        Error handling for errors with a command.

        Args:
            ctx (commands.Context): The context of the command.
            error (Any): A commands error.
        Returns:
            str: The response message to post in the Discord channel the error was received in.
        '''
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("**Invalid command. Try using** `help` **to figure out commands!**")
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements to use the command. Try using** `help`**!**')
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("**You dont have all the requirements or permissions for using this command :angry:**")
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send("**There was a connection error somewhere, why don't you try again now?**")


    async def on_ready(self) -> None:
        '''
        Message to print in the terminal when the bot is created to confirm its ready.
        '''
        print(f'Bot created as: {self.user.name}.')


    def add_events(self) -> None:
        '''
        Add the new events to the bot.
        '''
        self.on_message = self.event(self.on_message)
        self.on_command_error = self.event(self.on_command_error)
        self.on_ready = self.event(self.on_ready)
