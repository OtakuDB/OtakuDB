from ._Base import BaseContainer

from Source.Core import Exceptions

from dataclasses import dataclass

#==========================================================================================#
# >>>>> ПАРАМЕТРЫ ЛОКАЛЬНЫХ СВЯЗЕЙ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class ConnectionParameters:
	"""Параметры соединения."""

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

class Local(BaseContainer):
	"""Параметры локальных соединений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def connections(self) -> tuple[ConnectionParameters]:
		"""Последовательность данных соединений."""

		return tuple(self.__Connections.values())

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Connections: dict[str, ConnectionParameters] = dict()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def add_connection(self, connection: str, description: str | None = None, count: int | None = None, save: bool = True):
		"""
		Создаёт определение параметров локального соединения.

		:param connection: Имя соединения.
		:type connection: str
		:param description: Описание соединения.
		:type description: str | None
		:param count: Максимальное количество прикрепляемых записей. При `None` неограничено. 
		:type count: int | None
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises LocalBindAlreadyDescribed: Соединение уже описано.
		"""

		if connection in self.__Connections: raise Exceptions.Note.LocalBindAlreadyDescribed(connection)
		self.__Connections[connection] = ConnectionParameters(connection, description, count)
		if save: self.save()

	def get_connection_parameters(self, connection: str) -> ConnectionParameters:
		"""
		Возвращает параметры соединения.

		:param connection: Имя соединения.
		:type connection: str
		:return: Параметры соединения.
		:rtype: ConnectionParameters
		:raises LocalBindNotDescribed: Соединение не описано.
		"""

		if connection not in self.__Connections: raise Exceptions.Note.LocalBindNotDescribed(connection)

		return self.__Connections[connection]

	def parse(self, data: dict[str, dict]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Connections = dict()
		for Key in data.keys(): self.add_connection(Key, data.get("description"), data.get("count"), save = False)

	def remove_connection(self, connection: str, save: bool = True):
		"""
		Удаляет параметры соединения.

		:param connection: Имя соединения.
		:type connection: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises LocalBindNotDescribed: Соединение не описано.
		"""

		if connection in self.__Connections: raise Exceptions.Note.LocalBindNotDescribed(connection)
		del self.__Connections[connection]
		if save: self.save()

	def to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, dict]
		"""

		return {Connection.name: Connection.to_dict() for Connection in self.__Connections.values()}

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Binder(BaseContainer):
	"""Параметры соединений."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def local(self) -> Local:
		"""Параметры локальных соединений."""

		return self.__Local

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__Local = Local(self._Manifest)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def parse(self, data: dict[str, dict]):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict[str, dict]
		"""

		self.__Local.parse(data.get("local") or dict())

	def to_dict(self) -> dict[str, dict]:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict[str, dict]
		"""

		return {
			"local": self.__Local.to_dict(),
			"hyperlinks": dict()
		}
