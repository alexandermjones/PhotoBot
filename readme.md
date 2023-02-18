# Photo Bot

Photo Bot is a Python program for running a Discord bot which sends images uploaded in Discord to a designated URL.

## About

The intended use-case of this bot is to capture all images (e.g. holiday photos) sent in a Discord channel to a designated URL, for saving and processing.

**Note:** all uploads to Discord are **public**, which is how this is possible.

## Installation

Tested working on Python 3.9.0.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the requirements.

```bash
pip3 install -r requirements.txt
```

To use the bot with Discord you will need to create a Discord token. A guide on how to do this is available [here](https://www.writebots.com/discord-bot-token/).

Create a file named `.env` in the root of this repository and then add environment variables of `<my-discord-token>` (created in the step above) and `<my-db-url>` which is the URL (with port if not default) connect to the database with. The file should look like:

```javascript
DISCORD_TOKEN=<my-discord-token>
DB_ENDPOINT=<my-db-url>
```

## Usage

Run the file `main.py` using Python.

```bash
python3 main.py
```

The following commands are usable with the bot when prefixed (default is `!`), also available as slash commands:

```
​Commands:
  album     Name the photo album for this channel ID.
  capture   Start capturing uploaded photos in this channel.
  help      Shows the available commands.
  stop      Stop capturing uploaded photos in this channel.
```

To ensure slash commands display properly, the owner of the bot should use `!sync_command_tree`.

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

## Acknowledgements

Icon taken, available free for commercial use, from [here](https://www.iconfinder.com/icons/379526/camera_front_icon).