# Async File Sorter

Цей скрипт асинхронно читає всі файли з вихідної директорії та копіює їх у підпапки цільової директорії на основі розширення файлу.

## ⚙️ Функціонал

- Асинхронне копіювання файлів (`asyncio`, `to_thread`)
- Рекурсивний обхід всіх підпапок
- Розподіл файлів за розширенням (наприклад: `.jpg`, `.txt`, `.pdf`)
- Обробка аргументів командного рядка
- Мінімальне логування
- Підтримка роботи без аргументів (інтерактивний режим)

## 🖥️ Використання

### 1. Запуск з аргументами:

```bash
python async_sort.py --source ./unsorted --output ./sorted
```
