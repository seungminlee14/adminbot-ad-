"""Database helpers for the Hanbyeol administration bot."""

from __future__ import annotations

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

PunishmentRecord = dict[str, Any]
ReleaseRecord = dict[str, Any]


@dataclass(slots=True)
class _Entry:
    """Internal representation of a stored log entry."""

    kind: str
    user_id: int
    user_name: str
    punishment: str
    reason: str
    moderator_id: int
    moderator_name: str
    created_at: str
    duration: str | None = None

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Remove ``None`` duration so the consumer can omit the field.
        if data.get("duration") is None:
            data.pop("duration", None)
        return data


class Database:
    """Text-file backed storage for punishment data."""

    def __init__(self, path: str) -> None:
        self._path = Path(path)

    async def setup(self) -> None:
        """Ensure that the storage file exists."""

        await asyncio.to_thread(self._initialise_file)

    def _initialise_file(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("", encoding="utf-8")

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
        """Persist a punishment record to the storage file."""

        entry = _Entry(
            kind="punishment",
            user_id=user_id,
            user_name=user_name,
            punishment=punishment,
            reason=reason,
            duration=duration,
            moderator_id=moderator_id,
            moderator_name=moderator_name,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        await asyncio.to_thread(self._append_entry, entry.as_dict())

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
        """Persist a punishment release record to the storage file."""

        entry = _Entry(
            kind="release",
            user_id=user_id,
            user_name=user_name,
            punishment=punishment,
            reason=reason,
            moderator_id=moderator_id,
            moderator_name=moderator_name,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
        await asyncio.to_thread(self._append_entry, entry.as_dict())

    async def get_recent_punishments(self, limit: int) -> list[PunishmentRecord]:
        """Return the newest punishment entries."""

        entries = await asyncio.to_thread(self._read_entries)
        punishments = [entry for entry in entries if entry.get("kind") == "punishment"]
        return list(reversed(punishments[-limit:]))

    async def get_recent_releases(self, limit: int) -> list[ReleaseRecord]:
        """Return the newest punishment release entries."""

        entries = await asyncio.to_thread(self._read_entries)
        releases = [entry for entry in entries if entry.get("kind") == "release"]
        return list(reversed(releases[-limit:]))

    def _append_entry(self, entry: dict[str, Any]) -> None:
        self._initialise_file()
        with self._path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _read_entries(self) -> list[dict[str, Any]]:
        if not self._path.exists():
            return []

        entries: list[dict[str, Any]] = []
        with self._path.open("r", encoding="utf-8") as fp:
            for line in fp:
                data = line.strip()
                if not data:
                    continue
                try:
                    entries.append(json.loads(data))
                except json.JSONDecodeError:
                    # Skip malformed lines but keep processing newer entries.
                    continue
        return entries


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
