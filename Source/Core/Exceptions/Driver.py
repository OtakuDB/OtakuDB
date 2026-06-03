from pathlib import Path

class BoxItemOverride(Exception):
	"""Исключение: перезапись элемента контейнера."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: перезапись элемента контейнера.

		:param virtual_path: Виртуальный путь к перезаписываемому элементу.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class BoxNotFound(Exception):
	"""Исключение: контейнер не найден."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: контейнер не найден.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

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