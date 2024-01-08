"""
MIT License

Copyright (c) 2024 ArtyomK

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
import datetime
import random
import traceback

import discord
from discord import option, OptionChoice
from discord.ext import commands
from sqlalchemy import desc

from bot.models import ZephyrzenBot, ModuleBase, Session
from .tables import Report, Rule, Settings


class Reports(ModuleBase):

    async def get_rules(self, ctx: discord.AutocompleteContext):
        with Session() as s:
            if len(ctx.value) == 0:
                return [rule.code for rule in s.query(Rule).filter(Rule.guild_id == ctx.interaction.guild_id).all()]
            else:
                return [rule.code for rule in s.query(Rule).filter(Rule.guild_id == ctx.interaction.guild_id,
                                                                   Rule.code.icontains(ctx.value)).all()]

    async def create_channel(self, ctx: discord.ApplicationContext, id: int, code: str, applicant: discord.Member,
                             defendant: discord.Member, judge: discord.Member, description: str, proof: str):
        with Session() as s:
            settings = s.query(Settings).filter(Settings.guild_id == ctx.guild.id).one()
            category = None
            if settings.channels_category is not None:
                category = discord.utils.get(ctx.guild.categories, id=settings.channels_category)
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            applicant: discord.PermissionOverwrite(view_channel=True),
            defendant: discord.PermissionOverwrite(view_channel=True),
            judge: discord.PermissionOverwrite(view_channel=True)
        }
        channel = await ctx.guild.create_text_channel(f"#{id} {code} | {applicant} - {defendant}",
                                                      topic=description, overwrites=overwrites, category=category)
        embed = discord.Embed(title=f"Репорт #{id}", description=description, colour=discord.Colour.red())
        embed.add_field(name="Номер обращения", value=str(id), inline=True)
        embed.add_field(name="Нарушенное правило", value=code, inline=True)
        embed.add_field(name="ㅤ", value="ㅤ", inline=True)
        embed.add_field(name="Истец", value=applicant.mention, inline=True)
        embed.add_field(name="Ответчик", value=defendant.mention, inline=True)
        embed.add_field(name="Судья", value=judge.mention, inline=True)
        if proof is not None: embed.set_image(url=proof)
        await channel.send(embed=embed)
        return channel.id

    @discord.application_command(name="report", description="Сообщить о нарушении")
    @option("user", description="Пользователь, который нарушил правило.")
    @option("description", description="Опишите, что и как конкретно нарушил пользователь.")
    @option("rule", description="Какое правило нарушил пользователь.", autocomplete=get_rules)
    @option("proof", description="Если у вас есть доказательство, тогда приложите его.")
    @commands.guild_only()
    async def report(self, ctx: discord.ApplicationContext, user: discord.Member, description: str,
                     rule: str, proof: discord.Attachment = None):
        if user.bot:
            error_embed = discord.Embed(title='❌ Ошибка',
                                        description="Вы не можете отправить репорт на бота (даже если он нарушли правило)!",
                                        color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        if user.id == ctx.user.id:
            error_embed = discord.Embed(title='❌ Ошибка',
                                        description="Вы не можете отправить репорт на себя!",
                                        color=discord.Color.red())
            await ctx.respond(embed=error_embed, ephemeral=True)
        with Session() as s:
            judge_roles = s.query(Settings).filter(Settings.guild_id == ctx.guild.id).first().moderator_roles
            if judge_roles is None:
                owner_embed = discord.Embed(title=f'⚠️ Предупреждение',
                                            description=f"{ctx.user.mention} воспользовался командой {self.report.mention} на сервере {ctx.guild.name} ({ctx.guild.jump_url}), однако, на сервере не настроены роли модераторов!\nНастройте роли или выключите репорты на своём сервере.",
                                            color=discord.Color.yellow())
                await ctx.guild.owner.send(embed=owner_embed)
                error_embed = discord.Embed(title='❌ Ошибка',
                                            description="Роли модераторов на этом сервере не настроены!\nМы уже предупредили владельца сервера об этом, ожидайте его реакции.",
                                            color=discord.Color.red())
                await ctx.respond(embed=error_embed, ephemeral=True)
                return
            all_mods = list()
            for judje_role in judge_roles.split(';'):
                print(judje_role)
                role = ctx.guild.get_role(int(judje_role))
                print(role)
                all_mods.append(*role.members)
            mod = random.choice(all_mods)
            last_id = s.query(Report).order_by(desc(Report.id)).first()
            channel_id = await self.create_channel(ctx, last_id + 1 if last_id is not None else 1, rule, ctx.user,
                                                   user, mod, description, proof.url if proof is not None else None)
            report = Report(guild_id=ctx.guild.id, applicant_discord_id=ctx.user.id, defendant_discord_id=user.id,
                            judge_id=mod.id, channel_id=channel_id, title=f"", description=description, rule=rule,
                            photo_proof_url=proof.url if proof is not None else None,
                            start_time=datetime.datetime.now())
            try:
                s.add(report)
                embed = discord.Embed(title="✅ Репорт успешно создан!", color=discord.Color.green())
                await ctx.respond(embed=embed, ephemeral=True)
            except:
                s.rollback()
                embed = discord.Embed(title="❌ Во время создания репорта произошла ошибка!", color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)
                self._logger.error(traceback.format_exc())

    async def get_ticket(self, ctx: discord.AutocompleteContext):
        if len(ctx.value) > 3:
            with Session() as s:
                return [f'{report.title} - {(await self._bot.fetch_user(report.applicant_discord_id)).name}' for report
                        in s.query(Report).filter(Report.title.icontains(ctx.value)).all()]

    reports_group = discord.SlashCommandGroup(name="reports", description="Reports",
                                              checks=[discord.default_permissions(manage_messages=True)])

    @reports_group.command(name="list", description="Панель управления репортами.")
    @option("search", description="Имя нужного тикета.", autocomplete=get_ticket, required=False, default=None)
    @option("author", description="Автор нужного тикета.", required=False, default=None)
    @discord.default_permissions(manage_messages=True)
    @commands.guild_only()
    async def reports(self, ctx: discord.ApplicationContext, search: str = None, author: discord.Member = None):
        ...

    @discord.application_command(name="rule", description="Создать правило.")
    @option("code", description="Код правила.")
    @option("description", description="Описание правила.")
    @option("action", description="Наказание за нарушение правила.",
            choices=[OptionChoice(name="варн", value="warn"), OptionChoice(name='бан', value="ban")])
    @discord.default_permissions(administrator=True)
    @commands.guild_only()
    async def add_rule(self, ctx: discord.ApplicationContext, code: str, description: str, action: str):
        with Session() as s:
            s.add(Rule(guild_id=ctx.guild.id, code=code, description=description, violation_action=action))
            try:
                s.commit()
                embed = discord.Embed(title=f'✅ Правило {code} успешно добавлено!', color=discord.Color.green())
                await ctx.respond(embed=embed, ephemeral=True)
            except:
                s.rollback()
                self._logger.error(traceback.format_exc())
                embed = discord.Embed(title=f'❌ Возникла ошибка при добавлении правила {code}!',
                                      color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)

    @reports_group.command(name="settings", description="Настройки модуля Reports")
    @option("autoaction",
            description="Будет ли выполняться действие за нарушение автоматически, если модератор утвердил жалобу",
            choices=[discord.OptionChoice(name="Да", value=1), discord.OptionChoice(name="Нет", value=0)])
    @option("mod_role", description="Роль модератора. Если вы уже добавили роль, и введёте её ещё раз, она удалится.")
    @option("channel_category", description="Категория в которой будут создаваться каналы репортов.")
    @discord.default_permissions(administrator=True)
    @commands.guild_only()
    async def settings(self, ctx: discord.ApplicationContext, autoaction: int = None, mod_role: discord.Role = None,
                       channel_category: discord.CategoryChannel = None):
        if not ctx.user.top_role.permissions.administrator and not ctx.user.id == ctx.guild.owner_id:
            embed = discord.Embed(title=f'❌ Вы должны быть администратором!',
                                  color=discord.Color.red())
            await ctx.respond(embed=embed, ephemeral=True)
            return
        with Session() as s:
            settings = s.query(Settings).filter(Settings.guild_id == ctx.guild.id)
            guild = settings.one()
            if autoaction is not None:
                settings.update({Settings.auto_action: autoaction})
            if mod_role is not None:
                mod_roles = guild.moderator_roles.split(';')
                if str(mod_role.id) in mod_roles:
                    mod_roles.remove(str(mod_role.id))
                else:
                    mod_roles.append(str(mod_role.id))
                mod_roles = ';'.join(mod_roles).removeprefix(';')
                settings.update({Settings.moderator_roles: mod_roles})
            if channel_category is not None:
                settings.update({Settings.channels_category: channel_category.id})
            try:
                s.commit()
                embed = discord.Embed(title=f'✅ Настройки успешно применены!', color=discord.Color.green())
                await ctx.respond(embed=embed, ephemeral=True)
            except:
                s.rollback()
                self._logger.error(traceback.format_exc())
                embed = discord.Embed(title=f'❌ Во время применения настроек произошли ошибки!',
                                      color=discord.Color.red())
                await ctx.respond(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        with Session() as s:
            guild_settings = Settings(guild_id=guild.id)
            s.add(guild_settings)
            try:
                s.commit()
                self._logger.info(f'Сервер {guild.name} успешно добавлен!')
            except:
                s.rollback()
                self._logger.info(f'Во время добавления сервера {guild.name} произошла ошибка!')
                self._logger.error(traceback.format_exc())


def setup(bot: ZephyrzenBot):
    bot.add_cog(Reports(bot))


def teardown(bot: ZephyrzenBot):
    bot.remove_cog(Reports(bot))
