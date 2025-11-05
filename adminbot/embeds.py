"""Utility helpers for building Discord embeds."""

from __future__ import annotations

from datetime import datetime, timezone

import discord


def punishment_embed(
    *,
    user: discord.Member | discord.User,
    punishment: str,
    reason: str,
    duration: str | None,
    moderator: discord.Member | discord.User,
) -> discord.Embed:
    """Build an embed describing a punishment event."""

    embed = discord.Embed(
        title="처벌 안내",
        description=f"{user.mention} 님에게 처벌이 적용되었습니다.",
        colour=discord.Colour.red(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="처벌 대상", value=f"{user} (`{user.id}`)")
    embed.add_field(name="처벌 종류", value=punishment, inline=False)
    embed.add_field(name="사유", value=reason, inline=False)
    embed.add_field(name="기간", value=duration or "기간이 지정되지 않았습니다.", inline=False)
    embed.set_footer(text=f"담당자: {moderator} | ID: {moderator.id}")
    return embed


def release_embed(
    *,
    user: discord.Member | discord.User,
    punishment: str,
    reason: str,
    moderator: discord.Member | discord.User,
) -> discord.Embed:
    """Build an embed describing a punishment release event."""

    embed = discord.Embed(
        title="처벌 해제 안내",
        description=f"{user.mention} 님의 처벌이 해제되었습니다.",
        colour=discord.Colour.blue(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.add_field(name="해제 대상", value=f"{user} (`{user.id}`)")
    embed.add_field(name="처벌 종류", value=punishment, inline=False)
    embed.add_field(name="사유", value=reason, inline=False)
    embed.set_footer(text=f"담당자: {moderator} | ID: {moderator.id}")
    return embed


def log_embed(*, punishments: list[str], releases: list[str]) -> discord.Embed:
    """Build an embed summarising stored punishments and releases."""

    embed = discord.Embed(
        title="처벌 로그",
        colour=discord.Colour.purple(),
        timestamp=datetime.now(timezone.utc),
    )

    if punishments:
        embed.add_field(name="최근 처벌", value="\n\n".join(punishments), inline=False)
    else:
        embed.add_field(name="최근 처벌", value="저장된 처벌이 없습니다.", inline=False)

    if releases:
        embed.add_field(name="최근 해제", value="\n\n".join(releases), inline=False)
    else:
        embed.add_field(name="최근 해제", value="저장된 해제 내역이 없습니다.", inline=False)

    return embed
