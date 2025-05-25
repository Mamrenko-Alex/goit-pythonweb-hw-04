import asyncio
import os
import shutil
import logging
import argparse
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


async def copy_file(file_path: Path, output_dir: Path):
    try:
        extension = file_path.suffix[1:] or "no_extension"
        target_folder = output_dir / extension
        target_folder.mkdir(parents=True, exist_ok=True)

        target_path = target_folder / file_path.name
        await asyncio.to_thread(shutil.copy2, file_path, target_path)
        logging.info(f'Скопійовано: {file_path} → {target_path}')
    except Exception as e:
        logging.error(f'Помилка при копіюванні {file_path}: {e}')


async def read_folder(source_dir: Path, output_dir: Path):
    tasks = []
    for root, _, files in os.walk(source_dir):
        for name in files:
            file_path = Path(root) / name
            tasks.append(copy_file(file_path, output_dir))
    await asyncio.gather(*tasks)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Асинхронне сортування файлів за розширенням.')
    parser.add_argument('--source', '-s', type=str,
                        help='Шлях до вихідної папки', required=False)
    parser.add_argument('--output', '-o', type=str,
                        help='Шлях до цільової папки', required=False)
    return parser.parse_args()


async def main():
    args = parse_arguments()

    source_dir = Path(args.source)
    output_dir = Path(args.output)

    if not source_dir.exists() or not source_dir.is_dir():
        logging.error(f"Вихідна папка не існує: {source_dir}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    logging.info("Початок сортування файлів...")
    await read_folder(source_dir, output_dir)
    logging.info("Сортування завершено.")


if __name__ == '__main__':
    asyncio.run(main())
