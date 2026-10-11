from typing import TYPE_CHECKING

from ...base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

	from .....core.base.note import BaseNote as BaseNote
	from .....core.base.table import BaseTable as BaseTable

class CommonNoteHandlers(BaseHandlersCollection["BaseTable", "BaseNote"]):
	"""Common note commands handlers."""

	def close(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **close**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		self.navigator.close()

	def view(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **view**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		viewer = self.interface.load_note_viewer()
		viewer.view()
