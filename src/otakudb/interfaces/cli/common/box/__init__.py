from typing import override

from dublib.cli.terminalyzer import ModelsGroup
from dublib.validators import ValidableTypes

from ...base.processor import BaseCLI
from .handlers import BoxHandlers

class BoxCLI(BaseCLI[BoxHandlers]):
	"""Box CLI processor."""

	@override
	def _build_models(self):
		"""Build models and register handlers."""

		box_group: ModelsGroup = self._create_models_group("Box")

		model = box_group.create_model("go", "Navigate by virtual path.")
		position = model.create_position("PATH", "Virtual path.", important = True)
		position.set_argument(ValidableTypes.Path)
		model.register_handler(self.handlers.go)

		model = box_group.create_model("mkdir", "Create box.")
		position = model.create_position("NAME", "Box name.", important = True)
		position.set_argument()
		model.base.add_flag("-o", description = "Open box after creation.")
		model.register_handler(self.handlers.mkdir)

		model = box_group.create_model("new", "Create table.")
		position = model.create_position("TYPE", "Table type.", important = True)
		position.set_argument()
		position = model.create_position("NAME", "Table name. Type used instead if name missing.")
		position.set_argument()
		model.base.add_flag("-o", description = "Open table after creation.")
		model.register_handler(self.handlers.new)

		model = box_group.create_model("ls", "List box content.")
		model.register_handler(self.handlers.ls)

		model = box_group.create_model("rmdir", "Delete box. By default only for empty boxes.")
		position = model.create_position("NAME", "Box name.", important = True)
		position.set_argument()
		model.base.add_flag("-p", description = "Purge all data in box if exists.")
		model.register_handler(self.handlers.rmdir)

		model = box_group.create_model("types", "Print available tables types.")
		model.register_handler(self.handlers.types)

	@override
	def _export_handlers(self) -> type[BoxHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[BoxHandlers]
		"""

		return BoxHandlers
