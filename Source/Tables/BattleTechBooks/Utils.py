from Source.Core import Exceptions

from typing import TYPE_CHECKING

import dateparser

if TYPE_CHECKING:
	from Source.Core.Base.Table import BaseTable

class Chronolog:
	"""Сортировщик записей по дате публикации."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetTimestamp(self, publication_date: str | None) -> int:
		"""
		Возвращает UNIX Timestamp на основании переданного значения.

		:param publication_date: Дата публикации.
		:type publication_date: str | None
		:return: UNIX Timestamp.
		:rtype: int
		"""

		if not publication_date: return 0
		Datetime = dateparser.parse(publication_date, settings = self.__DateparserSettings)
		if not Datetime: return 0

		return int(Datetime.timestamp())

	def __SortByTimestamps(self, data: dict[int, int]) -> dict[int, int]:
		"""
		Сортирует ключи в словаре по значению.

		:param data: Словарь, в котором ключ – ID записи, значение – UNIX Timestamp даты публикации.
		:type data: dict[int, int]
		:return: Отсортированный словарь.
		:rtype: dict[int, int]
		"""

		return dict(sorted(data.items(), key = lambda Item: (Item[1] == 0, Item[1])))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BaseTable"):
		"""
		Сортировщик записей по дате публикации.

		:param table: Таблица.
		:type table: BaseTable
		"""

		self.__Table = table

		self.__DateparserSettings = {
			"PREFER_DAY_OF_MONTH": "first",
			"PREFER_MONTH_OF_YEAR": "first"
		}

	def apply(self, data: dict[int, int], sort: bool = True):
		"""
		Назначает записям новые ID, соответствующие их порядковому индексу после сортировки.

		:param data: Словарь, в котором ключ – ID записи, значение – UNIX Timestamp даты публикации.
		:type data: dict[int, int]
		:param sort: Указывает, необходимо ли произвести сортировку словаря по значениям.
		:type sort: bool
		"""

		if sort: data = self.__SortByTimestamps(data)
		Index = 0

		for OldID in data.keys():
			Index -= 1
			self.__Table.change_note_id(OldID, Index)

		Index = 0
		for OldID in data.keys():
			Index += 1
			self.__Table.change_note_id(Index * -1, Index)

	def calculate_timestamps(self) -> dict[int, int]:
		"""
		Вычисляет UNIX Timestamp для даты публикации записей.

		При отсутствии в дате дня или месяца, берутся наименьше значения (1-ое число, январь и т.д.). Для `None` UNIX Timestamp будет равен `0`.

		:return: Словарь, в котором ключ – ID записи, значение – UNIX Timestamp даты публикации. Ключи отсортированы по значению.
		:rtype: dict[int, int]
		"""

		Timestamps = dict()

		for CurrentNote in self.__Table.notes:
			PublicationDate = None
			
			try: PublicationDate = CurrentNote.metainfo.get_field_value("publication_date")
			except Exceptions.Note.MetainfoFieldMissing: pass
			
			Timestamps[CurrentNote.id] = self.__GetTimestamp(PublicationDate)
		
		return self.__SortByTimestamps(Timestamps)
