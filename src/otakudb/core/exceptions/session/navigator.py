from pathlib import Path

class TableNotAtPathEndError(Exception):
	"""Exception: table item not at path end."""

	def __init__(self, virtual_path: Path):
		"""
		Exception: table item not at path end.

		:param virtual_path: Virtual path to item.
		:type virtual_path: Path
		"""

		# To-Do: make table name in path bold.

		super().__init__(virtual_path.as_posix())

class NotBoxError(Exception):
	"""Exception: target item isn't box."""

	def __init__(self, virtual_path: Path):
		"""
		Exception: target item isn't box.

		:param virtual_path: Virtual path to item.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class NotTableError(Exception):
	"""Exception: target item isn't table."""

	def __init__(self, virtual_path: Path):
		"""
		Exception: target item isn't table.

		:param virtual_path: Virtual path to item.
		:type virtual_path: Path
		"""

		super().__init__(virtual_path.as_posix())

class RootUnboxingError(Exception):
	"""Exception: unable out from storage root box."""

	def __init__(self):
		"""Exception: unable out from storage root box."""

		super().__init__("Unable out from storage root box.")
