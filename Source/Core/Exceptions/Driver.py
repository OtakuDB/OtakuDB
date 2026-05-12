from pathlib import Path

class PathNotFound(Exception):
	"""Исключение: не найден вирутальный путь в таблице."""

	def __init__(self):
		"""Исключение: не найден вирутальный путь в таблице."""

		super().__init__("Path not found in table.")

class StorageUnmounted(Exception):
	"""Исключение: хранилище не примонтировано."""

	def __init__(self):
		"""Исключение: хранилище не примонтировано."""

		super().__init__("Mount storage before navigation.")

class TableAlreadyExists(Exception):
	"""Исключение: таблица уже существует."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: таблица уже существует.

		:param virtual_path: Виртуальный путь к таблице.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())