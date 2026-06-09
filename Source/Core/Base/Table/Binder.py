from Source.Core import Exceptions

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..Table import BaseNote, BaseTable

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class BindingCache:
	"""Кэш связей записи."""

	masters: list[int] = field(default_factory = list)
	slaves: list[int] = field(default_factory = list)

class LocalBinder:
	"""Оператор локальных связей."""

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __UpdateBindingsCache(self):
		"""Обновляет кэш связей."""

		for MasterID, SlavesID in self.__Data.items():
			if MasterID not in self.__Cache: self.__Cache[MasterID] = BindingCache()
			self.__Cache[MasterID].slaves = SlavesID

			for SlaveID in SlavesID:
				if SlaveID not in self.__Cache: self.__Cache[SlaveID] = BindingCache()
				self.__Cache[SlaveID].masters.append(MasterID)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BaseTable"):
		"""
		Локальные связи записи.

		:param note: Запись.
		:type note: BaseNote
		:param data: Список ID привязанных локальных записей.
		:type data: list[int]
		"""

		self.__Table = table

		self.__Data: dict[int, list] = dict()
		self.__Cache: dict[int, BindingCache] = dict()

		self.reload()

	def bind(self, master_id: int, slave_id: int):
		"""
		Осуществляет привязку записи.

		:param master_id: ID записи, к которой осуществляется привязка.
		:type master_id: int
		:param slave_id: ID привязываемой записи.
		:type slave_id: int
		:raises NoteNotFound: Запись не найдена в таблице.
		:raises LocalBindsDenied: Прикрепление записей той же таблицы к текущей записи запрещено.
		"""

		if not self.__Table.manifest.common.binds: raise Exceptions.Note.LocalBindsDenied()
		self.__Table.get_note(master_id)
		self.__Table.get_note(slave_id)

		if master_id not in self.__Data: self.__Data[master_id] = [slave_id]
		elif slave_id not in self.__Data[master_id]:
			self.__Data[master_id].append((slave_id))
			self.__Data[master_id] = list(set(self.__Data[master_id]))

		self.save()
		self.__UpdateBindingsCache()

	def get_masters(self, slave_id: int) -> "tuple[BaseNote]":
		"""
		Возвращает привязавшие записи.

		:param slave_id: ID записи, для которой нужно вернуть привязавшие записи.
		:type slave_id: int
		:return: Последовательность привязавших записей.
		:rtype: tuple[BaseNote]
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		BindedNotes: list["BaseNote"] = list()
		if slave_id in self.__Cache:
			for MasterID in self.__Cache[slave_id].masters: BindedNotes.append(self.__Table.get_note(MasterID))

		return tuple(sorted(BindedNotes, key = lambda CurrentNote: CurrentNote.id))

	def get_slaves(self, master_id: int) -> "tuple[BaseNote]":
		"""
		Возвращает привязанные записи.

		:param master_id: ID записи, для которой нужно вернуть привязанные записи.
		:type master_id: int
		:return: Последовательность привязанных записей.
		:rtype: tuple[BaseNote]
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		BindedNotes: list["BaseNote"] = list()
		if master_id in self.__Cache:
			for SlaveID in self.__Cache[master_id].slaves: BindedNotes.append(self.__Table.get_note(SlaveID))

		return tuple(sorted(BindedNotes, key = lambda CurrentNote: CurrentNote.id))

	def has_masters(self, slave_id: int) -> bool:
		"""
		Проверяет, есть ли у записи привязавшие записи.

		:param slave_id: ID записи, для которой нужно проверить наличие привязок.
		:type slave_id: int
		:return: Возвращает `True`, если найдены привязки.
		:rtype: bool
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		if slave_id not in self.__Cache: return False

		return bool(self.__Cache[slave_id].masters)
	
	def has_slaves(self, master_id: int) -> bool:
		"""
		Проверяет, есть ли у записи привязанные записи.

		:param slave_id: ID записи, для которой нужно проверить наличие привязок.
		:type slave_id: int
		:return: Возвращает `True`, если найдены привязки.
		:rtype: bool
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		if master_id not in self.__Cache: return False

		return bool(self.__Cache[master_id].slaves)
	
	def reload(self) -> dict[int, list[int]]:
		"""
		Загружает данные из файла _.binds.json_ в директории таблицы.

		:return: Словарь, где ключ – ID записи, а значение – список ID привязанных записей.
		:rtype: dict[int, list[int]]
		"""

		DataFilePath = self.__Table.full_path / ".binds.json"

		if DataFilePath.exists():
			Buffer = ReadJSON(DataFilePath)
			self.__Data = {int(Key): Value for Key, Value in Buffer.items()}

		self.__UpdateBindingsCache()

	def save(self):
		"""Сохраняет данные локальных связей таблицы."""

		WriteJSON(self.__Table.full_path / ".binds.json", self.__Data)

	def unbind(self, master_id: int, slave_id: int):
		"""
		Осуществляет отвязку записи.

		:param master_id: ID записи, от которой осуществляется отвязка.
		:type master_id: int
		:param slave_id: ID отвязываемой записи.
		:type slave_id: int
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		self.__Table.get_note(master_id)
		self.__Table.get_note(slave_id)

		if master_id in self.__Data and slave_id in self.__Data[master_id]:
			self.__Data[master_id].remove(slave_id)
			self.save()
			self.__UpdateBindingsCache()

	def update(self, old_id: int, new_id: int | None):
		"""
		Обновляет ID записи во внутреннем хранилище.

		:param old_id: Старый ID записи.
		:type old_id: int
		:param new_id: Новый ID записи. При указании `None` удаляет все связи.
		:type new_id: int | None
		"""

		if old_id in self.__Data:
			Buffer = self.__Data[old_id]
			del self.__Data[old_id]
			if new_id != None: self.__Data[new_id] = Buffer

		for MasterID in self.__Data.keys():
			if old_id in self.__Data[MasterID]:
				Index = self.__Data[MasterID].index(old_id)
				if new_id == None: self.__Data[MasterID].pop(Index)
				else: self.__Data[MasterID][Index] = new_id

		self.save()
		self.__UpdateBindingsCache()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Binder:
	"""Оператор связей."""

	@property
	def local(self) -> LocalBinder:
		"""Оператор локальных связей."""

		return self.__LocalBinder

	def __init__(self, table: "BaseTable"):
		"""
		Оператор связей.

		:param table: _description_
		:type table: BaseTable
		"""

		self.__Table = table

		self.__LocalBinder = LocalBinder(self.__Table)