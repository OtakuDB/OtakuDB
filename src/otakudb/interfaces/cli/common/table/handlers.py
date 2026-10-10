from typing import TYPE_CHECKING

from ...base.handlers import BaseHandlersCollection
from ...base.viewers.table import BaseTableViewer

if TYPE_CHECKING:
	from pydantic import BaseModel as BaseModel

	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from .....core.base.note import BaseNote as BaseNote
	from .....core.base.table import BaseTable as BaseTable

class CommonTableHandlers(BaseHandlersCollection["BaseTable[BaseNote, BaseModel]", "BaseNote"]):
	"""Common table commands handlers."""

	def close(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **close**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

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

	def view(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **view**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		BaseTableViewer(self._interface, self.table).view()
