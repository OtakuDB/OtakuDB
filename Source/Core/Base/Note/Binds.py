from dublib.Methods.Data import Copy

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from . import BaseNote

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class LocalBinds:
	"""Локальные связи записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def notes_id(self) -> tuple[int]:
		"""Последовательность ID привязанных локальных записей."""

		return tuple(self.__LocalBinds)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: list[int]):
		"""
		Локальные связи записи.

		:param note: Запись.
		:type note: BaseNote
		:param data: Список ID привязанных локальных записей.
		:type data: list[int]
		"""

		self.__Note = note
		self.__LocalBinds = data

	def __bool__(self) -> bool:
		"""
		Возвращает логическую интерпретацию содержимого объекта.

		:return: Логическая интерпретация содержимого объекта.
		:rtype: bool
		"""
		
		return bool(self.__LocalBinds)

	def bind(self, note_id: int):
		"""
		Привязывает запись из текущей таблицы.

		:param note_id: ID привязываемой записи.
		:type note_id: int
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		TargetNote = self.__Note.table.get_note(note_id)

		if TargetNote.id not in self.__LocalBinds:
			self.__LocalBinds.append(TargetNote.id)
			self.__Note.save()

	def unbind(self, note_id: int):
		"""
		Отвязывает запись из текущей таблицы.

		:param note_id: ID отвязываемой записи.
		:type note_id: int
		"""

		try:
			self.__LocalBinds.remove(note_id)
			self.__Note.save()
		except ValueError: pass

	def update(self, old_id: int, new_id: int):
		"""
		Обновляет ID привязанной записи в контейнере локальных связей.

		:param old_id: Старый ID записи.
		:type old_id: int
		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		Index = self.__LocalBinds.index(old_id)
		self.__LocalBinds[Index] = new_id
		self.__Note.save()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Binds:
	"""Cвязи записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def local(self) -> LocalBinds:
		"""Локальные связи записи."""

		return self.__LocalBinds

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: dict):
		"""
		Cвязи записи.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь связей.
		:type data: dict
		"""

		self.__Note = note
		self.__Data: dict[str, list] = {
			"local": [],
			"global": []
		} | data
		
		self.__LocalBinds = LocalBinds(self.__Note, self.__Data["local"])

	def to_dict(self, copy: bool = True) -> dict[str, list]:
		"""
		Возвращает словарное представление связей.

		:return: Словарное представление связей.
		:rtype: dict[str, list]
		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		"""

		return Copy(self.__Data) if copy else self.__Data