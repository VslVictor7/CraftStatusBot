# Status Manager Bot

- A functional Discord bot created by myself to address a niche concept that suits my needs. Its main functionality is monitoring a Minecraft server, displaying the public IP of the machine running the JAVA server, the number of players, their names, and whether the server is online.

- Main support functionality: Minecraft server LOG in a Discord chat for better remote monitoring, show in embeds the players who joined and left the server, achievement logs are shown too.

- It is recommended to start the bot together with your main minecraft server is ON (Right about when the server is on succesfully, you can start the bot). The bot reads the latest.log file and would send everything again in the chat specified, so attention is advised (I'm looking into better solutions to this problem, any guidance would be appreciated).

- Be aware of the risks of using RCON. Do not map or port-foward the port of your RCON!

## How things should look!

Server will show all of its data in real time, how many players, their names, if the server is online, etc.

![Tela Inicial](bot/images/server_online.png)
![Tela Inicial](bot/images/server_offline.png)

![Tela Inicial](bot/images/real_time.jpg)

---

Communication between discord server and minecraft server through RCON:

![uses](bot/images/normal_use.png)

---

Players joining and leaving the server!

![activity](bot/images/server_activity.png)

---

Advancements/goals/challenges will be shown with their respective color!

![goal](bot/images/goal1.png)
![goal](bot/images/goal2.png)

---

Deaths of players, named entities and villagers will be shown!

![morte](bot/images/named_entity_death.png)
![morte](bot/images/villager_death.png)
![morte](bot/images/player_death.png)

---

# Now, lets get started!

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


## 'Offline mode' servers (Ignore section if your server is "online-mode:true"):

- For offline servers, there is a variable in the .env.example that you can output a number "1" to set it to run in a offline server.

- It tracks the local UUID files, so it is important to read the .env.example with caution.

1. **Create a "players.json" file inside bot/core/utils/json and map the player names and their respective UUID's**

- Example of "players.json" (Add more players in the same format as bellow if you want to):

```bash
{
   "Awesome-gamer-NAME": {
        "uuid": "487f52ba-919b-39c1-8a46-1e37aef66614",
        "original": false,
        "skin": null
   },
   "Player1-nameEXAMPle": {
        "uuid": "0377e3e3-c767-330c-b352-70f60f5e7b83",
        "original": true,
        "skin": null
   },
   "JorjinGamer": {
        "uuid": "86c5cd29-ecd6-3611-8e9a-c937807f9807",
        "original": false,
        "skin": "https://p.novaskin.me/6250983452049408.png?class=thumbnail"
   }
}
```

- If player DOES have the original game: set "true" in original and "null" in skin.

- If player DOES NOT have the original game: set "false" in original and in skin, add a domain directly to a .png file of the helm (face of the minecraft skin). For instance:

"https://p.novaskin.me/6250983452049408.png?class=thumbnail"

**IMPORTANT: the uuid's present in the "players.json" are NOT the online uuid's you find in the internet! They are a separate type of UUID.**

- Go to the directory present in "bot/tools/offline-uuid.py", that's a function to see what is the UUID of a set String. It should look like this:

![Screenshot](bot/images/offline-uuid.png)

- In the line present in "final = get_offline_uuid("test")" change the string "test" to the username you want to get the uuid. For isntance:

```bash
final = get_offline_uuid("JorjinGamer")
```

- Be certain to be in the same directory as the said script before you run it, then run the script by using:

```bash
py offline-uuid.py
```

- The script should return something like this:

```bash
86c5cd29-ecd6-3611-8e9a-c937807f9807
```

## Docker configuration (Ignore section if you're not using docker)

- You might need to tweak some things depending on how you're planning to run the bot.

- The compose file, by default, is looking like this:

```bash
services:
  discord-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bot-desenvolvimento
    image: discord-bot:dev
    env_file:
      - .env
    tty: true
    stdin_open: true
    environment:
      RCON_PASSWORD: ${RCON_PASSWORD}
      RCON_PORT: ${RCON_PORT}
    volumes:
      - server_test:/data:ro
      - /data/logs/latest.log:/logs/latest.log
      - /data/world/stats:/world/stats
    networks:
      - request

volumes:
  server_test:
    external: true

networks:
  request:
    external: true
```

- It considers: 1. You're running the minecraft server in a docker container (Itzg minecraft image or a custom one). 2. The api is running on a container too.

- Why is this you ask? 

1. The bot will read the latest.log file as well as getting the stats from the players in the /stats directory. the volume is needed for that reason.

2. The network is made to avoid the mapping of the RCON port and to make requests for the api. In any circumstance you SHOULD NOT map the RCON port.

- If that's your case, just change the name of the volume and networks to the one you're using in the services mentioned the line behind.

**If that's not your use case, that's okay too, here's the guide:**

- As mentioned in the ENV variables section, this part will be a little similar.

1. You need to get the path of your stats folder and the path of the latest.log file. example bellow:

```bash
services:
  discord-bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: bot-desenvolvimento
    image: discord-bot:dev
    env_file:
      - .env
    tty: true
    stdin_open: true
    environment:
      RCON_PASSWORD: ${RCON_PASSWORD}
      RCON_PORT: ${RCON_PORT}
    volumes:
      - "C:path/to/your/server/world/stats:/data/world/stats"
      - "C:path/to/your/server/logs/latest.log:/data/logs/latest.log"
```
- That should be your compose file! Now keep going down to see how to run!

## Executing:

- After configuring the .env file and obtaining a placeholder message, run the bot using:

```bash
python main.py
```

(Be sure to be in the same directory as "main.py" before running the script)

Finally, if you plan to run it in a Docker container, read below:

## Running with Docker Container

- Make sure you are in the directory of the Dockerfile and docker-compose files.

- Ensure the .env and requirements.txt files are also in the directory mentioned above.

Run the container with:

```bash
docker compose up --build
```

## Important Notes

- .gitignore File: Include the name of your venv folder (e.g., venv/ or .venv/) in the .gitignore to avoid commit conflicts.

- Necessary Substitutions: Make sure to replace the tokens and IDs in the .env file to ensure the bot functions correctly.
