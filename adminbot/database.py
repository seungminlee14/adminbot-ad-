"""Database helpers for the Hanbyeol administration bot."""

from __future__ import annotations

import aiosqlite
from typing import Any, Iterable

PunishmentRecord = dict[str, Any]
ReleaseRecord = dict[str, Any]


class Database:
    """Lightweight SQLite wrapper for storing punishment data."""

    def __init__(self, path: str) -> None:
        self._path = path

    async def setup(self) -> None:
        """Initialise the required database tables."""

        async with aiosqlite.connect(self._path) as db:
            await db.executescript(
                """
                CREATE TABLE IF NOT EXISTS punishments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    punishment TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    duration TEXT,
                    moderator_id INTEGER NOT NULL,
                    moderator_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS punishment_releases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    user_name TEXT NOT NULL,
                    punishment TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    moderator_id INTEGER NOT NULL,
                    moderator_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            await db.commit()

    async def log_punishment(
        self,
        *,
        user_id: int,
        user_name: str,
        punishment: str,
        reason: str,
        duration: str | None,
        moderator_id: int,
        moderator_name: str,
    ) -> None:
        """Persist a punishment record to the database."""

        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                """
                INSERT INTO punishments (
                    user_id, user_name, punishment, reason, duration,
                    moderator_id, moderator_name
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    user_name,
                    punishment,
                    reason,
                    duration,
                    moderator_id,
                    moderator_name,
                ),
            )
            await db.commit()

    async def log_release(
        self,
        *,
        user_id: int,
        user_name: str,
        punishment: str,
        reason: str,
        moderator_id: int,
        moderator_name: str,
    ) -> None:
        """Persist a punishment release record to the database."""

        async with aiosqlite.connect(self._path) as db:
            await db.execute(
                """
                INSERT INTO punishment_releases (
                    user_id, user_name, punishment, reason,
                    moderator_id, moderator_name
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    user_name,
                    punishment,
                    reason,
                    moderator_id,
                    moderator_name,
                ),
            )
            await db.commit()

    async def get_recent_punishments(self, limit: int) -> list[PunishmentRecord]:
        """Return the newest punishment entries."""

        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM punishments ORDER BY id DESC LIMIT ?", (limit,)
            ) as cursor:
                rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def get_recent_releases(self, limit: int) -> list[ReleaseRecord]:
        """Return the newest punishment release entries."""

        async with aiosqlite.connect(self._path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM punishment_releases ORDER BY id DESC LIMIT ?",
                (limit,),
            ) as cursor:
                rows = await cursor.fetchall()
        return [dict(row) for row in rows]


def format_entries(entries: Iterable[dict[str, Any]]) -> list[str]:
    """Format database entries into Discord-friendly lines."""

    formatted = []
    for entry in entries:
        details = [
            f"• {entry['user_name']} (`{entry['user_id']}`)",
            f"  - 처벌: {entry['punishment']}",
            f"  - 사유: {entry['reason']}",
            f"  - 담당자: {entry['moderator_name']} (`{entry['moderator_id']}`)",
        ]
        duration = entry.get("duration")
        if duration:
            details.append(f"  - 기간: {duration}")
        timestamp = entry.get("created_at")
        if timestamp:
            details.append(f"  - 기록일: {timestamp}")
        formatted.append("\n".join(details))
    return formatted
