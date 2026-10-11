from typing import TYPE_CHECKING, Literal

import questionary

from ...base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from pydantic import BaseModel as BaseModel

	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from .....core.base.note import BaseNote as BaseNote
	from .....core.base.table import BaseTable as BaseTable

class CommonTableHandlers(BaseHandlersCollection["BaseTable[BaseNote, BaseModel]", "BaseNote"]):
	"""Common table commands handlers."""

	def chid(self, entity: "CommandEntity"):
		"""
		Command handler: **chid**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		note_id: int = entity.get_position_value("NOTE_ID", expected_type = int, important = True)
		new_id: int = entity.get_position_value("NEW_ID", expected_type = int, important = True)

		mode: Literal["i", "o", "s"] | None = None

		if entity.check_flag("-i"): mode = "i"
		elif entity.check_flag("-o"): mode = "o"
		elif entity.check_flag("-s"): mode = "s"

		self.table.change_note_id(note_id, new_id, mode)

	def close(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **close**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		self.navigator.close()

	def column(self, entity: "CommandEntity"):
		"""
		Command handler: **column**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		column: str = entity.get_position_value("COLUMN", expected_type = str, important = True)
		table_interface_options = self.interface.options.table
		options = table_interface_options.columns.get(column)

		if not options:
			self.printer.error("Options for column not found.")
			return

		if entity.check_flag("-e"):
			options.is_enabled = True
		elif entity.check_flag("-d"):
			options.is_enabled = False
		elif entity.check_key("--max-width"):
			max_width: int | None = entity.get_key_value("--max-width", expected_type = int) or None
			options.max_width = max_width

		table_interface_options.save()

	def columns(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **columns**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		table_interface_options = self.interface.options.table
		columns_options = table_interface_options.columns

		enabled_columns = questionary.checkbox(
			message = "Choose displayed columns:",
			choices = tuple(questionary.Choice(name, checked = options.is_enabled) for name, options in columns_options.items()),
			instruction = "Navigate by <Up>, <Down> keys, switch by <Space>, save by <Enter>.",
		).ask()

		if enabled_columns is None:
			return

		for column in columns_options.keys():
			columns_options[column].is_enabled = column in enabled_columns

		table_interface_options.save()

	def delete(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **delete**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		self.driver.delete_table(self.navigator.current_box, self.table.name)
		self.navigator.close()

	def new(self, entity: "CommandEntity"):
		"""
		Command handler: **new**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		is_open: bool = entity.check_flag("-o")
		note = self.table.create_note()

		if is_open:
			self.navigator.open_note(note.id)
		else:
			self.printer.emit(f"Note #{note.id} created.")

	def open(self, entity: "CommandEntity"):
		"""
		Command handler: **open**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		note_id: int = entity.get_position_value("TARGET", expected_type = int, important = True)

		self.navigator.open_note(note_id)

	def rename(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **rename**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		name: str = entity.get_position_value("NAME", expected_type = str, important = True)
		self.table.rename(name)

	def search(self, entity: "CommandEntity"):
		"""
		Command handler: **search**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		query: str = entity.get_position_value("QUERY", expected_type = str, important = True)
		viewer = self.interface.load_table_viewer()
		viewer.view(search_query = query)

	def view(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **view**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		viewer = self.interface.load_table_viewer()
		viewer.view()
