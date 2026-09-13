from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Literal, overload

from dublib.functions.filesystem import json

from .... import exceptions

if TYPE_CHECKING:
	from pathlib import Path

	from .. import BaseNote, BaseTable

#==========================================================================================#
# >>>>> ВСОПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class NoteBondsCache:
	"""Кэш связей записи."""

	masters: list[int] = field(default_factory = list)
	slaves: list[int] = field(default_factory = list)

@dataclass(frozen = True)
class Bond:
	"""Связь."""

	name: str
	slaves_id: list[int]

@dataclass(frozen = True)
class ReadOnlyBond:
	"""Связь."""

	name: str
	slaves_id: tuple[int, ...]

class NoteBonds[N: "BaseNote"]:
	"""Связи записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bonds(self) -> tuple[ReadOnlyBond, ...]:
		"""Последовательность связей."""

		return tuple(self.__create_read_only_bond(bond) for bond in self.__bonds.values())
	
	@property
	def bonds_names(self) -> tuple[str, ...]:
		"""Последовательность имён связей."""

		return tuple(self.__bonds.keys())

	@property
	def has_bonds(self) -> bool:
		"""Состояние: имеются ли связи."""

		return all((self.has_masters, self.has_slaves))

	@property
	def has_masters(self) -> bool:
		"""Состояние: имеются ли привязавшие записи."""

		return self.__operator.is_note_has_masters(self.__note_id)

	@property
	def has_slaves(self) -> bool:
		"""Состояние: имеются ли привязанные записи.."""

		return self.__operator.is_note_has_slaves(self.__note_id)

	@property
	def masters(self) -> tuple[N, ...]:
		"""Привязавшие записи."""

		return self.__operator.get_note_masters(self.__note_id)

	@property
	def slaves(self) -> tuple[N, ...]:
		"""Привязанные записи."""

		return self.__operator.get_note_slaves(self.__note_id)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __create_read_only_bond(self, bond: Bond) -> ReadOnlyBond:
		"""
		Преобразует связь в объект только для чтения.

		:param bond: Связь.
		:type bond: Bond
		:return: Объект связи только для чтения.
		:rtype: ReadOnlyBond
		"""

		return ReadOnlyBond(bond.name, tuple(bond.slaves_id))

	def __parse_data(self, data: dict[str, list[int]]) -> dict[str, Bond]:
		"""
		Парсит данные связей.

		:param data: Словарь данных связей.
		:type data: dict[str, list[int]]
		:return: Словарь связей.
		:rtype: dict[str, Bond]
		"""

		bonds: dict[str, Bond] = {}

		for name in self.__table.manifest.connections.bonds.names:

			if name not in data:
				bonds[name] = Bond(name, [])
				continue

			bonds[name] = Bond(name, data[name])

		return bonds

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

		self.__operator: "BondsOperator" = operator
		self.__note_id: int = note_id

		self.__bonds: dict[str, Bond] = self.__parse_data(data)
		self.__table = operator.table

	def bind(self, bond_name: str, slave_id: int):
		"""
		Привязывает одну запись к другой внутри таблицы.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param slave_id: ID привязываемой записи.
		:type slave_id: int
		"""

		self.__operator.bind(self.__note_id, bond_name, slave_id)

	@overload
	def get_bond(self, bond_name: str, read_only: Literal[False]) -> Bond: ...
	@overload
	def get_bond(self, bond_name: str, read_only: Literal[True] = True) -> ReadOnlyBond: ...

	def get_bond(self, bond_name: str, read_only: bool = True) -> ReadOnlyBond | Bond:
		"""
		Возвращает связь.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param read_only: Указывает, должна ли связь быть изменяемой. Изменяемая связь должна использоваться только внутри оператора связей!
		:type read_only: bool
		:return: Связь.
		:rtype: ReadOnlyBond | Bond
		:raises BondNotDescribedError: Связь не описана.
		"""

		if bond_name not in self.__bonds:
			raise exceptions.note.bonds.BondNotDescribedError(bond_name)

		bond: Bond = self.__bonds[bond_name]

		if read_only:
			return self.__create_read_only_bond(bond)

		return bond

	def set_note_id(self, new_note_id: int):
		"""
		Заменяет ID записи на новый.

		:param new_note_id: Новый ID записи.
		:type new_note_id: int
		"""

		self.__note_id = new_note_id

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

		self.__operator.unbind(self.__note_id, bond_name, slave_id)		

	def update_slaves_id(self, old_slave_id: int, new_slave_id: int):
		"""
		Заменяет старый ID привязанной записи на новый.

		:param old_slave_id: Старый ID.
		:type old_slave_id: int
		:param new_slave_id: Новый ID.
		:type new_slave_id: int
		"""

		for bond in self.__bonds.values():
			if old_slave_id in bond.slaves_id:
				index: int = bond.slaves_id.index(old_slave_id)
				bond.slaves_id[index] = new_slave_id

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BondsOperator[N: "BaseNote"]:
	"""Оператор связей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def table(self) -> "BaseTable":
		"""Таблица."""

		return self.__table

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ УПРАВЛЕНИЯ КЭШЕМ <<<<< #
	#==========================================================================================#

	def __add_bond_to_cache(self, master_id: int, slave_id: int):
		"""
		Добавляет данные о связи в кэш.

		:param master_id: ID записи, к которой осуществляется привязка. 
		:type master_id: int
		:param slave_id: ID привязываемой записи.
		:type slave_id: int
		"""

		for note_id in (master_id, slave_id):
			if note_id not in self.__cache:
				self.__cache[note_id] = NoteBondsCache()

		master_cache: NoteBondsCache = self.__cache[master_id]
		if slave_id not in master_cache.slaves:
			master_cache.slaves.append(slave_id)

		slave_cache: NoteBondsCache = self.__cache[slave_id]
		if master_id not in slave_cache.masters:
			slave_cache.masters.append(master_id)

	def __refresh_bonds_cache(self):
		"""Обновляет кэш связей. Перезаписывает текущие данные."""

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
	
	def __remove_bond_from_cache(self, master_id: int, slave_id: int):
		"""
		Удаляет данные о связи из кэша.

		:param master_id: ID записи, к которой осуществлена привязка. 
		:type master_id: int
		:param slave_id: ID привязанной записи.
		:type slave_id: int
		"""

		master_cache: NoteBondsCache | None = self.__cache.get(master_id)
		if master_cache and slave_id in master_cache.slaves:
			master_cache.slaves.remove(slave_id)

		slave_cache: NoteBondsCache | None = self.__cache.get(slave_id)
		if slave_cache and master_id in slave_cache.masters:
			slave_cache.masters.remove(master_id)

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __load_data(self):
		"""Считывает данные из файла _.bonds.json_ в директории таблицы и парсит их. Также обновляет кэш связей."""

		if self.__bonds_file.exists():
			data: dict = json.read(self.__bonds_file)
			self.__bonds = {int(master_id): NoteBonds(self, int(master_id), data[master_id]) for master_id in data.keys()}

		self.__refresh_bonds_cache()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BaseTable"):
		"""
		Оператор связей.

		:param table: Таблица.
		:type table: BaseTable
		"""

		self.__table: "BaseTable" = table

		self.__bonds_file: "Path" = self.__table.full_path / ".bonds.json"
		self.__bonds: dict[int, NoteBonds[N]] = {}
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

		self.__table.is_note_exists(master_id, not_found_error = True)
		self.__table.is_note_exists(slave_id, not_found_error = True)

		bond_parameters = self.__table.manifest.connections.bonds.get_bond_parameters(bond_name)
		bond: Bond = self.get_note_bonds(master_id).get_bond(bond_name, read_only = False)

		if bond_parameters.count and len(bond.slaves_id) >= bond_parameters.count:
			raise exceptions.note.bonds.MaxBindedNotesCountReachedError(bond_name, bond_parameters.count)

		bond.slaves_id.append(slave_id)

		self.save()
		self.__add_bond_to_cache(master_id, slave_id)

	def get_note_bonds(self, note_id: int) -> NoteBonds[N]:
		"""
		Возвращает связи записи.

		:param note_id: ID записи.
		:type note_id: int
		:return: Связи записи.
		:rtype: NoteBonds
		"""

		self.__table.is_note_exists(note_id, not_found_error = True)

		bonds: NoteBonds | None = self.__bonds.get(note_id)

		if bonds is None:
			bonds = NoteBonds(self, note_id, {})
			self.__bonds[note_id] = bonds

		return bonds

	def get_note_masters(self, slave_id: int) -> tuple[N, ...]:
		"""
		Возвращает привязавшие записи.

		:param slave_id: ID записи, для которой нужно вернуть привязавшие записи.
		:type slave_id: int
		:return: Последовательность привязавших записей.
		:rtype: tuple[BaseNote, ...]
		"""

		masters: list[N] = []
		
		if slave_id in self.__cache:
			for master_id in self.__cache[slave_id].masters:
				masters.append(self.__table.get_note(master_id))

		return tuple(sorted(masters, key = lambda note: note.id))

	def get_note_slaves(self, master_id: int) -> tuple[N, ...]:
		"""
		Возвращает привязанные записи.

		:param master_id: ID записи, для которой нужно вернуть привязанные записи.
		:type master_id: int
		:return: Последовательность привязанных записей.
		:rtype: tuple[BaseNote, ...]
		:raises NoteNotFound: Запись не найдена в таблице.
		"""

		slaves: list[N] = []

		if master_id in self.__cache:
			for slave_id in self.__cache[master_id].slaves:
				slaves.append(self.__table.get_note(slave_id))

		return tuple(sorted(slaves, key = lambda note: note.id))

	def is_note_has_masters(self, slave_id: int) -> bool:
		"""
		Проверяет, есть ли у записи привязавшие записи.

		:param slave_id: ID записи, для которой нужно проверить наличие привязок.
		:type slave_id: int
		:return: Возвращает `True`, если найдены привязки.
		:rtype: bool
		"""

		if slave_id not in self.__cache:
			return False

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

		if master_id not in self.__cache:
			return False

		return bool(self.__cache[master_id].slaves)

	def save(self):
		"""Сохраняет данные связей в файл _.bonds.json_ в директории таблицы."""

		json.write(self.__bonds_file, self.to_dict(), atomic = True)

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта
		:rtype: dict
		"""

		return {note_id: bonds.to_dict() for note_id, bonds in self.__bonds.items() if bonds.has_bonds}

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

		self.__table.is_note_exists(master_id, not_found_error = True)
		self.__table.is_note_exists(slave_id, not_found_error = True)

		# Проверка наличия описания связи.
		self.__table.manifest.connections.bonds.get_bond_parameters(bond_name)

		bond: Bond = self.get_note_bonds(master_id).get_bond(bond_name, read_only = False)

		if slave_id in bond.slaves_id:
			bond.slaves_id.remove(slave_id)
			self.save()
			self.__remove_bond_from_cache(master_id, slave_id)

	def update_note_id(self, old_id: int, new_id: int):
		"""
		Обновляет ID записи во внутреннем хранилище.

		:param old_id: Старый ID записи.
		:type old_id: int
		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if old_id in self.__bonds:
			buffer: NoteBonds = self.__bonds.pop(old_id)
			buffer.set_note_id(new_id)
			self.__bonds[new_id] = buffer

		for note_bonds in self.__bonds.values():
			note_bonds.update_slaves_id(old_id, new_id)

		self.save()
		self.__refresh_bonds_cache()
