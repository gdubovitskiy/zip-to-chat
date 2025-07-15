import logging
import re
import zipfile
from pathlib import Path
from typing import Dict, List

from tqdm import tqdm

from src.const import SUPPORTED_EXTENSIONS
from src.logger import configure_logging

configure_logging()
logger = logging.getLogger(__name__)


class RepositoryAnalyzer:
    """Класс для анализа репозитория из ZIP-архива."""

    def __init__(self, zip_path: str):
        """Инициализация анализатора.

        Args:
            zip_path: Путь к ZIP-архиву с репозиторием.
        """
        self.zip_path = Path(zip_path)
        self._validate_zip_path()

    def _validate_zip_path(self) -> None:
        """Проверка существования ZIP-архива."""
        if not self.zip_path.exists():
            logger.error(f"File not found: {self.zip_path}")
            raise FileNotFoundError(f"ZIP archive {self.zip_path} does not exist")

    @staticmethod
    def _build_file_tree(file_list: List[str]) -> Dict:
        """Построение древовидной структуры файлов.

        Args:
            file_list: Список путей к файлам в архиве.

        Returns:
            Древовидная структура файлов в виде словаря.
        """
        file_tree = {}
        for file_path in file_list:
            # Пропускаем служебные файлы
            if "__MACOSX" in file_path or ".DS_Store" in file_path:
                continue

            parts = [p for p in file_path.split("/") if p]
            current = file_tree
            for part in parts:
                current = current.setdefault(part, {})
        return file_tree

    @staticmethod
    def _generate_tree_view(tree: Dict, prefix: str = "", is_root: bool = True) -> str:
        """Генерация строкового представления дерева файлов с использованием ASCII-графики.

        Args:
            tree: Древовидная структура файлов.
            prefix: Префикс для отступов (используется рекурсивно).
            is_root: Является ли текущий элемент корневым.

        Returns:
            Строковое представление дерева.
        """
        lines = []
        items = list(tree.items())
        for i, (name, children) in enumerate(items):
            is_current_last = i == len(items) - 1

            if is_root:
                # Для корневой директории не используем соединительные линии
                connector = ""
                icon = "📁 " if children else "📄 "
                lines.append(f"{prefix}{icon}{name}{'/' if children else ''}")
            else:
                # Для всех остальных уровней используем стандартное оформление
                connector = "└── " if is_current_last else "├── "
                icon = "📁 " if children else "📄 "
                lines.append(
                    f"{prefix}{connector}{icon}{name}{'/' if children else ''}"
                )

            if children:
                new_prefix = prefix + ("" if is_root or is_current_last else "│   ")
                lines.extend(
                    RepositoryAnalyzer._generate_tree_view(
                        children, new_prefix, is_root=False
                    ).splitlines()
                )
        return "\n".join(lines)

    @staticmethod
    def _extract_file_contents(zip_ref: zipfile.ZipFile) -> Dict[str, str]:
        """Извлечение содержимого поддерживаемых файлов.

        Args:
            zip_ref: Открытый ZIP-архив.

        Returns:
            Словарь с содержимым файлов (имя файла -> содержимое).
        """
        contents = {}
        # Фильтруем только поддерживаемые файлы
        file_list = [
            f
            for f in zip_ref.namelist()
            if any(f.endswith(ext) for ext in SUPPORTED_EXTENSIONS)
            and not ("__MACOSX" in f or ".DS_Store" in f)
        ]

        for file_path in tqdm(file_list, desc="Analyzing files", unit="file"):
            try:
                # Извлекаем чистое имя файла (без пути архива)
                clean_name = re.sub(r"^.*?/", "", file_path)
                with zip_ref.open(file_path) as file:
                    content = file.read().decode("utf-8")
                    contents[clean_name] = content
                    logger.debug(f"Read file: {clean_name}")
            except UnicodeDecodeError:
                logger.warning(f"Binary data in file: {clean_name}")
            except Exception as e:
                logger.error(f"Error reading {clean_name}: {str(e)}")
        return contents

    def analyze(self) -> dict:
        """Основной метод анализа репозитория.

        Returns:
            Словарь с результатами анализа:
            - structure: строковое представление структуры файлов
            - contents: содержимое поддерживаемых файлов

        Raises:
            zipfile.BadZipFile: Если архив поврежден.
            Exception: При других ошибках во время анализа.
        """
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                # Построение дерева структуры
                file_tree = self._build_file_tree(zip_ref.namelist())
                tree_view = self._generate_tree_view(file_tree)

                # Извлечение содержимого файлов
                file_contents = self._extract_file_contents(zip_ref)

                return {"structure": tree_view, "contents": file_contents}
        except zipfile.BadZipFile:
            logger.exception("Invalid ZIP file")
            raise
        except Exception as e:
            logger.exception("Unexpected error during analysis")
            raise
