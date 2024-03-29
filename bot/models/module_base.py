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
from typing import TYPE_CHECKING

from discord.ext import commands

from .database import Base, engine

if TYPE_CHECKING:
    from bot.models import ZephyrzenBot


class ModuleBase(commands.Cog):
    def __init__(self, bot: "ZephyrzenBot", *args, **kwargs):
        self._bot = bot
        self._logger = logging.getLogger(self.__class__.__name__)
        self.table_creator()
        super().__init__(*args, **kwargs)
        self._logger.info("Module loaded: %s", self.__class__.__name__)

    def table_creator(self):
        self._logger.info("Creating tables...")
        Base.metadata.create_all(engine)
        self._logger.info("Tables created")
