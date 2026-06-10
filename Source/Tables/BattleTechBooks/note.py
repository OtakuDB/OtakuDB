from .Structs import CollectionStatuses, Era, Statuses, Types

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
	def another_names(self) -> tuple[str, ...]:
		"""Последовательность альтернативных названий."""

		return tuple(self._Data["another_names"])

	@property
	def collection_status(self) -> CollectionStatuses | None:
		"""Статус коллекционирования."""

		Status = self._Data.get("collection_status")
		if Status: return CollectionStatuses(Status)

	@property
	def comment(self) -> str | None:
		"""Комментарий к записи."""

		return self._Data.get("comment")

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
	def status(self) -> Statuses | None:
		"""Статус прочтения."""

		Status = self._Data.get("status")
		if Status: return Statuses(Status)

	@property
	def stories_count(self) -> int | None:
		"""Количество историй в произведении."""

		return self._Data.get("stories_count")

	@property
	def type(self) -> Types | None:
		"""Тип произведения."""

		return Types(self._Data["type"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __UpdateEstimationByLocalBinds(self):
		"""Вычисляет оценку сборника на основе оценок привязанных записей."""

		Slaves: "tuple[Note, ...]" = self.bonds.slaves
		Estimations = tuple(CurrentNote.estimation for CurrentNote in Slaves if CurrentNote.estimation)
		Estimation = None

		# Прибавление 0.5 исправляет округление отсечением.
		if Estimations: Estimation = round(0.5 + sum(Estimations) / len(Estimations))
		if Estimation and self.estimation != Estimation: self.estimate(Estimation)

	def __UpdateStatusByLocalBinds(self):
		"""Определяет статус сборника на основе статусов привязанных записей."""

		BindedNotes: "tuple[Note, ...]" = self.bonds.slaves
		BindedNotesStatuses = list(CurrentNote.status for CurrentNote in BindedNotes if CurrentNote.status)

		if BindedNotesStatuses.count(Statuses.Completed) == len(BindedNotes):
			self.set_status(Statuses.Completed)
			return
		
		if Statuses.Reading in BindedNotesStatuses:
			self.set_status(Statuses.Reading)
			return

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ОБРАБОТЧИКИ CALLBACK-ВЫЗОВОВ <<<<< #
	#==========================================================================================#	

	def _Callback_SlaveNoteSaved(self, slave_note: "BaseNote"):
		"""
		Обработчик вызова: привязанные запись выполнила сохранение.

		:param slave_note: Привязанная запись, выполнившая операцию сохранения.
		:type slave_note: BaseNote
		"""

		if self.type not in (Types.Anthology, Types.Compilation): return

		self.__UpdateEstimationByLocalBinds()
		self.__UpdateStatusByLocalBinds()

	def _Callback_AttachmentsChanged(self):
		"""Обработчик вызова: вложения изменены."""

		if self.collection_status == CollectionStatuses.Collected: return

		if self._Attachments.get_slot("ebook").file: self.set_collection_status(CollectionStatuses.Ebook)
		else: self.set_collection_status(None)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ТРИГГЕРНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostLocalBindMethod(self, note: "Note"):
		"""
		Метод, выполняющийся после привязки локальной записи.

		:param note: Привязанная запись.
		:type note: Note
		"""

		#---> Автообновление типа.
		#==========================================================================================#
		if self.type != Types.Compilation: self.set_type(Types.Compilation)

		#---> Автоматический подсчёт количества историй, если не указано большее значение.
		#==========================================================================================#
		StoriesCount = self.stories_count or 0
		BindsCount = len(self.bonds.slaves)
		if BindsCount - StoriesCount == 1: self.set_stories_count(BindsCount)

		#---> Автоматический подсчёт оценки и определение статуса.
		#==========================================================================================#
		self.__UpdateEstimationByLocalBinds()
		self.__UpdateStatusByLocalBinds()

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
			"type": "story",
			"stories_count": None,
			"era": None,
			"estimation": None,
			"comment": None,
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

	def set_collection_status(self, status: CollectionStatuses | None):
		"""
		Задаёт статус коллекционирования.

		:param status: Статус коллекционирования.
		:type status: CollectionStatuses | None
		"""

		if status: status = status.value
		self._Data["collection_status"] = status
		self.save()

	def set_comment(self, comment: str | None):
		"""
		Задаёт комментарий.

		:param comment: Текст комментария.
		:type comment: str | None
		"""

		self._Data["comment"] = comment
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

		AllNames = list(self.another_names)
		if self._Data["name"]: AllNames.append(self._Data["name"])
		if localized_name in AllNames: raise ValueError("Localized name already used.")

		self._Data["localized_name"] = localized_name
		self.save()

	def set_status(self, status: Statuses | None):
		"""
		Задаёт статус прочтения.

		:param status: Статус прочтения.
		:type status: Statuses | None
		"""

		if status: status = status.value

		if status != self._Data["status"]:
			self._Data["status"] = status
			self.save()

	def set_stories_count(self, count: int | None):
		"""
		Задаёт количество историй в произведении.

		:param count: Количество историй в произведении.
		:type count: int | None
		"""

		if count == 0: count = None
		self._Data["stories_count"] = count
		self.save()

	def set_type(self, type: Types):
		"""
		Задаёт тип произведения.

		:param type: Тип произведения.
		:type type: Types
		"""

		self._Data["type"] = type.value
		self.save()