"""
MIT License

Copyright (c) 2024 Shandy

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import os
import os.path

import discord
from discord.ext import commands


class ZephyrzenBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.members = True
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
