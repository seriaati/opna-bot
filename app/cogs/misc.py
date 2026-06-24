import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from app.core.embeds import DefaultEmbed

if TYPE_CHECKING:
    from app.core.bot import OpnaBot
    from app.types import Interaction


class MiscCog(commands.Cog):
    def __init__(self, bot: OpnaBot) -> None:
        self.bot = bot

    @app_commands.command(name="分隊", description="把語音頻道裡的人分成兩隊")
    async def split_teams(
        self,
        i: Interaction,
        a_team_num: app_commands.Range[int, 1, 5],
        b_team_num: app_commands.Range[int, 1, 5],
    ) -> None:
        """把語音頻道裡的人分成兩隊"""
        if not isinstance(i.user, discord.Member):
            await i.response.send_message("你不是伺服器成員", ephemeral=True)
            return

        voice_state = i.user.voice
        if not voice_state or not voice_state.channel:
            await i.response.send_message("你不在語音頻道裡", ephemeral=True)
            return

        members = [m for m in voice_state.channel.members if not m.bot]
        if len(members) < a_team_num + b_team_num:
            await i.response.send_message(
                f"語音頻道裡的人數不足, 至少需要 {a_team_num + b_team_num} 人", ephemeral=True
            )
            return

        random.shuffle(members)
        a_team = members[:a_team_num]
        b_team = members[a_team_num : a_team_num + b_team_num]

        embed = DefaultEmbed(title="分隊結果")
        embed.add_field(name="A 隊", value="\n".join(m.mention for m in a_team))
        embed.add_field(name="B 隊", value="\n".join(m.mention for m in b_team))

        await i.response.send_message(embed=embed)


async def setup(bot: OpnaBot) -> None:
    await bot.add_cog(MiscCog(bot))
