from typing import override

from otakudb.interfaces.cli.base.processor import BaseCLI

from .handlers import TableHandlers

class TableCLI(BaseCLI[TableHandlers]):
	"""Table CLI processor."""

	@override
	def _build_models(self):
		"""Build models and register handlers."""

		pass

	@override
	def _export_handlers(self) -> type[TableHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[TableHandlers]
		"""

		return TableHandlers
