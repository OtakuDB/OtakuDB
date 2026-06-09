from .Enums import PartStatuses, PartsTypes, Statuses
from .Part import Part

from Source.Core.Base.Note import BaseNote

from typing import Any

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Note(BaseNote):
	"""Запись о просмотре аниме."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> tuple[str]:
		"""Последовательность альтернативных названий."""

		return tuple(self._Data["another_names"])

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self._Data.get("estimation")

	@property
	def is_dropped(self) -> bool:
		"""Состояние: заброшен ли просмотр данного аниме."""

		if self._Data.get("is_dropped"): return True
		# Поддержка Legacy-статусов.
		if self._Data.get("status") == "dropped": return True

		return False

	@property
	def parts(self) -> tuple[Part]:
		"""Последовательность частей."""

		return tuple(self.__Parts)

	@property
	def progress(self) -> float:
		"""Доля прогресса просмотра."""

		if not self.__Parts: return 0.0

		Viewed = sum(Element.progress for Element in self.__Parts)
		Total = float(len(self.__Parts))

		return round(Viewed / Total, 2)

	@property
	def status(self) -> Statuses:
		"""Статус просмотра."""

		if self.is_dropped: return Statuses.Dropped
		if not self.__Parts: return Statuses.Planned

		PartsStatusesTuple = tuple(CurrentPart.status for CurrentPart in self.__Parts)

		IsAnnounced = PartStatuses.Announced in PartsStatusesTuple
		IsUnwatched = PartStatuses.Unwatched in PartsStatusesTuple
		IsWatching = PartStatuses.Watching in PartsStatusesTuple

		if IsAnnounced and not IsWatching and not IsUnwatched: return Statuses.Announced
		if not IsUnwatched and not IsWatching: return Statuses.Completed
		if IsWatching: return Statuses.Watching
		if IsUnwatched: return Statuses.Planned

	@property
	def tags(self) -> tuple[str]:
		"""Последовательность тегов."""

		return tuple(self._Data["tags"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseParts(self) -> list[Part]:
		"""
		Парсит словарные представления частей в объекты.

		:return: Список частей.
		:rtype: list[Part]
		"""

		Parts = list()
		for PartDictionary in self._Data["parts"]: Parts.append(Part(self, PartDictionary))

		return Parts

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ТРИГГЕРНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Parts: list[Part] = self.__ParseParts() 

	def _PreSaveMethod(self):
		"""Метод, выполняющийся перед сохранением записи."""

		self._Data["parts"] = tuple(CurrentPart.to_dict() for CurrentPart in self.__Parts)

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
			"name": None,
			"another_names": list(),
			"estimation": None,
			"is_dropped": False,
			"tags": list(),
			"metainfo": dict(),
			"parts": list()
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

		if another_name not in self._Data["another_names"] and another_name != self._Data["name"]:
			self._Data["another_names"].append(another_name)
			self.save()

	def add_tag(self, tag: str):
		"""
		Добавляет тег.

		:param tag: Тег.
		:type tag: str
		"""

		if tag not in self._Data["tags"]:
			self._Data["tags"].append(tag)
			self.save()

	def create_part(self, type: PartsTypes) -> int:
		"""
		Создаёт часть.

		:param type: Тип части.
		:type type: PartsTypes
		:return: Индекс части.
		:rtype: int
		"""

		NewPart = Part(self, {"type": type.value})
		self.__Parts.append(NewPart)
		self.save()

		return len(self.__Parts) - 1

	def down_part(self, index: int, count: int = 1) -> int:
		"""
		Опускает часть на указанное количество вниз (увеличивает индекс).

		:param index: Индекс части.
		:type index: int
		:param count: Количество операций.
		:type count: int
		:return: Новый индекс части.
		:rtype: int
		:raises ValueError: Неверное количество операций.
		"""

		if count < 1 or count > len(self.__Parts): raise ValueError(f"Incorrect operations count: {count}.")
		NewIndex = index

		if index < len(self.__Parts):

			if count > 1:
				for _ in range(0, count): NewIndex = self.down_part(index, 1)

			else:
				self.__Parts.insert(index - 1, self.__Parts.pop(index))
				self.save()

		self.save()

		return NewIndex

	def drop(self):
		"""Переключает состояние заброшенности тайтла."""

		self._Data["is_dropped"] = not self._Data["is_dropped"]
		self.save()

	def estimate(self, estimation: int | None):
		"""
		Выставляет оценку тайтла.

		:param estimation: Оценка.
		:type estimation: int
		:raises ValueError: Неверное значение оценки.
		"""

		if not estimation:
			self._Data["estimation"] = None
			self.save()
			return

		if estimation not in range(1, self._Table.manifest.custom["max_estimation"] + 1): raise ValueError("Estimation not in correct range.")

		self._Data["estimation"] = estimation
		self.save()

	def get_part(self, index: int) -> Part:
		"""
		Возвращает часть.

		:param index: Индекс части.
		:type index: int
		:return: Часть.
		:rtype: Part
		:raises IndexError: Часть не найдена.
		"""

		return self.__Parts[index]

	def remove_another_name(self, another_name: str):
		"""
		Удаляет альтернативное название.

		:param another_name: Альтернативное название.
		:type another_name: str
		:raises ValueError: Имя не найдено.
		"""

		self._Data["another_names"].remove(another_name)
		self.save()

	def remove_part(self, index: int):
		"""
		Удаляет часть.

		:param index: Индекс части.
		:type index: int
		:raises IndexError: Часть не найдена.
		"""

		self.__Parts.pop(index)
		self.save()

	def remove_tag(self, tag: str):
		"""
		Удаляет тег.

		:param tag: Тег.
		:type tag: str
		:raises ValueError: Тег не найден.
		"""

		self._Data["tags"].remove(tag)
		self.save()

	def up_part(self, index: int, count: int = 1) -> int:
		"""
		Поднимает часть на указанное количество вверх (увеличивает индекс).

		:param index: Индекс части.
		:type index: int
		:param count: Количество операций.
		:type count: int
		:return: Новый индекс части.
		:rtype: int
		:raises ValueError: Неверное количество операций.
		"""

		if count < 1 or count > len(self.__Parts): raise ValueError(f"Incorrect operations count: {count}.")
		NewIndex = index

		if index > 0:

			if count > 1:
				for _ in range(0, count): NewIndex = self.up_part(index, 1)

			else:
				self.__Parts.insert(index + 1, self.__Parts.pop(index))
				self.save()

		self.save()

		return NewIndex