from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger

from app.constants import DYNAMIC_VC_TRIGGER_ID
from app.db.models import VoiceChannel

if TYPE_CHECKING:
    from app.core.bot import OpnaBot
    from app.types import Interaction


class VoiceCog(commands.Cog):
    voice = app_commands.Group(name="語音", description="語音頻道相關指令")

    def __init__(self, bot: OpnaBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if after.channel is not None and after.channel.id == DYNAMIC_VC_TRIGGER_ID:
            await self._create_channel(member, after.channel)

        if (
            before.channel is not None
            and not before.channel.members
            and await VoiceChannel.filter(id=before.channel.id).exists()
        ):
            await self._delete_channel(before.channel)

    async def _create_channel(
        self, member: discord.Member, trigger: discord.VoiceChannel
    ) -> None:
        category = trigger.category
        overwrites = dict(category.overwrites) if category is not None else {}
        overwrites[member] = discord.PermissionOverwrite(
            manage_channels=True, move_members=True
        )

        channel = await member.guild.create_voice_channel(
            name=f"{member.display_name} 的語音",
            category=category,
            overwrites=overwrites,
        )
        await VoiceChannel.create(id=channel.id, owner_id=member.id)

        try:
            await member.move_to(channel)
        except discord.HTTPException:
            # Member left before we could move them; drop the empty channel.
            await self._delete_channel(channel)

    async def _delete_channel(self, channel: discord.VoiceChannel) -> None:
        await VoiceChannel.filter(id=channel.id).delete()
        try:
            await channel.delete()
        except discord.HTTPException:
            logger.exception(f"Failed to delete dynamic voice channel {channel.id}")

    async def _resolve_owned_channel(
        self, i: Interaction
    ) -> discord.VoiceChannel | None:
        """Return the voice channel the user owns, or reply with an error and return None."""
        if not isinstance(i.user, discord.Member):
            await i.response.send_message("你不是伺服器成員", ephemeral=True)
            return None

        voice_state = i.user.voice
        if voice_state is None or not isinstance(
            voice_state.channel, discord.VoiceChannel
        ):
            await i.response.send_message("你不在語音頻道裡", ephemeral=True)
            return None

        channel = voice_state.channel
        record = await VoiceChannel.get_or_none(id=channel.id)
        if record is None or record.owner_id != i.user.id:
            await i.response.send_message("你不是這個頻道的擁有者", ephemeral=True)
            return None

        return channel

    @voice.command(name="鎖定", description="鎖定你的語音頻道, 其他人可看見但無法加入")
    async def lock(self, i: Interaction) -> None:
        """鎖定你的語音頻道, 其他人可看見但無法加入"""
        channel = await self._resolve_owned_channel(i)
        if channel is None:
            return

        everyone = channel.guild.default_role
        overwrite = channel.overwrites_for(everyone)
        overwrite.connect = False
        await channel.set_permissions(everyone, overwrite=overwrite)

        await i.response.send_message(f"已鎖定 {channel.mention}", ephemeral=True)

    @voice.command(name="解鎖", description="解鎖你的語音頻道, 讓所有人都能加入")
    async def unlock(self, i: Interaction) -> None:
        """解鎖你的語音頻道, 讓所有人都能加入"""
        channel = await self._resolve_owned_channel(i)
        if channel is None:
            return

        everyone = channel.guild.default_role
        overwrite = channel.overwrites_for(everyone)
        overwrite.connect = None
        await channel.set_permissions(everyone, overwrite=overwrite)

        await i.response.send_message(f"已解鎖 {channel.mention}", ephemeral=True)

    @voice.command(name="重新命名", description="重新命名你的語音頻道")
    @app_commands.rename(name="名稱")
    @app_commands.describe(name="新的頻道名稱")
    async def rename(self, i: Interaction, name: app_commands.Range[str, 1, 100]) -> None:
        """重新命名你的語音頻道"""
        channel = await self._resolve_owned_channel(i)
        if channel is None:
            return

        await channel.edit(name=name)
        await i.response.send_message(f"已重新命名為 {channel.mention}", ephemeral=True)


async def setup(bot: OpnaBot) -> None:
    await bot.add_cog(VoiceCog(bot))
