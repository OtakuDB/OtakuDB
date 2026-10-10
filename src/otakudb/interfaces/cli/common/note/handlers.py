from typing import TYPE_CHECKING

from ...base.handlers import BaseHandlersCollection

if TYPE_CHECKING:
	from dublib.cli.terminalyzer.parser.entities import CommandEntity

class CommonNoteHandlers(BaseHandlersCollection):
	"""Common note commands handlers."""

	def close(self, entity: "CommandEntity"):  # noqa: ARG002
		"""
		Command handler: **close**.

		:param entity: Command entity.
		:type entity: CommandEntity
		"""

		self.navigator.close()
