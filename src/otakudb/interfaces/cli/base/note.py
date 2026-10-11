from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .processor import BaseCLI

if TYPE_CHECKING:
	from dublib.cli.terminalyzer import ModelsGroup

	from ....core.base.note import BaseNote
	from ....core.base.table import BaseTable
	from .handlers import BaseHandlersCollection

class BaseNoteCLI[T: "BaseTable", N: "BaseNote", H: "BaseHandlersCollection"](BaseCLI[H], ABC):

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def note(self) -> N:
		"""Note."""

		return self.handlers.note

	@property
	def table(self) -> T:
		"""Table."""

		return self.handlers.table

	#==========================================================================================#
	# >>>>> PROTECTED METHODS <<<<< #
	#==========================================================================================#

	def _build_models(self):
		"""Build models and register handlers."""

		group: ModelsGroup = self._create_models_group(f"Note ({self.table.manifest.table_type})")
		self._build_note_models(group)

	#==========================================================================================#
	# >>>>> OVERRIDABLE METHODS <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _build_note_models(self, group: "ModelsGroup"):
		"""Build note models and register handlers."""

		pass

	@abstractmethod
	def _export_handlers(self) -> type[H]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[H]
		"""

		pass
