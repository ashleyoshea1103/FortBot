import os
import asyncio
import logging.handlers
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands


logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)

DT_FMT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname}] {name}: {message}', DT_FMT, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", description="", intents=intents,
                   activity=discord.Activity(name="Learning how to be a Bot",
                                             type=discord.ActivityType.watching))

async def load():
    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

async def main():
    load_dotenv()
    async with bot:
        await load()
        await bot.start(token=os.getenv("BOT_TOKEN"))

asyncio.run(main())
