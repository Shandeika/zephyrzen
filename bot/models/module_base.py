import logging
from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from bot.models import ZephyrzenBot


class ModuleBase(commands.Cog):
    def __init__(self, bot: "ZephyrzenBot", *args, **kwargs):
        self._bot = bot
        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__(*args, **kwargs)
        self._logger.info("Module loaded: %s", self.__class__.__name__)
