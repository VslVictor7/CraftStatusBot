from datetime import datetime
import os, asyncio
from dotenv import load_dotenv
from .birthday_database import has_sent_birthday_message, mark_birthday_sent

load_dotenv()

USER_ID = int(os.getenv("USER_ID"))
sent_birthdays = set()

def parse_birthdays(birthdays_str):
    birthdays = {}
    if birthdays_str:
        for item in birthdays_str.split(','):
            name, date = item.split(':')
            birthdays[name.strip()] = date.strip()
    return birthdays

async def send_birthday_messages(bot, birthdays, channel_id):
    today = datetime.now().strftime('%m-%d')
    birthday_friends = [name for name, date in birthdays.items() if date == today]

    if birthday_friends:
        channel = bot.get_channel(channel_id)
        if channel:
            for friend in birthday_friends:

                if not has_sent_birthday_message(friend):

                    user = bot.get_user(USER_ID)
                    if user:
                        await channel.send(f"🎉 {user.mention} Hoje é o aniversário de {friend}! Dê parabéns a ele/ela! 🎂🎈")
                    else:
                        await channel.send(f"🎉 Hoje é o aniversário de {friend}! Dê parabéns a ele/ela!🎂🎈")

                    mark_birthday_sent(friend)


async def birthday_check_periodically(bot, birthdays, channel_id, interval=5):
    while True:
        await send_birthday_messages(bot, birthdays, channel_id)
        await asyncio.sleep(interval)