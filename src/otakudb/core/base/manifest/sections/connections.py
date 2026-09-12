from dataclasses import dataclass

from .... import exceptions
from ._base import BaseSection

#==========================================================================================#
# >>>>> ПАРАМЕТРЫ СВЯЗЕЙ <<<<< #
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

class BondsParameters(BaseSection):
	"""Параметры связей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def names(self) -> tuple[str, ...]:
		"""Последовательность имён связей."""

		return tuple(self.__Bonds.keys())

	@property
	def parameters(self) -> tuple[BondParameters, ...]:
		"""Последовательность параметров связей."""

		return tuple(self.__Bonds.values())

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Bonds: dict[str, BondParameters] = {}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def create_bond_parameters(self, bond_name: str, description: str | None = None, count: int | None = None, save: bool = True):
		"""
		Создаёт определение параметров связи.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param description: Описание связи.
		:type description: str | None
		:param count: Максимальное количество прикрепляемых записей. При `None` неограничено. 
		:type count: int | None
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises BondAlreadyDescribedError: Связь уже описана.
		"""

		if bond_name in self.__Bonds: raise exceptions.note.BondAlreadyDescribedError(bond_name)
		self.__Bonds[bond_name] = BondParameters(bond_name, description, count)
		if save: self.save()

	def get_bond_parameters(self, bond_name: str) -> BondParameters:
		"""
		Возвращает параметры связи.

		:param bond_name: Имя связи.
		:type bond_name: str
		:return: Параметры соединения.
		:rtype: ConnectionParameters
		:raises BondNotDescribedError: Связь не описана.
		"""

		if bond_name not in self.__Bonds: raise exceptions.note.BondNotDescribedError(bond_name)

		return self.__Bonds[bond_name]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Bonds = {}
		for Key in data.keys(): self.create_bond_parameters(Key, data.get("description"), data.get("count"), save = False)

	def remove_bond_parameters(self, bond_name: str, save: bool = True):
		"""
		Удаляет параметры связи.

		:param bond_name: Имя связи.
		:type bond_name: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises BondNotDescribedError: Связь не описана.
		"""

		if bond_name in self.__Bonds: raise exceptions.note.BondNotDescribedError(bond_name)
		del self.__Bonds[bond_name]
		if save: self.save()

	def to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, dict]
		"""

		return {Bond.name: Bond.to_dict() for Bond in self.__Bonds.values()}

#==========================================================================================#
# >>>>> ПАРАМЕТРЫ ГИПЕРССЫЛОК <<<<< #
#==========================================================================================#

class HyperlinksParameters(BaseSection):
	"""Параметры гиперссылок."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Hyperlinks = {}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Hyperlinks = data

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return self.__Hyperlinks.copy()

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ConnectionsSection(BaseSection):
	"""Параметры соединений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def bonds(self) -> BondsParameters:
		"""Параметры соединений."""

		return self.__Bonds
	
	@property
	def hyperlinks(self) -> HyperlinksParameters:
		"""Параметры гиперссылок."""

		return self.__Hyperlinks

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _post_init(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Bonds = BondsParameters(self._Manifest)
		self.__Hyperlinks = HyperlinksParameters(self._Manifest)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def parse(self, data: dict[str, dict]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict[str, dict]
		"""

		self.__Bonds.parse(data.get("bonds") or {})
		self.__Hyperlinks.parse(data.get("hyperlinks") or {})

	def to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, dict]
		"""

		return {
			"bonds": self.__Bonds.to_dict(),
			"hyperlinks": self.__Hyperlinks.to_dict()
		}
