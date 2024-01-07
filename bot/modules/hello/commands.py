import discord

from bot.models import ZephyrzenBot, ModuleBase


class Hello(ModuleBase):
    @discord.application_command(name="hello", description="Say hello!")
    async def test(self, interaction: discord.ApplicationContext):
        await interaction.response.send_message("Hello, world!")


def setup(bot: ZephyrzenBot):
    bot.add_cog(Hello(bot))


def teardown(bot: ZephyrzenBot):
    bot.remove_cog(Hello(bot))
