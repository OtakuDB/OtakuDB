from Source.Core.Base.Manifest.Containers import InterfacesOptions
from Source.Core.Enums import Interfaces

from typing import Any

#==========================================================================================#
# >>>>> ПАРАМЕТРЫ КОЛОНОК <<<<< #
#==========================================================================================#

class ColumnOptions:
	"""Параметры колонки."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_enabled(self) -> bool:
		"""Состояние: включено ли отображение колонки."""

		return self.__Data["enabled"]

	@property
	def max_width(self) -> int | None:
		"""Максимальная длина колонки в символах. При `None` длина не ограничена."""

		return self.__Data.get("max_width")

	@property
	def name(self) -> str:
		"""Название колонки."""

		return self.__Name

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, columns_options: "ColumnsOptions", name: str, data: dict[str, bool | int | None]):
		"""
		Параметры колонки таблицы.

		:param columns_options: Параметры колонок таблицы.
		:type columns_options: TableInterfaceOptions
		:param name: Название колонки.
		:type name: str
		:param data: Словарь параметров.
		:type data: dict[str, bool | int | None]
		"""

		self.__ColumnsOptions = columns_options
		self.__Name = name
		self.__Data = {
			"enabled": True,
			"max_width": None
		} | data

	def set_max_width(self, max_width: int | None):
		"""
		Задаёт максимальную длину колонки.

		:param max_width: Максимальная длина колонки в символах. При `None` длина не ограничена.
		:type max_width: int | None
		"""

		self.__Data["max_width"] = max_width
		self.save()
		
	def set_status(self, status: bool):
		"""
		Задаёт статус отображения колонки.

		:param status: Статус отображения колонки.
		:type status: bool
		"""

		self.__Data["enabled"] = status
		self.save()

	def save(self):
		"""Сохраняет статус отображения колонки."""

		self.__ColumnsOptions.save()

	def to_dict(self) -> dict[str, bool | int | None]:
		"""
		Возвращает словарное представление параметров колонки.

		:return: Словарное представление параметров колонки.
		:rtype: dict[str, bool | int | None]
		"""

		return self.__Data.copy()

class ColumnsOptions:
	"""Параметры колонок таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def names(self) -> tuple[str]:
		"""Названия колонок."""

		return tuple(self.__Data.keys())
	
	@property
	def options(self) -> tuple[ColumnOptions]:
		"""Последовательность параметров колонок."""

		return tuple(self.__Data.values())

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, interface_options: "TableInterfaceOptions", data: dict[str, dict]):
		"""
		Параметры колонок таблицы.

		:param interface_options: Параметры интерфейса таблицы.
		:type interface_options: TableInterfaceOptions
		:param data: Словарь, где ключи – названия колонок, а значения – параметры отображения.
		:type data: dict[str, dict]
		:raises ValueError: Отсутствует обязательная колонка.
		"""

		self.__InterfaceOptions = interface_options
		self.__Data = {Name: ColumnOptions(self, Name, Data) for Name, Data in data.items()}
		
		for ColumnName in ("ID", "Name"):
			if ColumnName not in self.__Data: raise ValueError(f"Important column \"{ColumnName}\" missing.")

	def get_column_options(self, column_name: str) -> ColumnOptions:
		"""
		Возвращает параметры колонки.

		:param column_name: Имя колонки.
		:type column_name: str
		:return: ColumnOptions
		:rtype: ColumnData
		:raises KeyError: Параметры для колонки не найдены.
		"""

		return self.__Data[column_name]
	
	def save(self):
		"""Сохраняет параметры колонок."""

		self.__InterfaceOptions.save()

	def to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление параметров колонок.

		:return: Словарное представление параметров колонок.
		:rtype: dict[str, dict]
		"""

		return {Name: Data.to_dict() for Name, Data in self.__Data.items()}

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class TableInterfaceOptions:
	"""Параметры интерфейса таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def columns(self) -> ColumnsOptions:
		"""Параметры колонок таблицы."""

		return self.__Columns

	@property
	def custom(self) -> dict[str, Any]:
		"""Кастомные опции интерфейса таблицы."""

		return self.__Options.get("custom") or dict()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, data: InterfacesOptions):
		"""
		Параметры интерфейса таблицы.

		:param data: Опции интерфейсов.
		:type data: InterfacesOptions
		"""

		self.__Data = data
		
		self.__Options = data.get_options(Interfaces.CLI)
		self.__Columns = ColumnsOptions(self, self.__Options.get("columns") or dict())

	def save(self):
		"""Сохраняет параметры интерфейса таблицы."""

		self.__Options["columns"] = self.__Columns.to_dict()
		self.__Data.set_options(Interfaces.CLI, self.__Options)
