# 📦 ZIP to Chat - Анализатор ZIP-архивов репозиториев

Утилита для анализа содержимого ZIP-архивов с исходным кодом проектов. Извлекает структуру файлов и их содержимое для последующего анализа.

## 🚀 Установка

1. Убедитесь, что у вас установлен Python 3.10 или новее
2. Установите Poetry (если еще не установлен):
   ```bash
   pip install poetry
   ```
3. Установите зависимости:
   ```bash
   poetry install
   ```

## 🛠 Использование

```bash
poetry run zip-to-chat path/to/your/repository.zip
```

После выполнения команды в папке `out/` появится файл с анализом в формате JSON.

### Пример вывода в консоли:
```
🔍 Analyzing archive: example.zip
Analyzing files: 100%|██████████| 42/42 [00:00<00:00, 123.45file/s]
✅ Results saved to: out/example_analysis.json

Repository structure:
📁 project/
├── 📁 src/
│   ├── 📄 main.py
│   └── 📄 utils.py
├── 📁 tests/
│   └── 📄 test_utils.py
└── 📄 README.md

📊 Analyzed files: 42
```

## 📁 Структура проекта

```
zip-to-chat/
├── out/                # Папка для результатов анализа
├── src/
│   ├── cli.py          # Интерфейс командной строки
│   ├── const.py        # Поддерживаемые расширения файлов
│   ├── core.py         # Основная логика анализа
│   └── logger.py       # Настройка логгирования
├── poetry.lock         # Зависимости Poetry
└── pyproject.toml      # Конфигурация проекта
```

## 📋 Поддерживаемые форматы файлов

Утилита анализирует файлы со следующими расширениями:
- `.py`, `.js`, `.c`, `.cpp`, `.h`
- `.html`, `.css`, `.php`, `.rb`
- `.rs`, `.ts`, `.sh`, `.md`
- `.txt`, `.yml`, `.yaml`
- `.json`, `.xml`, `.toml`

## 📄 Формат выходного файла

Результат анализа сохраняется в JSON-файл со следующей структурой:
```json
{
  "structure": {
    "project/": {
      "src/": {
        "main.py": "py",
        "utils.py": "py"
      },
      "README.md": "md"
    }
  },
  "contents": {
    "main.py": "содержимое файла...",
    "utils.py": "содержимое файла..."
  }
}
```