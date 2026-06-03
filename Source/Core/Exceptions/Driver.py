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

class BoxNotEmpty(Exception):
	"""Исключение: контейнер не пуст."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: контейнер не пуст.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class StorageUnmounted(Exception):
	"""Исключение: хранилище не примонтировано."""

	def __init__(self):
		"""Исключение: хранилище не примонтировано."""

		super().__init__("Mount storage before navigation.")

class IncorrectTableType(Exception):
	"""Исключение: несуществующий тип таблицы."""

	def __init__(self, type: str):
		"""
		Исключение: несуществующий тип таблицы.

		:param type: Тип таблицы
		:type type: str
		"""

		super().__init__(type)

class ItemAlreadyExists(Exception):
	"""Исключение: элемент уже существует."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: элемент уже существует.

		:param virtual_path: Виртуальный путь к таблице.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class ItemNotFound(Exception):
	"""Исключение: контейнер не найден."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: элемент не найден.

		:param virtual_path: Виртуальный путь к элементу.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())