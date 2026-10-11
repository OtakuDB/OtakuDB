from typing import TYPE_CHECKING, override

from otakudb.interfaces.cli.base.table import BaseTableCLI

from .handlers import TableHandlers

if TYPE_CHECKING:
	from dublib.cli.terminalyzer import ModelsGroup

	from ....table import Table as Table

class TableCLI(BaseTableCLI["Table", TableHandlers]):
	"""Table CLI processor."""

	@override
	def _build_table_models(self, group: "ModelsGroup"):
		"""Build table models and register handlers."""

		pass

	@override
	def _export_handlers(self) -> type[TableHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[TableHandlers]
		"""

		return TableHandlers
