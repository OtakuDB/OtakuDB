class FreeMetainfoFieldsDeniedError(Exception):
	"""Exception: free metainfo fields denied."""

	def __init__(self):
		"""Exception: free metainfo fields denied."""

		super().__init__("Denied by table manifest.")

class MetainfoFieldNotFoundError(Exception):
	"""Exception: metainfo field not found."""

	def __init__(self, field_name: str):
		"""
		Exception: metainfo field not found.

		:param field_name: Metainfo field name.
		:type field_name: str
		"""

		super().__init__(field_name)

class MetainfoTypingError(Exception):
	"""Exception: metainfo field typing error."""

	def __init__(self, field_name: str, value_type: type, allowed_types: tuple[type, ...]):
		"""
		Exception: metainfo field typing error.

		:param field_name: Metainfo field name.
		:type field_name: str
		:param value_type: Value type.
		:type value_type: type
		:param allowed_types: Allowed types.
		:type allowed_types: tuple[type, ...]
		"""

		allowed: str = ", ".join(str(element) for element in allowed_types)

		super().__init__(f"Value of \"{field_name}\" is {value_type}, allowed: {allowed}.")

class MetainfoEnlistingDeniedError(Exception):
	"""Exception: enlisting denied for matainfo field."""

	def __init__(self, field_name: str):
		"""
		Exception: enlisting denied for matainfo field.

		:param field_name: Metainfo field name.
		:type field_name: str
		"""

		super().__init__(field_name)
