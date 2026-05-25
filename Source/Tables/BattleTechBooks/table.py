from .Structs import Era

from Source.Core.Base.Table import BaseTable

class Table(BaseTable):
	"""Таблица просмотров аниме."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#	

	@property
	def eras(self) -> tuple[Era]:
		"""Последовательность эпох BattleTech."""

		return self.__Eras

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта таблицы."""

		self.__Eras: tuple[Era] = (
			Era(-1, "Clan Homeworlds", None, None),
			Era(0, "Pre–Star League", None, 2570),
			Era(1, "Star League", 2571, 2780),
			Era(2.1, "Succession Wars. Early", 2781, 2900),
			Era(2.2, "Succession Wars. LosTech", 2901, 3019),
			Era(2.3, "Succession Wars. Renaissance", 3020, 3049),
			Era(3, "Clan Invasion", 3050, 3061),
			Era(4, "Civil War", 3062, 3067),
			Era(5, "Jihad", 3068, 3080),
			Era(6.1, "Dark Age. Republic", 3081, 3130),
			Era(6.2, "Dark Age", 3131, 3150),
			Era(7, "IlClan", 3151, None)
		)

