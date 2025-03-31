from dublib.Engine.Bus import ExecutionStatus as ES

class ExecutionStatus(ES):
	"""Отчёт о выполнении."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def close(self) -> bool:
		""""""

		return self.__Close
	
	@property
	def navigate(self) -> str | None:
		""""""

		return self.__Path
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, вызываемый после инициализации объекта."""

		self.__Path = None
		self.__Close = False

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def emit_close_signal(self, status: bool = True):
		"""Передаёт сигнал о закрытии объекта текущего уровня."""

		self.__Close = status

	def emit_navigate_signal(self, path: str | None):
		"""Передаёт сигнал о навигации по пути."""

		self.__Path = str(path) if path != None else None

	def merge(self, status: "ExecutionStatus", overwrite: bool = True):
		"""
		Выполняет слияние другого статуса с текущим объектом, объединяя списки сообщений и перезаписывая данные.
			status – статус для слиянитя;
			overwrite – переключает перезапись данных статуса.
		"""

		super().merge(status, overwrite)
		self.emit_close_signal(status.close)
		self.emit_navigate_signal(status.navigate)