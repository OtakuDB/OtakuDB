from dataclasses import dataclass

from ..... import exceptions
from .._base import BaseSection

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class BondParameters:
	"""Параметры связи."""

	name: str
	description: str | None
	count: int | None

	def to_dict(self) -> dict[str, int | str | None]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, int | str | None]
		"""

		return {
			"description": self.description,
			"count": self.count
		}

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class BondsParameters(BaseSection):
	"""Параметры связей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def names(self) -> tuple[str, ...]:
		"""Последовательность имён связей."""

		return tuple(self.__bonds.keys())

	@property
	def parameters(self) -> tuple[BondParameters, ...]:
		"""Последовательность параметров связей."""

		return tuple(self.__bonds.values())

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__bonds.clear()

		for Key in data.keys():
			self.create_bond_parameters(Key, data.get("description"), data.get("count"))

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__bonds: dict[str, BondParameters] = {}

	def _to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, dict]
		"""

		return {bond.name: bond.to_dict() for bond in self.__bonds.values()}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def create_bond_parameters(self, bond_name: str, description: str | None = None, count: int | None = None):
		"""
		Создаёт определение параметров связи.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param description: Описание связи.
		:type description: str | None
		:param count: Максимальное количество прикрепляемых записей. При `None` неограничено. 
		:type count: int | None
		:raises BondAlreadyDescribedError: Связь уже описана.
		"""

		if bond_name in self.__bonds:
			raise exceptions.note.bonds.BondAlreadyDescribedError(bond_name)

		self.__bonds[bond_name] = BondParameters(bond_name, description, count)

	def get_bond_parameters(self, bond_name: str) -> BondParameters:
		"""
		Возвращает параметры связи.

		:param bond_name: Имя связи.
		:type bond_name: str
		:return: Параметры соединения.
		:rtype: ConnectionParameters
		:raises BondNotDescribedError: Связь не описана.
		"""

		if bond_name not in self.__bonds:
			raise exceptions.note.bonds.BondNotDescribedError(bond_name)

		return self.__bonds[bond_name]

	def remove_bond_parameters(self, bond_name: str):
		"""
		Удаляет параметры связи.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises BondNotDescribedError: Связь не описана.
		"""

		if bond_name in self.__bonds:
			raise exceptions.note.bonds.BondNotDescribedError(bond_name)

		del self.__bonds[bond_name]

