from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Self

from pydantic import BaseModel, TypeAdapter

from dublib.functions.filesystem import json

from .sections.attachments import AttachmentsSection
from .sections.common import CommonSection
from .sections.connections import ConnectionsSection
from .sections.interfaces_options import InterfacesOptions
from .sections.metainfo_rules import MetainfoRules

if TYPE_CHECKING:
	from pathlib import Path

class BaseManifest[C: "BaseModel"](ABC):
	"""Base manifest."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def directory(self) -> "Path":
		"""Full path to table directory."""

		return self._directory

	@property
	def is_exists(self) -> bool:
		"""Condition: is manifest file exists."""

		return self._manifest_path.exists()

	@property
	def table_type(self) -> str:
		"""Table type."""

		return self._table_type

	#==========================================================================================#
	# >>>>> SECTIONS <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> AttachmentsSection:
		"""Attachments options."""

		return self._attachments

	@property
	def common(self) -> CommonSection:
		"""Common options."""

		return self._common

	@property
	def connections(self) -> ConnectionsSection:
		"""Connections options."""

		return self._connections

	@property
	def custom(self) -> C:
		"""Custom settings."""

		return self._custom

	@property
	def metainfo_rules(self) -> MetainfoRules:
		"""Metainfo rules."""

		return self._metainfo_rules

	@property
	def interfaces_options(self) -> InterfacesOptions:
		"""Interfaces options."""

		return self._interfaces_options

	#==========================================================================================#
	# >>>>> PROTECTED METHODS <<<<< #
	#==========================================================================================#

	def _get_table_type(self) -> str:
		"""
		Get table type.

		:return: Table type.
		:rtype: str
		"""

		current_module: str = self.__class__.__module__
		parts: list[str] = current_module.split(".")

		return parts[-2]

	#==========================================================================================#
	# >>>>> OVERRIDABLE METHODS <<<<< #
	#==========================================================================================#

	@abstractmethod
	def _edit(self):
		"""Edit base manifest to generate table manifest."""

		pass

	@abstractmethod
	def _export_custom_settings_model(self) -> type[C]:
		"""
		Export custom settings typing [pydantic](https://github.com/pydantic/PYDANTIC) model.

		:return: Custom settings typing model.
		:rtype: type[BaseModel]
		"""

		pass

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, directory: "Path"):
		"""
		Base manifest.

		:param directory: Full path to table directory.
		:type directory: PathLike
		"""

		self._directory: Path = directory

		self._manifest_path: Path = self._directory / "manifest.json"
		self._table_type: str = self._get_table_type()

		self._attachments = AttachmentsSection(self)
		self._common = CommonSection(self)
		self._connections = ConnectionsSection(self)
		self._metainfo_rules = MetainfoRules(self)
		self._interfaces_options = InterfacesOptions(self)

		self._custom_settings_model: type[C] = self._export_custom_settings_model()
		self._custom_adapter: TypeAdapter[C] = TypeAdapter(self._custom_settings_model)
		self._custom: C = self._custom_settings_model()

	def change_directory(self, directory: "Path"):
		"""
		Set full path to table directory.

		:param directory: Full path to table directory.
		:type directory: Path
		:raises FileNotFoundError: Directory not found.
		"""

		if not directory.exists():
			raise FileNotFoundError(directory)

		self.__directory = directory

	def load(self) -> Self:
		"""
		Load manifest from file.

		:return: Manifest..
		:rtype: Manifest
		:raises FileNotFoundError: Manifest file not found.
		"""

		data: dict = json.read(self._manifest_path)
		self.parse(data)

		return self

	def parse(self, data: dict):
		"""
		Parse manifest data.

		:param data: Manifest data dictionary.
		:type data: dict
		"""

		self._attachments.parse(data.get("attachments", {}))
		self._common.parse(data.get("common", {}))
		self._connections.parse(data.get("connections", {}))
		self._metainfo_rules.parse(data.get("metainfo_rules", {}))
		self._interfaces_options.parse(data.get("interfaces_options", {}))

		self._custom = self._custom_adapter.validate_python(data.get("custom", {}))

	def save(self):
		"""Save manifest."""

		json.write(self._manifest_path, self.to_dict(), atomic = True)

	def to_dict(self) -> dict:
		"""
		Generate dictionary representation of the instance.

		:return: Dictionary representation of the instance.
		:rtype: dict
		"""

		return {
			"type": self._table_type,
			"attachments": self._attachments.to_dict(),
			"common": self._common.to_dict(),
			"connections": self._connections.to_dict(),
			"custom": self._custom_adapter.dump_python(self._custom, mode = "json"),
			"metainfo_rules": self._metainfo_rules.to_dict(),
			"interfaces_options": self._interfaces_options.to_dict(),
		}
