from typing import TYPE_CHECKING

from otakudb.interfaces.cli.base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from ....note import Note as Note
	from ....table import Table as Table

class TableHandlers(BaseHandlersCollection["Table", "Note"]):
	"""Table handlers."""

	pass
