from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

class ItemAlreadyExistsError(Exception):
	"""Исключение: элемент уже существует."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: элемент уже существует.

		:param virtual_path: Виртуальный путь к элементу.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class ItemNotFoundError(Exception):
	"""Исключение: элемент не найден."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: элемент не найден.

		:param virtual_path: Виртуальный путь к элементу.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class TableTypeNotFoundError(Exception):
	"""Исключение: тип таблицы не найден."""

	def __init__(self, table_type: str):
		"""
		Исключение: тип таблицы не найден.

		:param table_type: Тип таблицы.
		:type table_type: str
		"""
		
		super().__init__(table_type)
