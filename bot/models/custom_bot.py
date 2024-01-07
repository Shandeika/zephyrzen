import logging
import os.path

import discord
from discord.ext import commands


class ZephyrzenBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        super().__init__(command_prefix="zep.", intents=intents, *args, **kwargs)
        self._logger = logging.getLogger(self.__class__.__name__)

    async def module_loader(self):
        self._logger.info("Loading modules...")
        path = os.path.join("bot", "modules")
        for name in os.listdir(path):
            self.load_extension(f"bot.modules.{name}")
        self._logger.info(f"Loaded {len(self.extensions)} modules")

    async def on_connect(self):
        await self.module_loader()
        await self.sync_commands()

    async def on_ready(self):
        self._logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
