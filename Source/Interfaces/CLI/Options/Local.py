from Source.Core.Base.Manifest.Containers import InterfacesOptions
from Source.Core.Enums import Interfaces

from typing import Any

#==========================================================================================#
# >>>>> ПАРАМЕТРЫ КОЛОНОК <<<<< #
#==========================================================================================#

class ColumnOptions:
	"""Параметры колонки."""

	pass

class ColumnsOptions:
	"""Параметры колонок таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def names(self) -> tuple[str]:
		"""Названия колонок."""

		return tuple(self.__Data.keys())

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, interface_options: "TableInterfaceOptions", data: dict[str, bool]):
		"""
		Параметры колонок таблицы.

		:param interface_options: Параметры интерфейса таблицы.
		:type interface_options: TableInterfaceOptions
		:param data: Словарь, где ключи – названия колонок, а значения – статус отображения.
		:type data: dict[str, bool]
		:raises ValueError: Отсутствует обязательная колонка.
		"""

		self.__InterfaceOptions = interface_options
		self.__Data = data
		
		for ColumnName in ("ID", "Name"):
			if ColumnName not in self.__Data: raise ValueError(f"Important column \"{ColumnName}\" missing.")

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

		self.__Data.set_options(Interfaces.CLI, self.__Options)
