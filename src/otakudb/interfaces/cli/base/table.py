from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from .processor import BaseCLI

if TYPE_CHECKING:
	from dublib.cli.terminalyzer import ModelsGroup

	from ....core.base.table import BaseTable
	from .handlers import BaseHandlersCollection

class BaseTableCLI[T: "BaseTable", H: "BaseHandlersCollection"](BaseCLI[H], ABC):

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def table(self) -> T:
		"""Table."""

		return self.handlers.table

	#==========================================================================================#
	# >>>>> PROTECTED METHODS <<<<< #
	#==========================================================================================#

	def _build_models(self):
		"""Build models and register handlers."""

		table_type: str = self.table.manifest.table_type
		group: ModelsGroup = self._create_models_group(f"Table ({table_type})")
		self._build_table_models(group)

	#==========================================================================================#
	# >>>>> OVERRIDABLE METHODS <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _build_table_models(self, group: "ModelsGroup"):
		"""Build table models and register handlers."""

		pass

	@abstractmethod
	def _export_handlers(self) -> type[H]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[H]
		"""

		pass
