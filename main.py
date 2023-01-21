"""
Run the Discord bot.
"""
# Standard imports
from os import getenv

# Third party imports
from dotenv import load_dotenv

# Local imports
from bot import PhotoBot


if __name__ == '__main__':
    # Load in Discord token.
    load_dotenv()
    token = getenv('DISCORD_TOKEN')
    photo_url = getenv('PHOTO_ENDPOINT')

    try:
        assert token is not None
    except AssertionError:
        raise EnvironmentError('No token found for the Discord bot in the .env file. Please see the readme for details.')

    try:
        assert photo_url is not None
    except AssertionError:
        raise EnvironmentError('No token found for the photo endpoint in the .env file. Please see the readme for details.')

    # Create bot and run.
    bot = PhotoBot(photo_url, command_prefix='!')
    bot.run(token)