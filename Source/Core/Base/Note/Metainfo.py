from Source.Core import Exceptions

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from . import BaseNote

class Metainfo:
	"""Оператор метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def fields(self) -> tuple[str]:
		"""Последовательность имён полей метаданных."""

		return tuple(self.__Data.keys())

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: dict):
		"""
		Оператор метаданных.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь метаданных.
		:type data: dict
		"""

		self.__Note = note
		self.__Data: dict[str, int | str] = dict() | data

		self.__MetainfoRules = self.__Note.table.manifest.metainfo_rules

	def __getitem__(self, field: str) -> int | float | str | None:
		"""
		Возвращает значение поля метаданных.

		:param field: Имя поля метаданных.
		:type field: str
		:return: Значение.
		:rtype: int | float | str | None
		"""

		return self.__Data.get(field)

	def remove_field(self, field: str):
		"""
		Удаляет поле метаданных.

		:param field: Имя поля.
		:type field: str
		:raises KeyError: Поле с указанным именем отсутствует.
		"""

		del self.__Data[field]
		self.__Note.save()

	def set_field_value(self, field: str, value: int | float | str):
		"""
		Задаёт значение поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param value: Значение.
		:type value: str
		:raises MetainfoBlocked: Прикрепление метаданных заброкировано фильтром манифеста.
		"""

		if not self.__MetainfoRules.check_metainfo_value(field, value): raise Exceptions.Note.MetainfoBlocked()
		
		self.__Data[field] = value
		self.__Data[field] = dict(sorted(self.__Data.items()))
		self.__Note.save()