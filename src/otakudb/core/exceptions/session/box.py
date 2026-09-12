from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import Path

class BoxAlreadyInitializedError(Exception):
	"""Исключение: контейнер уже инициализирован."""

	def __init__(self, virtual_path: "Path"):
		"""
		Исключение: контейнер уже инициализирован.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class BoxItemOverrideError(Exception):
	"""Исключение: перезапись элемента контейнера."""

	def __init__(self, virtual_path: "Path"):
		"""
		Исключение: перезапись элемента контейнера.

		:param virtual_path: Виртуальный путь к перезаписываемому элементу.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class BoxNotEmptyError(Exception):
	"""Исключение: контейнер не пуст."""

	def __init__(self, virtual_path: "Path"):
		"""
		Исключение: контейнер не пуст.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class BoxNotInitializedError(Exception):
	"""Исключение: контейнер не инициализирован."""

	def __init__(self, virtual_path: "Path"):
		"""
		Исключение: контейнер не инициализирован.

		:param virtual_path: Виртуальный путь к контейнеру.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())
