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

		return self.__Directory

	@property
	def type(self) -> str | None:
		"""Тип таблицы."""

		return self.__Type
	
	#==========================================================================================#
	# >>>>> СЕКЦИИ <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> AttachmentsSection:
		"""Параметры вложений"""

		return self.__Attachments

	@property
	def common(self) -> CommonSection:
		"""Общие опции таблиц."""

		return self.__Common

	@property
	def connections(self) -> ConnectionsSection:
		"""Параметры соединений."""

		return self.__Connections

	@property
	def custom(self) -> CustomSection:
		"""Дополнительные опции."""

		return self.__Custom

	@property
	def metainfo_rules(self) -> MetainfoRules:
		"""Правила метаданных."""

		return self.__MetainfoRules

	@property
	def interfaces_options(self) -> InterfacesOptions:
		"""Опции интерфейсов."""

		return self.__InterfacesOptions

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

		self.__ManifestPath = self.__Directory / "manifest.json"
		self.__Type: str | None = None

		self.__Attachments = AttachmentsSection(self)
		self.__Common = CommonSection(self)
		self.__Custom = CustomSection(self)
		self.__Connections = ConnectionsSection(self)
		self.__MetainfoRules = MetainfoRules(self)
		self.__InterfacesOptions = InterfacesOptions(self) 

	def load(self) -> "Manifest":
		"""
		Читает и парсит манифест.

		:return: Манифест.
		:rtype: Manifest
		:raises FileNotFoundError: Выбрасывается при отсутствии файла манифеста.
		"""

		Data = json.read(self.__ManifestPath)
		self.__Type = Data["type"]

		self.__Attachments.parse(Data.get("attachments") or {})
		self.__Common.parse(Data.get("common") or {})
		self.__Connections.parse(Data.get("connections") or {})
		self.__Custom.parse(Data.get("custom") or {})
		self.__MetainfoRules.parse(Data.get("metainfo_rules") or {})
		self.__InterfacesOptions.parse(Data.get("interfaces_options") or {})

		return self

	def save(self):
		"""Сохраняет манифест."""

		json.write(self.__ManifestPath, self.to_dict(), atomic = True)

	def set_directory(self, directory: Path):
		"""
		Задаёт полный путь к директории таблицы.

		:param directory: _description_
		:type directory: Path
		:raises FileNotFoundError: Директория таблицы не найдена.
		"""

		if not directory.exists():
			raise FileNotFoundError(directory)

		self.__Directory = directory

	def set_type(self, table_type: str, save: bool = True):
		"""
		Задаёт тип таблицы.

		:param table_type: Тип таблицы.
		:type table_type: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		"""

		self.__Type = table_type
		if save: self.save()

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"type": self.__Type,
			"attachments": self.__Attachments.to_dict(),
			"common": self.__Common.to_dict(),
			"connections": self.__Connections.to_dict(),
			"custom": self.__Custom.to_dict(),
			"metainfo_rules": self.__MetainfoRules.to_dict(),
			"interfaces_options": self.__InterfacesOptions.to_dict()
		}
