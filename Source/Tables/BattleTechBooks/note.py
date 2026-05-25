from .Structs import CollectionStatusses, Era, Statusses, Types

from Source.Core.Base.Note import BaseNote

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
	from .table import Table

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Note(BaseNote):
	"""Запись о прочтении произведения по вселенной BattleTech."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> tuple[str]:
		"""Последовательность альтернативных названий."""

		return tuple(self._Data["another_names"])

	@property
	def collection_status(self) -> CollectionStatusses | None:
		"""Статус коллекционирования."""

		Status = self._Data.get("collection_status")
		if Status: return CollectionStatusses(Status)

	@property
	def era(self) -> Era | None:
		"""Эра BattleTech."""

		if self._Data.get("era") == None: return
		self._Table: "Table"
		
		for CurrentEra in self._Table.eras:
			if CurrentEra.index == self._Data["era"]: return CurrentEra

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self._Data.get("estimation")

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Data.get("localized_name")

	@property
	def status(self) -> Statusses | None:
		"""Статус прочтения."""

		Status = self._Data.get("status")
		if Status: return Statusses(Status)

	@property
	def type(self) -> Types | None:
		"""Тип произведения."""

		return Types(self._Data["type"])

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyNote(self) -> dict[str, Any]:
		"""
		Возвращает пустую структуру записи.

		Поля _name_, _metainfo_, _attachments_ будут добавлены автоматически, но их можно указать для определения порядка.

		:return: Пустая структура записи.
		:rtype: dict[str, Any]
		"""

		return {
			"localized_name": None,
			"another_names": [],
			"type": "novel",
			"era": None,
			"estimation": None,
			"comment": None,
			"link": None,
			"status": None,
			"collection_status": None
		}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str):
		"""
		Добавляет альтернативное название.

		:param another_name: Альтернативное название.
		:type another_name: str
		"""

		if another_name not in self._Data["another_names"]:
			self._Data["another_names"].append(another_name)
			self.save()

	def estimate(self, estimation: int | None):
		"""
		Выставляет оценку тайтла.

		:param estimation: Оценка от 1 до 5.
		:type estimation: int
		:raises ValueError: Неверное значение оценки.
		"""

		if not estimation:
			self._Data["estimation"] = None
			self.save()
			return

		if estimation not in range(1, 5 + 1): raise ValueError("Estimation not in correct range.")

		self._Data["estimation"] = estimation
		self.save()

	def remove_another_name(self, another_name: str):
		"""
		Удаляет альтернативное название.

		:param another_name: Альтернативное название.
		:type another_name: str
		:raises ValueError: Имя не найдено.
		"""

		self._Data["another_names"].remove(another_name)
		self.save()

	def remove_era(self):
		"""Удаляет эру."""

		self._Data["era"] = None
		self.save()

	def set_era_by_index(self, era_index: int | float):
		"""
		Задаёт эру по индексу.

		:param era_index: Индекс эры.
		:type era_index: int | float
		:raises ValueError: Несуществующий индекс эры.
		"""

		if era_index not in tuple(CurrentEra.index for CurrentEra in self._Table.eras): raise ValueError("Incorrect era index.")
		self._Data["era"] = era_index
		self.save()

	def set_era_by_year(self, year: int):
		"""
		Задаёт эру по году основных событий произведения.

		:param year: Год основных событий произведения.
		:type year: int
		"""

		for CurrentEra in self._Table.eras:
			if CurrentEra.index < 0: continue

			MatchStart = CurrentEra.start_year == None or year >= CurrentEra.start_year
			MatchEnd = CurrentEra.end_year == None or year <= CurrentEra.end_year

			if MatchStart and MatchEnd: self.set_era_by_index(CurrentEra.index)

	def set_localized_name(self, localized_name: str | None):
		"""
		Задаёт локализованное название книги.

		:param localized_name: Локализованное название.
		:type localized_name: str
		:raises ValueError: Локализованное название уже определено в другой графе.
		"""

		AllNames = self._Data["another_names"]
		if self._Data["name"]: AllNames.append(self._Data["name"])
		if localized_name in AllNames: raise ValueError("Localized name already used.")

		self._Data["localized_name"] = localized_name
		self.save()

	def set_status(self, status: Statusses | None):
		"""
		Задаёт статус прочтения.

		:param status: Статус прочтения.
		:type status: Statusses | None
		"""

		if status: status = status.value
		self._Data["status"] = status
		self.save()

	def set_type(self, type: Types):
		"""
		Задаёт тип произведения.

		:param type: Тип произведения.
		:type type: Types
		"""

		self._Data["type"] = type = type.value
		self.save()