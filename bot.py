'''
Class for PhotoBot, which handles photo retrieving and sending from Discord.
'''

# Standard library imports.
import json
import logging
import requests
from pathlib import Path
from typing import Any

# Third party imports.
import discord
from discord.ext import commands

# Add the message_content intent to manage Attachments
INTENTS = discord.Intents.default()
INTENTS.message_content = True

# Set the logging level and write to file
logging.basicConfig(filename='bot.log',
                    filemode='w',
                    format='%(levelname)s - %(asctime)s - %(message)s', 
                    level=logging.INFO)


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
        self.photo_url = db_url.replace('SUBDOMAIN', 'photo')
        self.album_url = db_url.replace('SUBDOMAIN', 'album')
        self.command_prefix = command_prefix
        self.image_suffixes = ['.jpg', '.jpeg', '.webp', '.png']
        self.channels_path = Path('channels.json')
        if not self.channels_path.is_file():
            self.channels = {}
        else:
            with open(self.channels_path, 'r') as f:
                self.channels = json.loads(f)
        self.add_events()
        self.add_commands()

    
    def handle_image(self, image_url: str, channel_id: str) -> bool:
        '''
        Post a URL of an image and channel_id the image was sent in to self.db_url.

        Args:
            image_url (str): The URL of the image to post to self.db_url.
            channel_id (str): The ID of the channel the image was sent in.

        Returns:
            bool: True if succesfully posted, False if not.
        '''
        post_data = {'url': image_url, 'channelId': channel_id}
        r = requests.post(url=self.photo_url, data=post_data)
        if r.status_code == 200:
            logging.info(f'Image URL of {image_url} succesfully posted to database.')
            return True
        else:
            logging.error(f'Error uploading image URL: {image_url}. The server responded: {r.reason} with status code {r.status_code}.')
            return False
        

    def update_channel_name(self, channel_id: str, album_name: str) -> bool:
        '''
        Send an updated album name for the given channel_id.

        Args:
            channel_id (str): The ID of the channel the image was sent in.
            album_name (str): The album name to POST.

        Returns:
            bool: True if succesfully posted, False if not.
        '''
        post_data = {'channelId': channel_id, 'name': album_name}
        r = requests.post(url=self.album_url, data=post_data)
        if r.status_code == 200:
            logging.info(f'Successfully updated {channel_id} with album name: {album_name}.')
            return True
        else:
            logging.error(f'Error updating {channel_id} name. The server responded: {r.reason} with status code {r.status_code}.')
            return False
    

    def update_channel(self, channel_id: str, capture: bool) -> None:
        '''
        Update self.channels and the file at self.channels_path to add or remove it from the channels to post in.

        Args:
            channel_id (str): The channel ID to update.
            capture (bool): Whether to capture the channel or not.
        '''
        self.channels[channel_id] = capture
        with open(self.channels_path, 'w') as f:
            json.dump(self.channels, f)
        logging.info(f'Channel ID: {channel_id} now has capture status: {bool}.')
        return


    '''
    Behaviour for events happening to the bot.
    '''
    async def on_message(self, message: discord.Message) -> None:
        '''
        Handle functionality for when a message is posted in a channel.

        Sends all image attachments to self.handle_image and then reacts to the message with a camera emoji.

        Args:
            message: A Discord message event.
        '''
        # Ignore if the Bot is the messager, so we don't enter into a recursive loop
        if message.author == self.user:
            return

        channel_id = message.channel.id
        # Exit if we aren't capturing in this channel
        if not self.channels.get(channel_id, False):
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
        successes = []
        for image_url in image_urls:
            successes.append(self.handle_image(image_url, channel_id))
        
        # React to the message if it contained an image with a camera with flash emoji
        if any(successes):
            await message.add_reaction('📸')


    async def on_command_error(self, ctx: commands.Context, error: Any) -> None:
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


    async def on_ready(self) -> None:
        '''
        Print message to confirm the PhotoBot has been succesfully created.
        '''
        print(f'PhotoBot created as: {self.user.name}.')


    def add_events(self) -> None:
        '''
        Add the new events to the bot.
        '''
        self.on_message = self.event(self.on_message)
        self.on_command_error = self.event(self.on_command_error)
        self.on_ready = self.event(self.on_ready)
    

    '''
    Commands for the bot.
    '''
    @commands.hybrid_command(name='album',
                             description='Name the album for photos in the channel.')
    async def name_album(self, ctx: commands.Context, album_name: str) -> None:
        '''
        Command to name the album for a given channel, starts an album if not currently in the channel.

        Args:
            ctx (commands.Context): The context of the command.
            album_name (str): The name of the album.
        '''
        channel_id = ctx.channel.id
        album_name = album_name.title()
        success = self.update_channel_name(channel_id, album_name)
        if success:
            ctx.message.add_reaction('👌')
    

    @commands.hybrid_command(name='capture',
                             description='Capture photos uploaded in the channel.')
    async def capture_album(self, ctx: commands.Context):
        '''
        Command to tell the bot to capture photos uploaded in the channel.

        Args:
            ctx (commands.Context): The context of the command.
        '''
        channel_id = ctx.channel.id
        self.update_channel(channel_id, True)
        ctx.message.add_reaction('👍')
    

    @commands.hybrid_command(name='stop',
                              description='Stop capturing photos uploaded in the channel.')
    async def stop_capture_album(self, ctx: commands.Context):
        '''
        Command to tell the bot to stop capturing photos uploaded in the channel.

        Args:
            ctx (commands.Context): The context of the command.
        '''
        channel_id = ctx.channel.id
        self.update_channel(channel_id, False)
        ctx.message.add_reaction('👍')
    

    async def add_commands(self) -> None:
        self.add_command(self.name_album)
        self.add_command(self.capture_album)
        self.add_command(self.stop_capture_album)
        await self.tree.sync()
