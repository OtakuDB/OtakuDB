from pathlib import Path

from dublib.functions.filesystem import json

from .sections.attachments import AttachmentsSection
from .sections.common import CommonSection
from .sections.connections import ConnectionsSection
from .sections.custom import CustomSection
from .sections.interfaces_options import InterfacesOptions
from .sections.metainfo_rules import MetainfoRules

class Manifest:
	"""Манифест таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def directory(self) -> Path:
		"""Путь к директории таблицы."""

		return self.__directory

	@property
	def table_type(self) -> str | None:
		"""Тип таблицы."""

		return self.__table_type
	
	#==========================================================================================#
	# >>>>> СЕКЦИИ <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> AttachmentsSection:
		"""Параметры вложений"""

		return self.__attachments

	@property
	def common(self) -> CommonSection:
		"""Общие опции таблиц."""

		return self.__common

	@property
	def connections(self) -> ConnectionsSection:
		"""Параметры соединений."""

		return self.__connections

	@property
	def custom(self) -> CustomSection:
		"""Дополнительные опции."""

		return self.__custom

	@property
	def metainfo_rules(self) -> MetainfoRules:
		"""Правила метаданных."""

		return self.__metainfo_rules

	@property
	def interfaces_options(self) -> InterfacesOptions:
		"""Опции интерфейсов."""

		return self.__interfaces_options

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, directory: Path):
		"""
		Манифест таблицы.

		:param directory: Полный путь к директории таблицы.
		:type directory: PathLike
		"""

		self.set_directory(directory)

		self.__manifest_path = self.__directory / "manifest.json"
		self.__table_type: str | None = None

		self.__attachments = AttachmentsSection(self)
		self.__common = CommonSection(self)
		self.__custom = CustomSection(self)
		self.__connections = ConnectionsSection(self)
		self.__metainfo_rules = MetainfoRules(self)
		self.__interfaces_options = InterfacesOptions(self) 

	def load(self) -> "Manifest":
		"""
		Читает и парсит манифест.

		:return: Манифест.
		:rtype: Manifest
		:raises FileNotFoundError: Выбрасывается при отсутствии файла манифеста.
		"""

		data: dict = json.read(self.__manifest_path)
		self.__table_type = data["type"]

		self.__attachments.parse(data.get("attachments", {}))
		self.__common.parse(data.get("common", {}))
		self.__connections.parse(data.get("connections", {}))
		self.__custom.parse(data.get("custom", {}))
		self.__metainfo_rules.parse(data.get("metainfo_rules", {}))
		self.__interfaces_options.parse(data.get("interfaces_options", {}))

		return self

	def save(self):
		"""Сохраняет манифест."""

		json.write(self.__manifest_path, self.to_dict(), atomic = True)

	def set_directory(self, full_path: Path):
		"""
		Задаёт полный путь к директории таблицы.

		:param full_path: Полный путь к директории таблицы.
		:type full_path: Path
		:raises FileNotFoundError: Директория таблицы не найдена.
		"""

		if not full_path.exists():
			raise FileNotFoundError(full_path)

		self.__directory = full_path

	def set_type(self, table_type: str):
		"""
		Задаёт тип таблицы.

		:param table_type: Тип таблицы.
		:type table_type: str
		"""

		self.__type = table_type

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"type": self.__type,
			"attachments": self.__attachments.to_dict(),
			"common": self.__common.to_dict(),
			"connections": self.__connections.to_dict(),
			"custom": self.__custom.to_dict(),
			"metainfo_rules": self.__metainfo_rules.to_dict(),
			"interfaces_options": self.__interfaces_options.to_dict()
		}
