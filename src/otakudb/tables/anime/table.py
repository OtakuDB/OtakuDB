from typing import TYPE_CHECKING

from otakudb.core.base.table import BaseTable

if TYPE_CHECKING:
	from .manifest import Manifest as Manifest
	from .note import Note as Note

class Table(BaseTable["Note", "Manifest"]):
	"""Anime views table."""

	pass
