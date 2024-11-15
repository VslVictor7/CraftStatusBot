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

async def send_birthday_messages(bot, birthdays):
    today = datetime.now().strftime('%m-%d')
    birthday_friends = [name for name, date in birthdays.items() if date == today]

    if birthday_friends:
        user = bot.get_user(USER_ID)
        if user:
            for friend in birthday_friends:

                if not has_sent_birthday_message(friend):
                    await user.send(f"🎉 Hoje é o aniversário de {friend}! Dê parabéns a ele/ela! 🎂🎈")
                    mark_birthday_sent(friend)

async def birthday_check_periodically(bot, birthdays, interval=600):
    while True:
        await send_birthday_messages(bot, birthdays)
        await asyncio.sleep(interval)