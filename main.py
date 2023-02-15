'''
Run the Discord bot.
'''
# Standard imports
from os import getenv

# Third party imports
from dotenv import load_dotenv

# Local imports
from bot import PhotoBot


if __name__ == '__main__':
    # Load in Discord token and db_url.
    load_dotenv()
    token = getenv('DISCORD_TOKEN')
    db_url = getenv('DB_ENDPOINT')

    try:
        assert token is not None
    except AssertionError:
        raise EnvironmentError('No token found for the Discord bot in the .env file. Please see the readme for details.')

    try:
        assert db_url is not None
    except AssertionError:
        raise EnvironmentError('No token found for the DB endpoint in the .env file. Please see the readme for details.')

    # Create bot
    bot = PhotoBot(db_url, command_prefix='!')

    # Add commands to bot
    @bot.hybrid_command(name='album',
                        description='Name the photo album for this channel ID.')
    async def name_album(ctx, album_name: str):
        await bot.name_album(ctx, album_name)
    
    @bot.hybrid_command(name='capture',
                        description='Start capturing uploaded photos in this channel.')
    async def capture_album(ctx):
        await bot.capture_album(ctx)

    @bot.hybrid_command(name='stop',
                        description='Stop capturing uploaded photos in this channel.')
    async def stop_capture_album(ctx):
        await bot.stop_capture_album(ctx)

    @bot.hybrid_command(name='sync_commands_photobot')
    async def sync_command_tree(ctx):
        await bot.sync_command_tree(ctx)

    bot.run(token)
