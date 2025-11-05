"""Entry point for the Hanbyeol administration Discord bot."""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

from adminbot.config import BotConfig
from adminbot.database import Database, format_entries
from adminbot.embeds import log_embed, punishment_embed, release_embed


def role_required(role_id: int) -> app_commands.Check:
    """Restrict a slash command to members with a specific role."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            raise app_commands.CheckFailure("길드 내에서만 사용할 수 있는 명령어입니다.")
        if any(role.id == role_id for role in interaction.user.roles):
            return True
        raise app_commands.CheckFailure("이 명령어를 실행할 권한이 없습니다.")

    return app_commands.check(predicate)


class HanbyeolBot(commands.Bot):
    """Discord bot that manages punishment reports for the Hanbyeol server."""

    def __init__(self, *, config: BotConfig) -> None:
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(command_prefix="!", intents=intents)
        self.config = config
        self.database = Database(config.database_path)

        self.hanbyeol = app_commands.Group(
            name="hanbyeol",
            description="Hanbyeol administration commands.",
            name_localizations={"ko": "한별"},
            description_localizations={"ko": "한별 서버 관리 명령어."},
        )
        self.tree.add_command(self.hanbyeol)

        self._register_commands()

    def _register_commands(self) -> None:
        @self.hanbyeol.command(
            name="send_punishment",
            description="Send a punishment notification to the configured channel.",
            name_localizations={"ko": "처벌정보전송"},
            description_localizations={"ko": "처벌 정보를 채널에 전송하고 데이터베이스에 저장합니다."},
        )
        @role_required(self.config.punishment_role_id)
        async def send_punishment(
            interaction: discord.Interaction,
            user: discord.Member,
            punishment: str,
            reason: str,
            duration: str | None = None,
        ) -> None:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await self.database.log_punishment(
                user_id=user.id,
                user_name=str(user),
                punishment=punishment,
                reason=reason,
                duration=duration,
                moderator_id=interaction.user.id,
                moderator_name=str(interaction.user),
            )

            channel = await self._resolve_channel()
            embed = punishment_embed(
                user=user,
                punishment=punishment,
                reason=reason,
                duration=duration,
                moderator=interaction.user,
            )
            await channel.send(embed=embed)
            await interaction.followup.send("처벌 정보를 전송하고 저장했습니다.", ephemeral=True)

        @self.hanbyeol.command(
            name="send_punishment_release",
            description="Send a punishment release notification to the configured channel.",
            name_localizations={"ko": "처벌해제정보전송"},
            description_localizations={"ko": "처벌 해제 정보를 채널에 전송하고 데이터베이스에 저장합니다."},
        )
        @role_required(self.config.punishment_role_id)
        async def send_punishment_release(
            interaction: discord.Interaction,
            user: discord.Member,
            punishment: str,
            reason: str,
        ) -> None:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await self.database.log_release(
                user_id=user.id,
                user_name=str(user),
                punishment=punishment,
                reason=reason,
                moderator_id=interaction.user.id,
                moderator_name=str(interaction.user),
            )

            channel = await self._resolve_channel()
            embed = release_embed(
                user=user,
                punishment=punishment,
                reason=reason,
                moderator=interaction.user,
            )
            await channel.send(embed=embed)
            await interaction.followup.send("처벌 해제 정보를 전송하고 저장했습니다.", ephemeral=True)

        @self.hanbyeol.command(
            name="punishment_log",
            description="Inspect stored punishment logs.",
            name_localizations={"ko": "처벌로그"},
            description_localizations={"ko": "저장된 처벌 로그를 확인합니다."},
        )
        @role_required(self.config.log_role_id)
        async def punishment_log(
            interaction: discord.Interaction, count: app_commands.Range[int, 1, 10]
        ) -> None:
            await interaction.response.defer(ephemeral=True, thinking=True)
            limit = min(50, count * 5)
            punishments = await self.database.get_recent_punishments(limit)
            releases = await self.database.get_recent_releases(limit)

            embed = log_embed(
                punishments=format_entries(punishments),
                releases=format_entries(releases),
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

    async def _resolve_channel(self) -> discord.TextChannel:
        """Resolve the announcement channel, fetching it if necessary."""

        channel = self.get_channel(self.config.announcement_channel_id)
        if channel is None:
            channel = await self.fetch_channel(self.config.announcement_channel_id)
        if not isinstance(channel, discord.TextChannel):
            raise RuntimeError("처벌 공지 채널을 텍스트 채널로 찾을 수 없습니다.")
        return channel

    async def setup_hook(self) -> None:
        await self.database.setup()
        await super().setup_hook()
        if self.config.guild_id:
            guild = discord.Object(id=self.config.guild_id)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()

    async def on_ready(self) -> None:
        await self.change_presence(activity=discord.Game(name="한별 서버 관리"))
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        if isinstance(error, app_commands.CheckFailure):
            message = str(error)
            if interaction.response.is_done():
                await interaction.followup.send(message, ephemeral=True)
            else:
                await interaction.response.send_message(message, ephemeral=True)
            return
        handler = getattr(super(), "on_app_command_error", None)
        if handler:
            await handler(interaction, error)
        else:
            raise error


def load_environment() -> None:
    """Load environment variables from a local `.env` file if present."""

    project_root = Path(__file__).resolve().parent
    env_path = project_root / ".env"
    loaded = False
    if env_path.exists():
        loaded = load_dotenv(env_path)
    if not loaded:
        load_dotenv(find_dotenv())


def main() -> None:
    load_environment()
    config = BotConfig.from_env()
    bot = HanbyeolBot(config=config)
    bot.run(config.token)


if __name__ == "__main__":
    main()
