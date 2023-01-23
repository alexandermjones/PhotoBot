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

    # Create bot and run.
    bot = PhotoBot(db_url, command_prefix='!')
    bot.run(token)