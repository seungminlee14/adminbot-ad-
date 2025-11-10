"""Configuration helpers for the Hanbyeol administration bot."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class BotConfig:
    """Runtime configuration for the bot."""

    token: str
    guild_id: int | None
    announcement_channel_id: int
    punishment_role_id: int
    log_role_id: int
    database_path: str

    @classmethod
    def from_env(cls) -> "BotConfig":
        """Create a configuration object from environment variables."""

        token = os.environ.get("DISCORD_BOT_TOKEN")
        if not token:
            raise RuntimeError(
                "DISCORD_BOT_TOKEN 환경 변수가 설정되어 있지 않습니다. 봇 토큰을 지정해주세요."
            )

        guild_id_value = os.environ.get("DISCORD_GUILD_ID")
        guild_id = int(guild_id_value) if guild_id_value else None

        announcement_channel_id = int(
            os.environ.get("HANBYEOL_ANNOUNCEMENT_CHANNEL", "1434881803075846286")
        )
        punishment_role_id = int(
            os.environ.get("HANBYEOL_PUNISHMENT_ROLE", "1434877292546621602")
        )
        log_role_id = int(
            os.environ.get("HANBYEOL_LOG_ROLE", "1434877292546621602")
        )
        database_path = os.environ.get("HANBYEOL_DATABASE", "hanbyeol_logs.txt")

        return cls(
            token=token,
            guild_id=guild_id,
            announcement_channel_id=announcement_channel_id,
            punishment_role_id=punishment_role_id,
            log_role_id=log_role_id,
            database_path=database_path,
        )
