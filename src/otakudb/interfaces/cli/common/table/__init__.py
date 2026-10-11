from typing import override

from dublib.cli.terminalyzer import ModelsGroup
from dublib.validators import ValidableTypes

from ...base.processor import BaseCLI
from .handlers import CommonTableHandlers

class CommonTableCLI(BaseCLI[CommonTableHandlers]):
	"""Common table CLI processor."""

	def _build_models_tui(self):
		"""Build TUI models and register handlers."""

		tui_group: ModelsGroup = self.create_models_group("TUI")

		model = tui_group.create_model("columns", "Runs columns visibility manager.")
		model.register_handler(self.handlers.columns)

	def _build_models_table(self):
		"""Build table models and register handlers."""

		table_group: ModelsGroup = self.create_models_group("Table")

		model = table_group.create_model("chid", "Change note ID.")
		position = model.create_position("NOTE_ID", description = "Exists note ID.", important = True)
		position.set_argument(ValidableTypes.UnsignedInteger)
		position = model.create_position("NEW_ID", description = "New note ID.", important = True)
		position.set_argument(ValidableTypes.UnsignedInteger)
		position = model.create_position("MODE", description = "Mode of ID changing. By default may insert only on free index.")
		position.add_flag("-o", description = "Overwtite exists note.")
		position.add_flag("-s", description = "Swipe with exists note.")
		position.add_flag("-i", description = "Insert to filled note place with offset. If index is free same as default.")
		model.register_handler(self.handlers.chid)

		model = table_group.create_model("close", "Close table.")
		model.register_handler(self.handlers.close)

		model = table_group.create_model("column", "Manage column viewing options.")
		position = model.create_position("COLUMN", "Column name (case insensitive).", important = True)
		position.set_argument(ValidableTypes.Alpha)
		position = model.create_position("OPERATION", "Management operation.", important = True)
		position.add_flag("-e", "Enable column.")
		position.add_flag("-d", "Disable column.")
		position.add_key("--max-width", value_type = ValidableTypes.UnsignedInteger, description = "Maximal width of column content. Put 0 to clear.")
		model.register_handler(self.handlers.column)

		model = table_group.create_model("delete", "Delete table.")
		model.register_handler(self.handlers.delete)

		model = table_group.create_model("new", "Create note.")
		model.base.add_flag("-o", description = "Open note after creation.")
		model.register_handler(self.handlers.new)

		model = table_group.create_model("open", "Open note.")
		position = model.create_position("TARGET", "Note ID.", important = True)
		position.set_argument(ValidableTypes.UnsignedInteger)
		model.register_handler(self.handlers.open)

		model = table_group.create_model("rename", "Rename table.")
		position = model.create_position("NAME", description = "New table name.")
		position.set_argument()
		model.register_handler(self.handlers.rename)

		model = table_group.create_model("search", "Search notes.")
		position = model.create_position("QUERY", description = "Search query.", important = True)
		position.set_argument()
		model.register_handler(self.handlers.search)

		model = table_group.create_model("view", "View table notes.")
		model.register_handler(self.handlers.view)

	@override
	def _build_models(self):
		"""Build models and register handlers."""

		self._build_models_table()
		self._build_models_tui()

	@override
	def _export_handlers(self) -> type[CommonTableHandlers]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[BaseTableHandlers]
		"""

		return CommonTableHandlers
