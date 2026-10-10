from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from dublib.cli.terminalyzer import ModelsGroup

if TYPE_CHECKING:
	from ..shell import Interface
	from .handlers import BaseHandlersCollection

class BaseCLI[H: "BaseHandlersCollection"](ABC):
	"""Base CLI processor."""

	@property
	def groups(self) -> tuple[ModelsGroup, ...]:
		"""Commands models groups."""

		return tuple(self._groups.values())

	@property
	def handlers(self) -> H:
		"""Handlers collection."""

		return self._handlers

	@property
	def interface(self) -> "Interface":
		"""Interface processor."""

		return self._interface

	@abstractmethod
	def _build_models(self):
		"""Build models and register handlers."""

		pass
		
	@abstractmethod
	def _export_handlers(self) -> type[H]:
		"""
		Export handlers collection.

		:return: Handlers collection.
		:rtype: type[H]
		"""

		pass

	def _post_init(self):
		"""Execute after instance initialization."""

		pass

	def __init__(self, interface: "Interface"):
		"""
		Base CLI processor.

		:param interface: Interface processor.
		:type interface: Interface
		"""

		self._interface: Interface = interface

		self._groups: dict[str, ModelsGroup] = {}
		self._handlers: H = self._export_handlers()(self._interface)

		self._post_init()
		self._build_models()

	def create_models_group(self, name: str, supergroup: str | None = None) -> ModelsGroup:
		"""
		Create models group.

		:param name: Group name.
		:type name: str
		:param supergroup: Supergroup identifier to run commands by template: {supergroup} {command} {parameters}.
		:type supergroup: str | None
		:return: Commands models group.
		:rtype: ModelsGroup
		:raises KeyError: Group name unavailable.
		"""

		if name in self._groups:
			raise KeyError("Group already created.")

		if name in self._interface.reserved_groups:
			raise KeyError("Group name reserved.")

		group: ModelsGroup = ModelsGroup(name, supergroup)
		self._groups[name] = group

		return group	