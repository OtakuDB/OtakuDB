from .Containers import Attachments, Common, Custom, InterfacesOptions
from .Metainfo import MetainfoRules

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from pathlib import Path
from typing import Any

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
	def type(self) -> str:
		"""Тип таблицы."""

		return self.__Type
	
	#==========================================================================================#
	# >>>>> СЕКЦИИ <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> Attachments:
		"""Параметры вложений"""

		return self.__Attachments

	@property
	def common(self) -> Common:
		"""Общие опции таблиц."""

		return self.__Common

	@property
	def custom(self) -> Custom:
		"""Дополнительные опции."""

		return self.__Custom

	@property
	def metainfo_rules(self) -> MetainfoRules:
		"""Опции метаданных."""

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

		self.__Directory = directory

		self.__ManifestPath = self.__Directory / "manifest.json"

		self.__Type = None
		self.__Common = Common(self)
		self.__MetainfoRules = MetainfoRules(self)
		self.__Attachments = Attachments(self)
		self.__Custom = Custom(self)
		self.__InterfacesOptions = InterfacesOptions(self) 

	def load(self) -> "Manifest":
		"""
		Загружает данные манифеста.

		:return: Манифест.
		:rtype: Manifest
		:raises FileNotFoundError: Выбрасывается при отсутствии файла манифеста.
		"""

		Data = ReadJSON(self.__ManifestPath)
		self.__Type = Data["type"]
		self.__Common.parse(Data.get("common") or dict())
		self.__MetainfoRules.parse(Data.get("metainfo_rules") or dict())
		self.__Attachments.parse(Data.get("attachments") or dict())
		self.__Custom.parse(Data.get("custom") or dict())
		self.__InterfacesOptions.parse(Data.get("interfaces_options") or dict())

		return self

	def save(self):
		"""Сохраняет манифест."""

		WriteJSON(self.__ManifestPath, self.to_dict(), atomic = True)

	def set_type(self, type: str):
		"""
		Задаёт тип таблицы.

		:param type: Тип таблицы.
		:type type: str
		"""

		self.__Type = type
		self.save()

	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление манифеста.

		:return: Словарное представление манифеста.
		:rtype: dict[str, Any]
		"""

		return {
			"type": self.__Type,
			"common": self.__Common.to_dict(),
			"metainfo_rules": self.__MetainfoRules.to_dict(),
			"attachments": self.__Attachments.to_dict(),
			"custom": self.__Custom.to_dict(),
			"interfaces_options": self.__InterfacesOptions.to_dict()
		}
