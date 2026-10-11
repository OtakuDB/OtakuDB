from typing import TYPE_CHECKING, Literal

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
