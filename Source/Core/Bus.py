from dublib.Engine.Bus import ExecutionStatus as ES

from dataclasses import dataclass

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass
class CreateTable:
	name: str | None = None
	type: str | None = None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class ExecutionStatus(ES):
	"""Отчёт о выполнении."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def close(self) -> bool:
		"""Статус сигнала закрытия текущего объекта."""

		return self.__Close
	
	@property
	def create_table(self) -> CreateTable | None:
		"""Название инициализируемого модуля."""

		return self.__CreateTable
	
	@property
	def initialize_module(self) -> str | None:
		"""Тип инициализируемого модуля."""

		return self.__InitializeModule

	@property
	def navigate(self) -> str | None:
		"""Путь для перехода."""

		return self.__Path
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, вызываемый после инициализации объекта."""

		self.__Path = None
		self.__Close = False
		self.__CreateTable = None
		self.__InitializeModule = None

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def emit_close(self, status: bool = True):
		"""Передаёт сигнал о закрытии объекта текущего уровня."""

		self.__Close = status

	def emit_create_table(self, name: str, type: str):
		"""
		Передаёт сигнал о создании таблицы.
			name – название таблицы;\n
			type – тип таблицы.
		"""

		self.__CreateTable = CreateTable(name, type)

	def emit_initialize_module(self, type: str):
		"""
		Передаёт сигнал об инициализации модуля.
			name – название модуля.
		"""

		self.__InitializeModule = type

	def emit_navigate(self, path: str | None):
		"""Передаёт сигнал о навигации по пути."""

		self.__Path = str(path) if path != None else None

	def merge(self, status: "ExecutionStatus", overwrite: bool = True):
		"""
		Выполняет слияние другого статуса с текущим объектом, объединяя списки сообщений и перезаписывая данные.
			status – статус для слиянитя;
			overwrite – переключает перезапись данных статуса.
		"""

		super().merge(status, overwrite)
		self.emit_close(status.close)
		if status.create_table: self.emit_create_table(status.create_table.name, status.create_table.type)
		self.emit_initialize_module(status.initialize_module)
		self.emit_navigate(status.navigate)