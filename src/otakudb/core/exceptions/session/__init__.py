from . import box, driver, navigator

__all__ = ["box", "driver", "navigator"]

class StorageUnmountedError(Exception):
	"""Исключение: хранилище не примонтировано."""

	def __init__(self):
		"""Исключение: хранилище не примонтировано."""

		super().__init__("Mount storage before operations.")