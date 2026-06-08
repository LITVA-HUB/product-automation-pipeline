from __future__ import annotations

from pathlib import Path

import httpx

from app.services.telegram.intake import IntakeEvent


class TelegramFileDownloader:
    def __init__(
        self,
        bot_token: str,
        storage_root: str = "local_storage",
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.bot_token = bot_token
        self.storage_root = Path(storage_root)
        self.client = client or httpx.AsyncClient(timeout=30)
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()

    async def download_for_event(self, event: IntakeEvent) -> IntakeEvent:
        file_id = event.item.payload.get("telegram_file_id")
        if not file_id:
            return event

        try:
            file_info = await self._get_file(str(file_id))
            file_path = file_info["file_path"]
            content = await self._download_file(file_path)
            local_path = self._write_file(event, file_path, content)
        except (httpx.HTTPError, KeyError, OSError) as exc:
            event.item.payload["download_error"] = str(exc)
            return event

        event.item.payload["storage_path"] = str(local_path)
        event.item.payload["telegram_file_path"] = file_path
        return event

    async def _get_file(self, file_id: str) -> dict:
        response = await self.client.get(
            f"https://api.telegram.org/bot{self.bot_token}/getFile",
            params={"file_id": file_id},
        )
        response.raise_for_status()
        payload = response.json()
        if not payload.get("ok"):
            raise KeyError(payload.get("description", "Telegram getFile returned ok=false"))
        return payload["result"]

    async def _download_file(self, file_path: str) -> bytes:
        response = await self.client.get(
            f"https://api.telegram.org/file/bot{self.bot_token}/{file_path}"
        )
        response.raise_for_status()
        return response.content

    def _write_file(self, event: IntakeEvent, file_path: str, content: bytes) -> Path:
        suffix = Path(file_path).suffix or Path(event.item.payload.get("file_name", "")).suffix
        target_dir = self.storage_root / "telegram" / str(event.id)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"source{suffix}"
        target.write_bytes(content)
        return target
