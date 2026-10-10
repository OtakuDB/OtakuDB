from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from .enums import InteractionLevels

class ObjectUnavailableError(Exception):
	"""Exception: object unavailable."""

	def __init__(self, unavailable_object: "InteractionLevels"):
		"""
		Exception: object unavailable.

		:param unavailable_object: Object of interaction level.
		:type unavailable_object: InteractionLevels
		"""

		super().__init__(unavailable_object.name)
