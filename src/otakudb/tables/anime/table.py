from typing import TYPE_CHECKING

from otakudb.core.base.table import BaseTable

if TYPE_CHECKING:
	from .manifest import CustomSettingsModel as CustomSettingsModel
	from .note import Note as Note

class Table(BaseTable["Note", "CustomSettingsModel"]):
	"""Anime views table."""

	pass