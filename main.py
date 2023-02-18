'''
Create and run the Discord bot.
'''

# Standard imports
from os import getenv

# Third party imports
import discord
from dotenv import load_dotenv

# Local imports
from bot import PhotoBot, add_commands_to_bot


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

    # Create bot and assign commands
    bot = PhotoBot(db_url, command_prefix='!')
    add_commands_to_bot(bot)

    bot.run(token)

    # Change presence of bot to watching for photos
    bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='for photos...'))
