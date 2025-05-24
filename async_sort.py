#!/usr/bin/env python3
"""
Асинхронне сортування файлів за розширенням
(версія на aiopath / aioshutil / aiofile).

Приклад запуску:
    python sort_async_aio.py ~/Downloads ~/Sorted
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aioshutil import copyfile  # асинхронний аналог shutil.copy2

# Скільки копіювань паралельно — щоб не «забити» диск.
MAX_PARALLEL_COPIES = 50
_sema = asyncio.Semaphore(MAX_PARALLEL_COPIES)


async def copy_file(src: AsyncPath, dst_root: AsyncPath) -> None:
    """
    Копіює *src* у підпапку *dst_root/<ext>* асинхронно.

    Для демонстрації роботи **aiofile** читаємо перші 64 байти
    та пишемо їх у LOG, але ядро копіювання робить **aioshutil.copyfile**.
    """
    ext = src.suffix.lower().lstrip(".") or "no_extension"
    dst_dir = dst_root / ext
    await dst_dir.mkdir(parents=True, exist_ok=True)

    dst_path = dst_dir / src.name

    async with _sema:
        try:
            # основне асинхронне копіювання
            await copyfile(src, dst_path)

            # маленький «бонус» — читаємо перші байти через aiofile
            # (необов’язково для завдання, просто щоб показати синтаксис)
            from aiofile import async_open

            async with async_open(src, "rb") as afp:
                head = await afp.read(64)
                logging.debug("Перші байти %s: %s", src.name, head[:16].hex())

        except Exception:  # noqa: BLE001
            logging.exception("Не вдалося скопіювати %s → %s", src, dst_path)


async def read_folder(src_root: AsyncPath, dst_root: AsyncPath) -> None:
    """
    Рекурсивно обходить *src_root* та ставить завдання на копіювання файлів.
    Використовує асинхронний **rglob** з aiopath.
    """
    tasks: list[asyncio.Task] = []

    async for path in src_root.rglob("*"):
        if await path.is_file():
            tasks.append(asyncio.create_task(copy_file(path, dst_root)))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Асинхронно сортує файли у підпапки за їх розширенням."
    )
    parser.add_argument("source", help="Вихідна (source) директорія")
    parser.add_argument("output", help="Цільова (output) директорія")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    src_root = AsyncPath(args.source).expanduser().resolve()
    dst_root = AsyncPath(args.output).expanduser().resolve()

    if not src_root.exists():
        raise SystemExit(f"Помилка: {src_root} не існує")

    logging.basicConfig(
        filename="file_sorter_async.log",
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s",
        encoding="utf-8",
    )

    try:
        asyncio.run(read_folder(src_root, dst_root))
    except KeyboardInterrupt:
        logging.warning("Роботу перервано користувачем (Ctrl-C)")


if __name__ == "__main__":
    main()
