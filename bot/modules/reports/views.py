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
import discord
from discord import ui, Interaction
from discord.ext import pages

from .tables import Report, Rule, Settings
from bot.models import Session


def create_page_embed(
    report: Report,
    rule: Rule,
    applicant: discord.Member,
    defendant: discord.Member,
    judge: discord.Member,
) -> discord.Embed:
    embed = discord.Embed(
        title=f"Репорт #{report.id}",
        description=report.description,
        colour=discord.Colour.red(),
    )
    embed.add_field(name="Номер обращения", value=str(report.id), inline=True)
    embed.add_field(name="Нарушенное правило", value=rule.code, inline=True)
    embed.add_field(name="Статус", value=report.status, inline=True)
    embed.add_field(name="Истец", value=applicant.mention, inline=True)
    embed.add_field(name="Ответчик", value=defendant.mention, inline=True)
    embed.add_field(name="Судья", value=judge.mention, inline=True)
    if report.photo_proof_url is not None:
        embed.set_image(url=report.photo_proof_url)
    return embed


class ReportsPaginator(pages.Paginator):
    def __init__(
        self, reports: list[Report], ctx: discord.Interaction, *args, **kwargs
    ):
        self.pages = list()
        with Session() as s:
            for report in reports:
                rule = s.query(Rule).filter(Rule.id == report.rule).one()
                applicant = ctx.guild.get_member(report.applicant_discord_id)
                defendant = ctx.guild.get_member(report.defendant_discord_id)
                judge = ctx.guild.get_member(report.judge_id)
                embed = create_page_embed(report, rule, applicant, defendant, judge)
                self.pages.append(
                    pages.Page(
                        embeds=[embed],
                        custom_view=ReportView(
                            applicant,
                            defendant,
                            judge,
                            ctx.user,
                            report,
                            rule,
                            self,
                            len(self.pages),
                        ),
                    )
                )
        super().__init__(self.pages, loop_pages=True, *args, **kwargs)


class ReportView(ui.View):
    def __init__(
        self,
        applicant: discord.Member,
        defendant: discord.Member,
        judge: discord.Member,
        author: discord.Member,
        report: Report,
        rule: Rule,
        paginator: ReportsPaginator,
        page: int,
    ):
        self.applicant = applicant
        self.defendant = defendant
        self.judge = judge
        self.author = author
        self.report = report
        self.rule = rule
        self.paginator = paginator
        self.page = page
        super().__init__()
        if report.status == "Открыто":
            self.accept.disabled = False

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return (
            interaction.user.id == interaction.guild.owner.id
            or interaction.user.id == self.judge.id
            or interaction.user.id == self.author.id
        )

    async def on_check_failure(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            f"У вас нет прав на взаимодействие!", ephemeral=True
        )

    async def update_page(self, interaction: discord.Interaction):
        with Session() as s:
            embed = embed = create_page_embed(
                self.report, self.rule, self.applicant, self.defendant, self.judge
            )
            if self.report.photo_proof_url is not None:
                embed.set_image(url=self.report.photo_proof_url)
            self.paginator.pages[self.page] = pages.Page(
                embeds=[embed], custom_view=self
            )
            await interaction.followup.edit_message(
                message_id=self.paginator.message.id,
                embed=embed,
                view=self.paginator,
            )

    @ui.button(
        label="Подтвердить нарушение",
        style=discord.ButtonStyle.green,
        emoji="✅",
        disabled=True,
    )
    async def accept(self, button: ui.Button, interaction: discord.Interaction):
        with Session() as s:
            settings = (
                s.query(Settings)
                .filter(Settings.guild_id == interaction.guild_id)
                .one()
            )
            if settings.auto_action:
                pass  # auto warn/ban
            report = s.query(Report).filter(Report.id == self.report.id)
            report.update({Report.status: "Принято"})
            try:
                s.commit()
                report_close = f"Дело закрыто в пользу {self.applicant.mention}"
                self.accept.disabled = True
                self.report = report.one()
                await interaction.guild.get_channel(self.report.channel_id).delete(
                    reason=report_close
                )
                await interaction.response.send_message(report_close, ephemeral=True)
            except:
                s.rollback()
                await interaction.response.send_message(
                    "Возникла ошибка, попробуйте позже.", ephemeral=True
                )
        await self.update_page(interaction)
