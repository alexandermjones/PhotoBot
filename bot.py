'''
Class for PhotoBot, which handles photo retrieving and sending from Discord.
'''

# Standard library imports.
import json
import logging
import requests
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

# Third party imports.
import discord
from discord.ext import commands

# Add the message_content intent to manage Attachments
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
INTENTS.reactions = True

# Set the logging level and write to file
logging.basicConfig(filename='bot.log',
                    format='%(levelname)s - %(asctime)s - %(message)s', 
                    level=logging.INFO)


class PhotoBot(commands.Bot):
    '''
    Class for a Photo Discord Bot.
    
    Inherits from a Discord bot with additional events.

    The main functionality of the Bot is that it sends the URLs of images uploaded in the channel to self.photo_url.

    Non-inherited public attributes:
        photo_url (str): The URL to the database where URLs of photos are stored.
        album_url (str): The URL to the database where album names are stored.
        image_suffixes (list): The suffixes for attachments which are sent to the database.
        channels_path (pathlib.Path): The filepath at which channels to save attachments from are stored.
        channels (dict): The dictionary of channel IDs and whether to save attachements from them or not.
    
    Non-inherited public methods:
        handle_image: Send a URL of an image to self.db_url.
        update_channel_name: Post a URL of an image and channel_id the image was sent in to self.db_url.
        update_channel: Update self.channels and the file at self.channels_path to add or remove it from the channels to post in.
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
        self.photo_url = db_url + 'photo'
        self.album_url = db_url + 'album'
        self.delete_photo_url = db_url + 'delete_photo_by_url'
        self.image_suffixes = ['.jpg', '.jpeg', '.webp', '.png']
        self.channels_path = Path('channels.json')
        if not self.channels_path.is_file():
            self.channels = {}
        else:
            with open(self.channels_path, 'r') as f:
                self.channels = json.load(f)
        self.add_events()
        logging.info('PhotoBot initialised.')

    
    def handle_image(self, 
                     image_url: str, 
                     channel_id: str, 
                     uploader_id: str, 
                     upload_time: str, 
                     caption: str,
                     message_id: str) -> bool:
        '''
        Post a URL of an image and channel_id the image was sent in to self.db_url.

        Args:
            image_url (str): The URL of the image to post to self.db_url.
            channel_id (str): The ID of the channel the image was sent in.
            uploader_id (str): The ID of the uploader.
            upload_time (str): The original time of the upload message (ISO 8601 format).
            caption (str): The text written along with the upload message (first 100 chars).
            message_id (str): The ID of the message.

        Returns:
            bool: True if succesfully posted, False if not.
        '''
        post_data = json.dumps({'url': image_url, 'channelId': channel_id, 'uploaderId': uploader_id, 'uploadTime': upload_time, 'caption': caption, 'messageId': message_id })
        r = requests.post(url=self.photo_url, data=post_data)
        if r.status_code == 200:
            logging.info(f'Image URL of {image_url} succesfully posted to database.')
            return True
        else:
            logging.error(f'Error uploading image URL: {image_url}. The server responded: {r.reason} with status code {r.status_code}.')
            return False


    def update_channel(self, channel_id: str, album_name: str, members: list) -> str:
        '''
        Send an updated album name and members list for the given channel_id.

        Args:
            channel_id (str): The ID of the channel the image was sent in.
            album_name (str): The album name to POST.
            members (list): List of users ID present in the discord channel.

        Returns:
            bool: True if succesfully posted, False if not.
        '''
        post_data = json.dumps({'channelId': channel_id, 'name': album_name, 'members': members })
        r = requests.post(url=self.album_url, data=post_data)
        
        if r.status_code == 200:
            logging.info(f'Successfully updated: {channel_id} with album name: {album_name}.')
            return r.json().get('albumUrl')
        else:
            logging.error(f'Error updating {channel_id} name. The server responded: {r.reason} with status code {r.status_code}.')
            return None


    def update_capture(self, channel_id: str, capture: bool) -> None:
        '''
        Update self.channels and the file at self.channels_path to add or remove it from the channels to post in.

        Args:
            channel_id (str): The channel ID to update.
            capture (bool): Whether to capture the channel or not.
        '''
        self.channels[channel_id] = capture
        with open(self.channels_path, 'w') as f:
            json.dump(self.channels, f)
        logging.info(f'Channel ID: {channel_id} now has capture status: {capture}.')
        return
    

    def delete_photo(self, image_url: str, requester_id: str) -> int:
        '''
        Send a request to delete a photo from the db.

        Args:
            image_url (str): The URL of the photo to remove from the DB.
            requester_id (str): The ID of the requester sending the deletion.
        
        Returns:
            int: The response code of the server for the request.
        '''
        post_data = json.dumps({'photoId': image_url, 'requesterId': requester_id})
        r = requests.post(url=self.album_url, data=post_data)

        if r.status_code == 200:
            logging.info(f'Successfully deleted photo with URL: {image_url} from database.')
        else:
            logging.error(f'Error deleting photo with URL: {image_url}. The server responded: {r.reason} with status code {r.status_code}.')
        return r.status_code


    '''
    Behaviour for events happening to the bot.
    '''
    async def on_message(self, message: discord.Message) -> None:
        '''
        Handle functionality for when a message is posted in a channel.

        Sends all image attachments to self.handle_image and then reacts to the message with a camera emoji.

        Args:
            discrd.Message: A Discord message event.
        '''
        # Ignore if the Bot is the messager, so we don't enter into a recursive loop
        if message.author == self.user:
            return

        channel_id = str(message.channel.id)
        # Exit if we aren't capturing in this channel or the message didn't contain an attachment
        if not self.channels.get(channel_id, False) or not message.attachments:
            await self.process_commands(message)
            return

        # Get all image urls in the message
        image_urls = [urlparse(a.url).path for a in message.attachments if Path(urlparse(a.url).path).suffix.lower() in self.image_suffixes]

        uploader_id = str(message.author.id)
        upload_time = message.created_at.utcnow().replace(microsecond=0).isoformat() + 'Z' # format to match JS
        caption = message.content[:100]
        message_id = str(message.id);

        # Handle these URLs
        successes = [self.handle_image(image_url, channel_id, uploader_id, upload_time, caption, message_id) for image_url in image_urls]

        # React to the message if it contained an image with a camera with flash emoji
        if any(successes):
            await message.add_reaction('📸')
        
        # Process any commands along with the attachments
        await self.process_commands(message)
    

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent) -> None:
        '''
        Handle functionality for when a reaction is added to a message.

        Removes a photo from the database if an ❌ emoji is added.

        Args:
            discord.RawReactionActionEvent: The payload of the reaction event.
        '''
        # Ignore the bot's own reactions
        if payload.member == self.user:
            pass
        
        # Get the message the reaction was added to
        channel = self.get_partial_messageable(payload.channel_id)
        message = channel.fetch_message(payload.message_id)

        # Ignore reactions which the bot has not added 📸 (i.e. capture) to
        if not ('📸', True) in any([(r.emoji, r.me) for r in message.reactions]):
            pass

        # Delete photos from the database which have a '❌' added
        if payload.emoji == '❌':
            image_urls = [a.url for a in message.attachments if Path(a.url).suffix.lower() in self.image_suffixes]
            _ = [self.delete_photo(image_url, str(payload.user_id)) for image_url in image_urls]

        return


    async def on_command_error(self, ctx: commands.Context, error: Any) -> None:
        '''
        Handle functionality for when an error occurs - sends a relevant message to the channel.

        Args:
            ctx (commands.Context): The context of the command.
            error (Any): A commands error.
        '''
        if isinstance(error, commands.CommandNotFound):
            await ctx.send('**Invalid command. Try using** `help` **to figure out commands!**')
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('**Please pass in all requirements to use the command. Try using** `help`**!**')
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send('**You dont have all the requirements or permissions for using this command :angry:**')
        elif isinstance(error, commands.errors.CommandInvokeError):
            logging.warning('CommandInvokeError for command: {ctx.command}.')
            await ctx.send('**There was a connection error somewhere, why don\'t you try again now?**')
        else:
            logging.error(f'Unhandled error with: {ctx}. Raised: {error}.')


    async def on_ready(self) -> None:
        '''
        Print message to confirm the PhotoBot has been created.
        '''
        logging.info(f'PhotoBot running as: {self.user.name}.')


    def add_events(self) -> None:
        '''
        Add the new events to the bot.
        '''
        self.on_message = self.event(self.on_message)
        self.on_raw_reaction_add = self.event(self.on_raw_reaction_add)
        self.on_command_error = self.event(self.on_command_error)
        self.on_ready = self.event(self.on_ready)


    '''
    Commands for the bot. Added using a decorator in main.
    '''
    async def capture_album(self, ctx: commands.Context, album_name: str) -> None:
        '''
        Command to name the album for a given channel, starts an album if not currently in the channel.

        Args:
            ctx (commands.Context): The context of the command.
            album_name (str): The name of the album.
        '''
        channel_id = str(ctx.channel.id)
        is_new = not self.channels.get(channel_id, False)
        members = [str(member.id) for member in ctx.channel.members]
        members.remove(str(self.user.id))

        if is_new and not album_name:
            await ctx.send('Error capturing album. Please provide an album name when capturing a new channel.')
            return

        self.update_capture(channel_id, True)
        album_name = album_name.title()
        url = self.update_channel(channel_id, album_name, members)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for photos...'))

        if url:
            if is_new:
                await ctx.send(f'New album created: {album_name}. Photos uploaded to this channel will be captured 📷.')
            elif not album_name:
                await ctx.send(f'Users in channel updated. Photos uploaded to this channel will still be captured 📷.')
            else:
                await ctx.send(f'Album renamed to: {album_name}. Users in channel updated. Photos uploaded to this channel will still be captured 📷.')
                
            await ctx.send(f'Album is available at: {url}')
        else:
            await ctx.send('Error capturing album. Please check the logs for details.')


    async def stop_capture_album(self, ctx: commands.Context):
        '''
        Command to tell the bot to stop capturing photos uploaded in the channel.

        Args:
            ctx (commands.Context): The context of the command.
        '''
        channel_id = str(ctx.channel.id)
        self.update_capture(channel_id, False)
        await ctx.send('Photos no longer being captured in this channel.')


    async def sync_command_tree(self, ctx: commands.Context):
        '''
        Command to sync the command tree for the bot, to set commands as slash commands.

        Args:
            ctx (commands.Context): The context of the command.
        '''
        if await self.is_owner(ctx.author):
            await self.tree.sync()
            await ctx.send('Command tree synced 👌.')
        else:
            await ctx.send('Only the owner of the bot can use this command 😞.')



def add_commands_to_bot(bot: PhotoBot):
    '''
    Add commands to a PhotoBot object.

    Functions have to be tied to class instance, not class, due to decorators attached to object.

    Args:
        bot (PhotoBot): An instance of the PhotoBot class.
    '''
    @bot.hybrid_command(name='album',
                        description='Name the photo album for this channel ID.',
                        brief='Start cpaturing uploaded photos in this channel. Also rename the album. Update the users in album.')
    async def capture_album(ctx, *, album_name: str=""):
        await bot.capture_album(ctx, album_name)

    @bot.hybrid_command(name='stop',
                        description='Stop capturing uploaded photos in this channel.',
                        brief='Stop capturing uploaded photos in this channel.')
    async def stop_capture_album(ctx):
        await bot.stop_capture_album(ctx)

    @bot.command(name='sync_commands_photobot',
                 hidden=True)
    async def sync_command_tree(ctx):
        await bot.sync_command_tree(ctx)
    
    logging.info('Commands added to PhotoBot.')
