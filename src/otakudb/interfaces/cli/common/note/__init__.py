from typing import override

from dublib.cli.terminalyzer import ModelsGroup

from ...base.processor import BaseCLI
from .handlers import CommonNoteHandlers

class CommonNoteCLI(BaseCLI[CommonNoteHandlers]):
	"""Common note CLI processor."""

	@override
	def _build_models(self):
		"""Build models and register handlers."""

		note_group: ModelsGroup = self.create_models_group("Note")

		model = note_group.create_model("close", "Close note.")
		model.register_handler(self.handlers.close)

		model = note_group.create_model("view", "View note.")
		model.register_handler(self.handlers.view)

	@override
	def _export_handlers(self) -> type[CommonNoteHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[CommonNoteHandlers]
		"""

		return CommonNoteHandlers
