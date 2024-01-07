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

import discord

from bot.models import ZephyrzenBot, ModuleBase, Session
from .tables import HelloTable


class Hello(ModuleBase):
    @discord.application_command(name="hello", description="Say hello!")
    async def test(self, interaction: discord.ApplicationContext):
        with Session() as session:
            current_user_hello = (
                session.query(HelloTable).filter_by(name=interaction.user.name).first()
            )

            if current_user_hello:
                current_user_hello.count += 1
                session.commit()
            else:
                new_user_hello = HelloTable(name=interaction.user.name, count=1)
                session.add(new_user_hello)
                session.commit()

        if not current_user_hello:
            await interaction.response.send_message("Hello, world!")
        else:
            await interaction.response.send_message(
                f"Hello, {interaction.user.name}! You've said hello {current_user_hello.count} times."
            )


def setup(bot: ZephyrzenBot):
    bot.add_cog(Hello(bot))


def teardown(bot: ZephyrzenBot):
    bot.remove_cog(Hello(bot))
