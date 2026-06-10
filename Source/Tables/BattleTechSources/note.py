from .Enums import CollectionStatuses, Statuses, Types

from Source.Core.Base.Note import BaseNote

from typing import Any

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Note(BaseNote):
	"""Запись о прочтении соурсбука BattleTech."""

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
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Data.get("localized_name")

	@property
	def type(self) -> Types | None:
		"""Тип произведения."""

		return Types(self._Data["type"])

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ ОБРАБОТЧИКИ CALLBACK-ВЫЗОВОВ <<<<< #
	#==========================================================================================#	

	def _Callback_AttachmentsChanged(self):
		"""Обработчик вызова: вложения изменены."""

		if self.collection_status == CollectionStatuses.Collected: return

		if self._Attachments.get_slot("ebook").file: self.set_collection_status(CollectionStatuses.Ebook)
		else: self.set_collection_status(None)

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
			"type": Types.Sourcebook.value,
			"estimation": None,
			"comment": None,
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
		self._Data["status"] = status
		self.save()

	def set_type(self, type: Types):
		"""
		Задаёт тип соурсбука.

		:param type: Тип соурсбука.
		:type type: Types
		"""

		self._Data["type"] = type.value
		self.save()