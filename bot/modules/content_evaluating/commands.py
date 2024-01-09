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
from discord.ext.pages import Paginator

from bot.models import ModuleBase
from .db_ops import get_emoji_sets, get_emoji_set


class ContentEvaluating(ModuleBase):
    group = discord.SlashCommandGroup(
        name="content_evaluating",
        description="Commands for evaluating content",
        default_member_permissions=discord.Permissions(manage_guild=True),
        name_localizations={
            "en-US": "evaluating",
            "ru": "оценка",
        },
        description_localizations={
            "en-US": "Commands for evaluating content",
            "ru": "Команды для оценки контента",
        },
    )

    @group.command(
        name="sets",
        description="List all emoji sets",
        name_localizations={
            "en-US": "sets",
            "ru": "наборы",
        },
        description_localizations={
            "en-US": "List all emoji sets",
            "ru": "Список всех наборов эмодзи",
        },
    )
    async def emoji_sets(self, ctx: discord.ApplicationContext):
        sets = get_emoji_sets()

        if not sets:
            embed = discord.Embed(
                title="Не найдено наборов эмодзи",
                color=discord.Color.red(),
            )
            return await ctx.respond(embed=embed, ephemeral=True)

        pages = []

        for i in range(0, len(sets), 10):
            embed = discord.Embed(
                title="Наборы эмодзи",
                color=discord.Color.blurple(),
            )
            for emoji_set in sets[i : i + 10]:
                embed.add_field(
                    name=f"{emoji_set.id}: {emoji_set.name}",
                    value=", ".join(emoji.emoji for emoji in emoji_set.emojis)
                    or "Нет эмодзи",  # вывод всех эмодзи из набора
                    inline=False,
                )

            pages.append(embed)

        paginator = Paginator(pages=pages)
        await paginator.respond(ctx.interaction, ephemeral=True)

    @group.command(
        name="set",
        description="Get an emoji set",
        name_localizations={
            "en-US": "set",
            "ru": "набор",
        },
        description_localizations={
            "en-US": "Get information about a set of emojis",
            "ru": "Получить информацию о наборе эмодзи",
        },
    )
    @discord.option(
        name="set_id",
        description="ID of the emoji set",
        input_type=int,
        required=True,
        name_localizations={
            "en-US": "identifier",
            "ru": "идентификатор",
        },
        description_localizations={
            "en-US": "ID of the emoji set",
            "ru": "ID набора эмодзи",
        },
    )
    async def emoji_set(self, ctx: discord.ApplicationContext, set_id: int):
        emoji_set = get_emoji_set(set_id)
        embed = discord.Embed(
            title=f"{emoji_set.id}: {emoji_set.name}",
            color=discord.Color.blurple(),
        )
        emoji_list = [
            discord.PartialEmoji.from_str(emoji.emoji) for emoji in emoji_set.emojis
        ]
        embed.add_field(
            name="Эмодзи",
            value=", ".join(str(emoji) for emoji in emoji_list)
            or "Нет эмодзи",  # вывод всех эмодзи из набора
            inline=False,
        )

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(ContentEvaluating(bot))


def teardown(bot):
    bot.remove_cog(ContentEvaluating(bot))
