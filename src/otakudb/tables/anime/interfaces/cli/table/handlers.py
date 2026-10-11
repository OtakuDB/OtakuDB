from typing import TYPE_CHECKING

from otakudb.interfaces.cli.base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from ....note import Note as Note
	from ....table import Table as Table

class TableHandlers(BaseHandlersCollection["Table", "Note"]):
	"""Table handlers."""

	def test(self, entity: "CommandEntity"):
		"""
		Command handler: **test**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		pass
