from .Structs import ModuleData

from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from typing import Any, Literal

#==========================================================================================#
# >>>>> МАНИФЕСТ <<<<< #
#==========================================================================================#

class ColumnsOptions:
	"""Опции отображения колонок таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def important_columns(self) -> tuple[str]:
		"""Список обязательных колонок."""

		return ("ID", "Name")

	@property
	def is_available(self) -> bool:
		"""Указывает, доступны ли настройки отображения колонок таблицы."""

		IsAvailable = False
		if len(list(self.__Data.keys())): IsAvailable = True

		return IsAvailable

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Опции отображения колонок таблицы.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data: dict[str, bool] = dict()
		for Column in self.important_columns: self.__Data[Column] = True

	def __getitem__(self, column: str) -> bool | None:
		"""
		Возвращает статус отображения колонки.

		:param column: Название колонки в любом регистре.
		:type column: Manifest
		"""

		return self.__Data.get(column)

	def check_column(self, column: str) -> bool:
		"""
		Проверяет, описано ли правило для колонки.

		:param column: Название колонки. Проверка нечувствительна к регистру.
		:type column: str
		:return: Состояние присутствия колонки в списке.
		:rtype: bool
		"""

		return column in self.__Data
	
	def edit_column_status(self, column: str, status: bool):
		"""
		Задаёт статус отображения для колонки.

		:param column: Название колонки.
		:type column: str
		:param status: Статус отображения.
		:type status: bool
		:raises KeyError: Выбрасывается при отсутствии колонки.
		"""

		if column not in self.__Data.keys(): raise KeyError(column)
		self.__Data[column] = status
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = data
		for Column in self.important_columns: self.__Data[Column] = True

	def set_columns(self, columns: tuple[str]):
		"""
		Задаёт последовательность колонок.

		:param tuple: Последовательность колонок.
		:type tuple: tuple[str]
		"""

		Buffer: dict[str, bool] = dict()

		for Column in columns:
			Value = self.__getitem__(Column)
			if Value == None: Value = True
			Buffer[Column] = True

		for Column in self.important_columns:
			if Column not in Buffer: Buffer[Column] = True

		self.__Data = Buffer
		self.__Manifest.save()

	def to_dict(self) -> dict:
		"""Возвращает словарь опций отображения."""

		return self.__Data.copy()

class CommonOptions:
	"""Общие опции таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_attachments_enabled(self) -> bool:
		"""Указывает, разрешено ли прикреплять файлы к записям."""

		return self.__Data["attachments"]

	@property
	def recycle_id(self) -> bool:
		"""Указывает, необходимо ли занимать освободившиеся ID."""

		return self.__Data["recycle_id"]

	@property
	def slots(self) -> dict[str, str | None]:
		"""Определения слотов, предназначенных для особого взаимодействия."""

		return self.__Data["slots"].copy()

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""Общие опции таблицы."""

		self.__Manifest = manifest

		self.__Data = {
			"recycle_id": True,
			"attachments": False,
			"slots": {}
		}

	def switch_recycle_id(self, status: bool):
		"""
		Переключает состояние утилизации свободных ID.

		:param status: Состояние утилизации свободных ID.
		:type status: bool
		"""

		self.__Data["recycle_id"] = status
		self.__Manifest.save()

	def enable_attachments(self, status: bool):
		"""
		Переключает использование вложений.

		:param status: Состояние использования вложений.
		:type status: bool
		"""

		self.__Data["attachments"] = status
		self.__Manifest.save()

	def add_slot(self, slot: str, description: str | None):
		"""
		Резервирует слот вложений для особого взаимодействия.

		:param slot: Название слота.
		:type slot: str
		:param description: Описание слота.
		:type description: str | None
		"""

		self.__Data["slots"][slot] = description
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def remove_slot(self, slot: str):
		"""
		Удаляет слот вложений.

		:param slot: Название слота.
		:type slot: str
		"""

		try: 
			del self.__Data["slots"][slot]
			self.__Manifest.save()
		except KeyError: pass

	def to_dict(self) -> dict[str, bool | dict]:
		"""
		Возвращает словарное представление общих опций.

		:return: Словарное представление общих опций.
		:rtype: dict[str, bool | dict]
		"""

		return self.__Data.copy()

class MetainfoRules:
	"""Правила метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def fields(self) -> tuple[str]:
		"""Список названий полей с правилами."""

		return tuple(self.__Data.keys())
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Правила метаданных.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data = dict()

	def __getitem__(self, key: str) -> list | tuple | None:
		"""
		Возвращает правило.

		:param key: Ключ правила.
		:type key: str
		:return: Правило.
		:rtype: Any
		"""

		return self.__Data[key]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def remove_rule(self, name: str):
		"""
		Удаляет правило проверки поля метаданных.

		:param name: Название поля метаданных.
		:type name: str
		"""

		try: 
			del self.__Data[name]
			self.__Manifest.save()
		except KeyError: pass

	def set_rule(self, name: str, rule: list | tuple | None):
		"""
		Добавляет правило проверки поля метаданных.

		:param name: Название поля метаданных.
		:type name: str
		:param rule: Правило проверки. `None` – любое значение, `list | tuple` – одно и зуказанных значений. 
		:type rule: list | tuple | None
		"""

		self.__Data[name] = rule
		self.__Manifest.save()

class ViewerOptions:
	"""Опции просмоторщика записей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def autoclear(self) -> bool | None:
		"""Указывает, следует ли очищать консоль перед выводом списков и просмотром содержимого."""

		Option = None
		if "autoclear" in self.__Data.keys(): Option = self.__Data["autoclear"]

		return Option
	
	@property
	def colorize(self) -> bool | None:
		"""Указывает, следует ли окрашивать элементы консольного интерфейса."""

		Option = None
		if "colorize" in self.__Data.keys(): Option = self.__Data["colorize"]

		return Option

	@property
	def columns(self) -> ColumnsOptions:
		"""Опции отображения колонок таблицы."""

		return self.__Columns

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Опции просмоторщика записей.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data = {
			"autoclear": True,
			"colorize": True,
			"columns": {}
		}

		self.__Columns = ColumnsOptions(manifest)
		self.__Columns.parse(self.__Data["columns"])

	def enable_autoclear(self, status: bool):
		"""
		Переключает режим автоочистки консоли перед отображением объектов.

		:param status: Состояние автоочистки.
		:type status: bool
		"""

		self.__Data["autoclear"] = status
		self.__Manifest.save()

	def enable_colorize(self, status: bool):
		"""
		Переключает режим раскраски вывода.

		:param status: Состояние раскраски вывода.
		:type status: bool
		"""

		self.__Data["colorize"] = status
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data
		self.__Columns.parse(self.__Data["columns"])

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление опций.

		:return: Словарное представление опций.
		:rtype: dict
		"""

		Data = self.__Data.copy()
		Data["columns"] = self.__Columns.to_dict()

		return Data

class Manifest:
	"""Манифест таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def common(self) -> CommonOptions:
		"""Общие опции таблиц."""

		return self.__Common

	@property
	def custom(self) -> dict:
		"""Дополнительные опции."""

		return self.__Custom.copy()

	@property
	def metainfo_rules(self) -> MetainfoRules:
		"""Опции метаданных."""

		return self.__MetainfoRules

	@property
	def modules(self) -> tuple[ModuleData]:
		"""Список модулей таблицы."""

		return self.__Modules
	
	@property
	def path(self) -> str:
		"""Путь к директории таблицы."""

		return self.__Path

	@property
	def type(self) -> str:
		"""Тип таблицы."""

		return self.__Type
	
	@property
	def viewer(self) -> ViewerOptions:
		"""Опции просмоторщика записей."""

		return self.__ViewerOptions

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseModules(self, modules_data: list[dict] | None) -> list[ModuleData]:
		"""
		Парсит данные модулей в структуры.

		:param modules_data: Данные модулей.
		:type modules_data: list[dict]
		:return: Структуры данных модулей.
		:rtype: list[ModuleData]
		"""

		if not modules_data: return tuple()

		Modules = list()
		for Module in modules_data: Modules.append(ModuleData(self, Module["name"], Module["type"]))

		return Modules

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str):
		"""
		Манифест таблицы.

		:param path: Путь к директории таблицы.
		:type path: str
		"""

		self.__Path = path

		self.__Object = None
		self.__Type = None
		self.__Common = CommonOptions(self)
		self.__MetainfoRules = MetainfoRules(self)
		self.__ViewerOptions = ViewerOptions(self) 
		self.__Custom = dict()
		self.__Modules = list()

		self.__SuppressSaving = False

	def add_module(self, module: ModuleData):
		"""
		Добавялет данные модуля в манифест.

		:param module: Данные модуля.
		:type module: ModuleData
		"""

		self.__Modules.append(module)
		self.save()

	def load(self):
		"""
		Загружает данные манифеста.
		
		:return: Манифест.
		:rtype: Manifest
		"""

		Data = ReadJSON(f"{self.__Path}/manifest.json")
		self.__Object = Data["object"]
		self.__Type = Data["type"]
		self.__Common.parse(Data.get("common") or dict())
		self.__MetainfoRules.parse(Data.get("metainfo_rules") or dict())
		self.__ViewerOptions.parse(Data.get("viewer") or dict())
		self.__Custom = Data.get("custom") or dict()
		self.__Modules = self.__ParseModules(Data.get("modules") or dict())

		return self

	def save(self) -> ExecutionStatus:
		"""
		Сохраняет манифест.

		:return: Статус выполнения.
		:rtype: ExecutionStatus
		"""

		Status = ExecutionStatus()

		try:
			if not self.__SuppressSaving: WriteJSON(f"{self.__Path}/manifest.json", self.to_dict())
			
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def suppress_saving(self, status: bool):
		"""
		Переключает подавление сохранения.

		:param status: Статус подавление сохранения.
		:type status: bool
		"""

		self.__SuppressSaving = status

	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление манифеста.

		:return: Словарное представление манифеста.
		:rtype: dict[str, Any]
		"""

		Data = {
			"object": self.__Object,
			"type": self.__Type,
			"common": self.__Common.to_dict(),
			"metainfo_rules": {},
			"viewer": {
				"autoclear": False,
				"colorize": True,
				"columns": {}
			},
			"custom": self.__Custom.copy()
		}

		ModulesBuffer = list()
		for Module in self.__Modules: ModulesBuffer.append({"name": Module.name, "type": Module.type, "is_active": Module.is_active})
		if ModulesBuffer: Data["modules"] = tuple(ModulesBuffer)

		return Data

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ЗАПОЛНЕНИЯ МАНИФЕСТА <<<<< #
	#==========================================================================================#

	def set_object(self, object: Literal["module", "table"]):
		"""
		Задаёт тип объекта.

		:param type: Тип описываемого манифестом объекта.
		:type type: Literal["module", "table"]
		"""

		if object not in ("module", "table"): raise ValueError(f"Incorrect object: \"{object}\".")
		self.__Object = object

	def set_type(self, type: str):
		"""
		Задаёт название типа таблицы.

		:param type: Название типа таблицы. Для модуля используется шаблон `{TABLE}:{MODULE}`.
		:type type: str
		"""

		self.__Type = type