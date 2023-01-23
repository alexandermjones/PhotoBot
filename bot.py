'''
Class for PhotoBot, which handles photo retrieving and sending from Discord.
'''

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
    '''
    Class for a Photo Discord Bot.
    
    Inherits from a Discord bot with additional events.

    The main functionality of the Bot is that it sends the URLs of images uploaded in the channel to self.db_url.

    Non-inherited public attributes:
        db_url (str): The URL to the database where URLs of photos are stored.
        image_suffixes (list): The suffixes for attachments which are sent to the database.
    
    Non-inherited public methods:
        handle_image: Send a URL of an image to self.db_url.
        add_events: Add the new events to the bot.
    '''
    def __init__(self,
                 db_url: str,
                 command_prefix: str='!'):
        '''
        Initialises the Queue_Bot.

        Args:
            db_url (str): The URL to the database where photos are stored.
            command_prefix (str, default='!'): The character which identifies a message as a command.
        '''
        super().__init__(command_prefix=command_prefix,
                         intents=INTENTS,
                         help_command=commands.DefaultHelpCommand(no_category='Commands'))
        self.db_url = db_url
        self.command_prefix = command_prefix
        self.image_suffixes = ['.jpg', '.jpeg', '.webp', '.png']
        self.add_events()

    
    def handle_image(self, image_url: str) -> None:
        '''
        Send a URL of an image to self.db_url.

        Args:
            image_url (str): The URL of the image to send to self.db_url.
        '''
        r = requests.post(url=self.photo_url, data=image_url)
        print(r)


    '''
    Behaviour for events happening to the bot.
    '''
    async def __on_message(self, message) -> None:
        '''
        Handle functionality for when a message is posted in a channel.

        Sends all image attachments to self.handle_image.

        Args:
            message: A Discord message event.
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


    async def __on_command_error(self, ctx: commands.Context, error: Any) -> None:
        '''
        Handle functionality for when an error occurs - sends a relevant message to the channel.

        Args:
            ctx (commands.Context): The context of the command.
            error (Any): A commands error.
        '''
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('**Invalid command. Try using** `help` **to figure out commands!**')
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements to use the command. Try using** `help`**!**')
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('**You dont have all the requirements or permissions for using this command :angry:**')
        if isinstance(error, commands.errors.CommandInvokeError):
            await ctx.send('**There was a connection error somewhere, why don\'t you try again now?**')


    async def __on_ready(self) -> None:
        '''
        Print message to confirm the PhotoBot has been succesfully created.
        '''
        print(f'PhotoBot created as: {self.user.name}.')


    def add_events(self) -> None:
        '''
        Add the new events to the bot.
        '''
        self.__on_message = self.event(self.__on_message)
        self.__on_command_error = self.event(self.__on_command_error)
        self.__on_ready = self.event(self.__on_ready)
