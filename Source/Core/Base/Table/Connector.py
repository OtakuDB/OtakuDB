from Source.Core import Exceptions

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from . import BaseNote, BaseTable

#==========================================================================================#
# >>>>> ОПЕРАТОР СВЯЗЕЙ <<<<< #
#==========================================================================================#

@dataclass
class NoteBondsCache:
	"""Кэш связей записи."""

	masters: list[int] = field(default_factory = list)
	slaves: list[int] = field(default_factory = list)

@dataclass(frozen = True)
class Bond:
	"""Связь."""

	name: str
	slaves_id: list[int]

class NoteBonds:
	"""Связи записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bonds(self) -> tuple[Bond, ...]:
		"""Последовательность связей."""

		return tuple(self.__Bonds.values())
	
	@property
	def bonds_names(self) -> tuple[str, ...]:
		"""Последовательность имён связей."""

		return tuple(self.__Bonds.keys())

	@property
	def has_masters(self) -> bool:
		"""Состояние: имеются ли привязавшие записи.."""

		return self.__Operator.is_note_has_masters(self.__NoteID)

	@property
	def has_slaves(self) -> bool:
		"""Состояние: имеются ли привязанные записи.."""

		return self.__Operator.is_note_has_slaves(self.__NoteID)

	@property
	def masters(self) -> "tuple[BaseNote, ...]":
		"""Привязавшие записи."""

		return self.__Operator.get_note_masters(self.__NoteID)

	@property
	def slaves(self) -> "tuple[BaseNote, ...]":
		"""Привязанные записи."""

		return self.__Operator.get_note_slaves(self.__NoteID)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseData(self, data: dict[str, list[int]]) -> dict[str, Bond]:
		"""
		Парсит данные связей.

		:param data: Словарь данных связей.
		:type data: dict[str, list[int]]
		:return: Словарь связей.
		:rtype: dict[str, Bond]
		"""

		for BondName in self.__Table.manifest.connections.bonds.names:
			if BondName not in data: data[BondName] = list()

		Bonds = dict()
		for Name, SlavesList in data.items(): Bonds[Name] = Bond(Name, SlavesList)

		return Bonds

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, operator: "BondsOperator", note_id: int, data: dict[str, list[int]]):
		"""
		Связи записи.
		
		:param operator: Оператор связей.
		:type operator: BondsOperator
		:param note_id: ID записи.
		:type note_id: int
		:param data: Словарь данных связей.
		:type data: dict[str, list[int]]
		"""

		self.__Operator = operator
		self.__NoteID = note_id

		self.__Table = operator.table
		self.__Bonds: dict[str, Bond] = self.__ParseData(data)

	def bind(self, bond_name: str, slave_id: int):
		"""
		Привязывает одну запись к другой внутри таблицы.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param slave_id: ID привязываемой записи.
		:type slave_id: int
		"""

		self.__Operator.bind(self.__NoteID, bond_name, slave_id)

	def get_bond(self, bond_name: str) -> Bond:
		"""
		Возвращает связь.

		:param bond_name: Имя связи.
		:type bond_name: str
		:return: Связь.
		:rtype: Bond
		:raises BondNotDescribed: Связь не описана.
		"""

		if bond_name not in self.__Bonds: raise Exceptions.Note.BondNotDescribed(bond_name)

		return self.__Bonds[bond_name]

	def set_note_id(self, new_note_id: int):
		"""
		Заменяет ID записи на новый.

		:param new_note_id: Новый ID записи.
		:type new_note_id: int
		"""

		self.__NoteID = new_note_id

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта
		:rtype: dict
		"""

		return {Name: CurrentBond.slaves_id for Name, CurrentBond in self.__Bonds.items()}

	def unbind(self, bond_name: str, slave_id: int):
		"""
		Отвязывает одну запись от другой внутри таблицы.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param slave_id: ID отвязываемой записи.
		:type slave_id: int
		"""

		self.__Operator.unbind(self.__NoteID, bond_name, slave_id)		

	def update_slaves_id(self, old_slave_id: int, new_slave_id: int):
		"""
		Заменяет старый ID привязанной записи на новый.

		:param old_slave_id: Старый ID.
		:type old_slave_id: int
		:param new_slave_id: Новый ID.
		:type new_slave_id: int
		"""

		for CurrentBond in self.__Bonds.values():
			if old_slave_id in CurrentBond.slaves_id:
				Index = CurrentBond.slaves_id.index(old_slave_id)
				CurrentBond.slaves_id[Index] = new_slave_id

class BondsOperator:
	"""Оператор связей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def table(self) -> "BaseTable":
		"""Таблица."""

		return self.__Table

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __LoadData(self):
		"""Считывает данные из файла _.bonds.json_ в директории таблицы и парсит их."""

		self.__Bonds: dict[int, NoteBonds] = dict()

		DataFilePath = self.__Table.full_path / ".bonds.json"

		if DataFilePath.exists():
			Buffer = ReadJSON(DataFilePath)
			for MasterID in Buffer.keys(): self.__Bonds[int(MasterID)] = NoteBonds(self, int(MasterID), Buffer[MasterID])

		self.__UpdateBondsCache()

	def __UpdateBondsCache(self):
		"""Обновляет кэш связей."""

		self.__Cache: dict[int, NoteBondsCache] = dict()

		for MasterID, MasterBonds in self.__Bonds.items():
			if MasterID not in self.__Cache: self.__Cache[MasterID] = NoteBondsCache()

			for Bond in MasterBonds.bonds:
				for SlaveID in Bond.slaves_id:
					if SlaveID not in self.__Cache: self.__Cache[SlaveID] = NoteBondsCache()

					if SlaveID not in self.__Cache[MasterID].slaves: self.__Cache[MasterID].slaves.append(SlaveID)
					if MasterID not in self.__Cache[SlaveID].masters: self.__Cache[SlaveID].masters.append(MasterID)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BaseTable"):
		"""
		Оператор связей.

		:param table: Таблица.
		:type table: BaseTable
		"""

		self.__Table = table
		
		self.__LoadData()

	def bind(self, master_id: int, bond_name: str, slave_id: int):
		"""
		Привязывает одну запись к другой внутри таблицы.

		:param master_id: ID записи, к которой осуществляется привязка.
		:type master_id: int
		:param bond_name: Имя связи.
		:type bond_name: str
		:param slave_id: ID привязываемой записи.
		:type slave_id: int
		:raises MaxBindedNotesCountReached: Достигнуто максимальное количество прикрепляемых записей.
		"""

		self.__Table.get_note(master_id)
		self.__Table.get_note(slave_id)

		BondParameters = self.__Table.manifest.connections.bonds.get_bond_parameters(bond_name)
		MasterBond = self.get_note_bonds(master_id).get_bond(bond_name)

		if BondParameters.count and len(MasterBond.slaves_id) >= BondParameters.count: raise Exceptions.Note.MaxBindedNotesCountReached(bond_name, BondParameters.count)

		MasterBond.slaves_id.append(slave_id)

		self.save()
		self.__UpdateBondsCache()

	def get_note_bonds(self, note_id: int) -> NoteBonds:
		"""
		Возвращает связи записи.

		:param note_id: ID записи.
		:type note_id: int
		:return: Связи записи.
		:rtype: NoteBonds
		"""

		self.__Table.get_note(note_id)

		if not self.__Bonds.get(note_id): self.__Bonds[note_id] = NoteBonds(self, note_id, dict())

		return self.__Bonds.get(note_id)

	def get_note_masters(self, slave_id: int) -> "tuple[BaseNote, ...]":
		"""
		Возвращает привязавшие записи.

		:param slave_id: ID записи, для которой нужно вернуть привязавшие записи.
		:type slave_id: int
		:return: Последовательность привязавших записей.
		:rtype: tuple[BaseNote, ...]
		"""

		BindedNotes: list["BaseNote"] = list()
		if slave_id in self.__Cache:
			for MasterID in self.__Cache[slave_id].masters: BindedNotes.append(self.__Table.get_note(MasterID))

		return tuple(sorted(BindedNotes, key = lambda CurrentNote: CurrentNote.id))

	def get_note_slaves(self, master_id: int) -> "tuple[BaseNote, ...]":
		"""
		Возвращает привязанные записи.

		:param master_id: ID записи, для которой нужно вернуть привязанные записи.
		:type master_id: int
		:return: Последовательность привязанных записей.
		:rtype: tuple[BaseNote, ...]
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		BindedNotes: list["BaseNote"] = list()
		if master_id in self.__Cache:
			for SlaveID in self.__Cache[master_id].slaves: BindedNotes.append(self.__Table.get_note(SlaveID))

		return tuple(sorted(BindedNotes, key = lambda CurrentNote: CurrentNote.id))

	def is_note_has_masters(self, slave_id: int) -> bool:
		"""
		Проверяет, есть ли у записи привязавшие записи.

		:param slave_id: ID записи, для которой нужно проверить наличие привязок.
		:type slave_id: int
		:return: Возвращает `True`, если найдены привязки.
		:rtype: bool
		"""

		if slave_id not in self.__Cache: return False

		return bool(self.__Cache[slave_id].masters)
	
	def is_note_has_slaves(self, master_id: int) -> bool:
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

	def save(self):
		"""Сохраняет данные связей в файл _.bonds.json_ в директории таблицы."""

		WriteJSON(self.__Table.full_path / ".bonds.json", self.to_dict(), atomic = True)

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта
		:rtype: dict
		"""

		return {NoteID: CurrentNoteBonds.to_dict() for NoteID, CurrentNoteBonds in self.__Bonds.items() if CurrentNoteBonds.bonds}

	def unbind(self, master_id: int, bond_name: str, slave_id: int):
		"""
		Отвязывает одну запись от другой внутри таблицы.

		:param master_id: ID записи, от которой осуществляется отвязка.
		:type master_id: int
		:param bond_name: Имя связи.
		:type bond_name: str
		:param slave_id: ID отвязываемой записи.
		:type slave_id: int
		"""

		self.__Table.get_note(master_id)
		self.__Table.get_note(slave_id)
		self.__Table.manifest.connections.bonds.get_bond_parameters(bond_name)

		MasterBond = self.get_note_bonds(master_id).get_bond(bond_name)

		try:
			MasterBond.slaves_id.remove(slave_id)
			self.save()
			self.__UpdateBondsCache()
		except ValueError: pass

	def update_note_id(self, old_id: int, new_id: int):
		"""
		Обновляет ID записи во внутреннем хранилище.

		:param old_id: Старый ID записи.
		:type old_id: int
		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if old_id in self.__Bonds:
			Buffer = self.__Bonds[old_id]
			Buffer.set_note_id(new_id)
			del self.__Bonds[old_id]
			self.__Bonds[new_id] = Buffer

		for CurrentNoteBonds in self.__Bonds.values(): CurrentNoteBonds.update_slaves_id(old_id, new_id)

		self.save()
		self.__UpdateBondsCache()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Connector:
	"""Оператор соединений."""

	@property
	def bonds(self) -> BondsOperator:
		"""Оператор связей."""

		return self.__Bonds
	
	@property
	def hyperlinks(self):
		"""Оператор гиперссылок."""

		raise NotImplementedError("Hyperlinks")

	def __init__(self, table: "BaseTable"):
		"""
		Оператор связей и гиперссылок.

		:param table: Таблица.
		:type table: BaseTable
		"""

		self.__Table = table

		self.__Bonds = BondsOperator(self.__Table)