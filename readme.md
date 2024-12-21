# Status Manager Bot

- A functional Discord bot created by myself to address a niche concept that suits my needs. Its main functionality is monitoring a Minecraft server, displaying the public IP of the machine running the JAVA server, the number of players, their names, and whether the server is online.

- Main support functionality: Minecraft server LOG in a Discord chat for better remote monitoring, as well as showing in embeds the players who joined and left the server (this data is also recorded in the database).

- Secondary functionalities: GENIUS API for searching song lyrics, a command to display statistics of players who have played on the server, clearing server and DM (bot DM) chats.

## Table of Contents

- [Pre-requisites](#pre-requisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Executing](#executing)
- [Important Notes](#important-notes)

## Pre-requisites

- Python 3.8 or higher
- Docker (optional)

## Installation

1. **Clone the repository** (if you haven’t done so already):
```bash
   git clone <https://github.com/VslVictor7/Status-Manager-Bot.git>

   cd Status-Manager-Bot
```

2. **Create a Virtual Environment** (venv):

```bash
python -m venv venv
```

3. **Activate the Virtual Environment:**:
```bash
source .venv/scripts/activate
```

4. **Upgrade pip**
```bash
python -m pip install --upgrade pip
```

5. **Install requirements.txt**
```bash
pip install -r requirements.txt
```

## Configuration

1. **Configure the .env file**:

- Duplicate the .example-env file and rename it to .env

- Replace the values for token, IDs, and other fields as needed.

2. Send the bot's initial message:

- Python file directory: bot/core/utils/bot_sender.py

- The .env file must be configured correctly for the placeholder message step to work.

- Run the bot_sender.py script to send a placeholder message that will be used as a base to update the message with an embed showing Minecraft server information.
```bash
python bot_sender.py
```
- Don’t worry, you can run the script independently. As long as you're in the file directory, use 'py bot_sender.py' to run the script.

## Executing:

- After configuring the .env file and obtaining a placeholder message, run the bot through the following files:

run_message_manager.vbs (To run the bot without keeping any terminal open, useful for running it in the background)

ou

script.bat (If you want to see the terminal output normally.)

ou

- To run directly, execute main.py:
```bash
python main.py
```

Finally, if you plan to run it in a Docker container, read below:

## Running with Docker Container

- Make sure you are in the directory of the Dockerfile and docker-compose files.

- Ensure the .env and requirements.txt files are also in the directory mentioned above.

- After that, build the image with:

```bash
docker build -t discord-bot:prod .
```
Run the container with:

```bash
docker-compose -f docker-compose-prod.yml -p bot-prod up -d
```

## Important Notes

- .gitignore File: Include the name of your venv folder (e.g., venv/ or .venv/) in the .gitignore to avoid commit conflicts.

- Necessary Substitutions: Make sure to replace the tokens and IDs in the .env file to ensure the bot functions correctly.
