# Status Manager Bot

- A functional Discord bot created by myself to address a niche concept that suits my needs. Its main functionality is monitoring a Minecraft server, displaying the public IP of the machine running the JAVA server, the number of players, their names, and whether the server is online.

- Main support functionality: Minecraft server LOG in a Discord chat for better remote monitoring, show in embeds the players who joined and left the server, achievement logs are shown too.

- It is recommended to start the bot together with your main minecraft server is ON (Right about when the server is on succesfully, you can start the bot). The bot reads the latest.log file and would send everything again in the chat specified, so attention is advised (I'm looking into better solutions to this problem, any guidance would be appreciated).

- Be aware of the risks of using RCON. Do not map or port-foward the port of your RCON!

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
docker build -t discord-bot .
```
Run the container with:

```bash
docker-compose -f docker-compose-prod.yml -p discord-bot up -d
```

## 'Offline mode' servers:

- For offline servers, there is a variable in the .env.example that you can output a number "1" to set it to run in a offline server.

- It tracks the local UUID files, so it is important to read the .env.example with caution.

- Another thing, you need to create a "players.json" file inside bot/core/utils/json and map the player names and their respective UUID's.

- Example of "players.json":

```bash
{
   "test":"530fa97a-357f-3c19-94d3-0c5c65c18fe8",
   "Awesome-gamer-NAME":"487f52ba-919b-39c1-8a46-1e37aef66614",
   "Player1-nameEXAMPle":"0377e3e3-c767-330c-b352-70f60f5e7b83",
   "JorjinGamer":"86c5cd29-ecd6-3611-8e9a-c937807f9807"
}
```

- Be aware that the names are case sensitive, you must type it right as well as the UUID's.

- Type the UUID's in lower case as showed previously. As well as in the exact format showed.

## Important Notes

- .gitignore File: Include the name of your venv folder (e.g., venv/ or .venv/) in the .gitignore to avoid commit conflicts.

- Necessary Substitutions: Make sure to replace the tokens and IDs in the .env file to ensure the bot functions correctly.
