import logging
import os

from .models import ZephyrzenBot

logging.basicConfig(
    level=logging.INFO,
    format="{asctime} [{name}] [{levelname:<8}]: {message}",
    datefmt="%d.%m.%Y-%H:%M:%S",
    style="{",
)

bot = ZephyrzenBot()

bot.run(os.environ.get("DISCORD_TOKEN"))
