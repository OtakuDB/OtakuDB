from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dublib.functions.filesystem import json

from .... import exceptions

if TYPE_CHECKING:
	from .. import BaseNote, BaseTable

#==========================================================================================#
# >>>>> ВСОПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ СВЯЗЕЙ <<<<< #
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

		return tuple(self.__bonds.values())
	
	@property
	def bonds_names(self) -> tuple[str, ...]:
		"""Последовательность имён связей."""

		return tuple(self.__bonds.keys())

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

	def __parse_data(self, data: dict[str, list[int]]) -> dict[str, Bond]:
		"""
		Парсит данные связей.

		:param data: Словарь данных связей.
		:type data: dict[str, list[int]]
		:return: Словарь связей.
		:rtype: dict[str, Bond]
		"""

		for BondName in self.__table.manifest.connections.bonds.names:
			if BondName not in data: data[BondName] = []

		Bonds = {}
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

		self.__table = operator.table
		self.__bonds: dict[str, Bond] = self.__parse_data(data)

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
		:raises BondNotDescribedError: Связь не описана.
		"""

		if bond_name not in self.__bonds: raise exceptions.note.BondNotDescribedError(bond_name)

		return self.__bonds[bond_name]

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

		return {Name: CurrentBond.slaves_id for Name, CurrentBond in self.__bonds.items()}

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

		for CurrentBond in self.__bonds.values():
			if old_slave_id in CurrentBond.slaves_id:
				Index = CurrentBond.slaves_id.index(old_slave_id)
				CurrentBond.slaves_id[Index] = new_slave_id

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BondsOperator:
	"""Оператор связей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def table(self) -> "BaseTable":
		"""Таблица."""

		return self.__table

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __load_data(self):
		"""Считывает данные из файла _.bonds.json_ в директории таблицы и парсит их. Также обновляет кэш связей."""

		data_file = self.__table.full_path / ".bonds.json"

		if data_file.exists():
			buffer = json.read(data_file)
			self.__bonds = {int(master_id): NoteBonds(self, int(master_id), buffer[master_id]) for master_id in buffer.keys()}

		self.__update_bonds_cache()

	def __update_bonds_cache(self):
		"""Обновляет кэш связей."""

		self.__cache.clear()

		for master_id, master_bonds in self.__bonds.items():
			if master_id not in self.__cache:
				self.__cache[master_id] = NoteBondsCache()

			for bond in master_bonds.bonds:
				for slave_id in bond.slaves_id:

					if slave_id not in self.__cache:
						self.__cache[slave_id] = NoteBondsCache()

					if slave_id not in self.__cache[master_id].slaves:
						self.__cache[master_id].slaves.append(slave_id)

					if master_id not in self.__cache[slave_id].masters:
						self.__cache[slave_id].masters.append(master_id)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BaseTable"):
		"""
		Оператор связей.

		:param table: Таблица.
		:type table: BaseTable
		"""

		self.__table = table
		self.__bonds: dict[int, NoteBonds] = {}
		self.__cache: dict[int, NoteBondsCache] = {}

		self.__load_data()

	def bind(self, master_id: int, bond_name: str, slave_id: int):
		"""
		Привязывает одну запись к другой внутри таблицы.

		:param master_id: ID записи, к которой осуществляется привязка.
		:type master_id: int
		:param bond_name: Имя связи.
		:type bond_name: str
		:param slave_id: ID привязываемой записи.
		:type slave_id: int
		:raises MaxBindedNotesCountReachedError: Достигнуто максимальное количество прикрепляемых записей.
		"""

		self.__table.get_note(master_id)
		self.__table.get_note(slave_id)

		bond_parameters = self.__table.manifest.connections.bonds.get_bond_parameters(bond_name)
		master_bond = self.get_note_bonds(master_id).get_bond(bond_name)

		if bond_parameters.count and len(master_bond.slaves_id) >= bond_parameters.count:
			raise exceptions.note.MaxBindedNotesCountReachedError(bond_name, bond_parameters.count)

		master_bond.slaves_id.append(slave_id)

		self.save()
		self.__update_bonds_cache()

	def get_note_bonds(self, note_id: int) -> NoteBonds:
		"""
		Возвращает связи записи.

		:param note_id: ID записи.
		:type note_id: int
		:return: Связи записи.
		:rtype: NoteBonds
		"""

		self.__table.get_note(note_id)
		Bonds = self.__bonds.get(note_id)

		if not Bonds:
			Bonds = NoteBonds(self, note_id, {})
			self.__bonds[note_id] = Bonds

		return Bonds

	def get_note_masters(self, slave_id: int) -> "tuple[BaseNote, ...]":
		"""
		Возвращает привязавшие записи.

		:param slave_id: ID записи, для которой нужно вернуть привязавшие записи.
		:type slave_id: int
		:return: Последовательность привязавших записей.
		:rtype: tuple[BaseNote, ...]
		"""

		BindedNotes: list["BaseNote"] = []
		if slave_id in self.__cache:
			for MasterID in self.__cache[slave_id].masters: BindedNotes.append(self.__table.get_note(MasterID))

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

		BindedNotes: list["BaseNote"] = []
		if master_id in self.__cache:
			for SlaveID in self.__cache[master_id].slaves: BindedNotes.append(self.__table.get_note(SlaveID))

		return tuple(sorted(BindedNotes, key = lambda CurrentNote: CurrentNote.id))

	def is_note_has_masters(self, slave_id: int) -> bool:
		"""
		Проверяет, есть ли у записи привязавшие записи.

		:param slave_id: ID записи, для которой нужно проверить наличие привязок.
		:type slave_id: int
		:return: Возвращает `True`, если найдены привязки.
		:rtype: bool
		"""

		if slave_id not in self.__cache: return False

		return bool(self.__cache[slave_id].masters)
	
	def is_note_has_slaves(self, master_id: int) -> bool:
		"""
		Проверяет, есть ли у записи привязанные записи.

		:param slave_id: ID записи, для которой нужно проверить наличие привязок.
		:type slave_id: int
		:return: Возвращает `True`, если найдены привязки.
		:rtype: bool
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		if master_id not in self.__cache: return False

		return bool(self.__cache[master_id].slaves)

	def save(self):
		"""Сохраняет данные связей в файл _.bonds.json_ в директории таблицы."""

		json.write(self.__table.full_path / ".bonds.json", self.to_dict(), atomic = True)

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта
		:rtype: dict
		"""

		return {NoteID: CurrentNoteBonds.to_dict() for NoteID, CurrentNoteBonds in self.__bonds.items() if CurrentNoteBonds.bonds}

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

		self.__table.get_note(master_id)
		self.__table.get_note(slave_id)
		self.__table.manifest.connections.bonds.get_bond_parameters(bond_name)

		MasterBond = self.get_note_bonds(master_id).get_bond(bond_name)

		try:
			MasterBond.slaves_id.remove(slave_id)
			self.save()
			self.__update_bonds_cache()
		except ValueError: pass

	def update_note_id(self, old_id: int, new_id: int):
		"""
		Обновляет ID записи во внутреннем хранилище.

		:param old_id: Старый ID записи.
		:type old_id: int
		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if old_id in self.__bonds:
			Buffer = self.__bonds[old_id]
			Buffer.set_note_id(new_id)
			del self.__bonds[old_id]
			self.__bonds[new_id] = Buffer

		for CurrentNoteBonds in self.__bonds.values(): CurrentNoteBonds.update_slaves_id(old_id, new_id)

		self.save()
		self.__update_bonds_cache()
