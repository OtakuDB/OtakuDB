from typing import override

from dublib.cli.terminalyzer import ModelsGroup
from dublib.validators import ValidableTypes

from ...base.processor import BaseCLI
from .handlers import CommonTableHandlers

class CommonTableCLI(BaseCLI[CommonTableHandlers]):
	"""Common table CLI processor."""

	@override
	def _build_models(self):
		"""Build models and register handlers."""

		common_group: ModelsGroup = self.create_models_group("Common")

		model = common_group.create_model("close", "Close table.")
		model.register_handler(self.handlers.close)

		model = common_group.create_model("new", "Create note.")
		model.base.add_flag("-o", description = "Open note after creation.")
		model.register_handler(self.handlers.new)

		model = common_group.create_model("open", "Open note.")
		position = model.create_position("TARGET", "Note ID.", important = True)
		position.set_argument(ValidableTypes.UnsignedInteger)
		model.register_handler(self.handlers.open)

	@override
	def _export_handlers(self) -> type[CommonTableHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[BaseTableHandlers]
		"""

		return CommonTableHandlers