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
from discord.ui import Modal

from .db_ops import get_emoji_set, add_emoji_to_set, add_emoji


class EmojiAddModal(Modal):
    def __init__(self, set_id: int):
        self.set = get_emoji_set(set_id)
        super().__init__(title=f"Добавление эмодзи ({self.set.name})")
        self.set_id = set_id

    emoji = discord.ui.InputText(
        style=discord.InputTextStyle.short,
        label="Эмодзи",
        placeholder="❤",
    )

    async def on_submit(self, interaction: discord.Interaction):
        name = self.emoji.value
        # проверка на валидность эмодзи в Discord
        discord_emoji = discord.PartialEmoji.from_str(name)
        if discord_emoji.is_custom_emoji() or discord_emoji.is_unicode_emoji():
            # добавление эмодзи в базу данных
            emoji = add_emoji(name)
            await add_emoji_to_set(self.set_id, emoji.id)
        else:
            await interaction.response.send_message(
                "Эмодзи должен быть в Discord", ephemeral=True
            )
