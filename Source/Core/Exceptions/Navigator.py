from pathlib import Path

class RootUnboxingDenied(Exception):
	"""Исключение: невозможно подняться из корневого каталога."""

	def __init__(self):
		"""Исключение: невозможно подняться из корневого каталога."""

		super().__init__("Storage root can't be unboxed.")

class UnableInboxNonBoxObject(Exception):
	"""Исключение: невозможно открыть объект, не являющийся хранилищем."""

	def __init__(self, virtual_path: Path):
		"""
		Исключение: невозможно открыть объект, не являющийся хранилищем.

		:param virtual_path: Виртуальный путь к объекты.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())