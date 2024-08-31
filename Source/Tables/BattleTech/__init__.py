from Source.Core.Base import Note, NoteCLI, Table, TableCLI 
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionStatus

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class BattleTech_NoteCLI(NoteCLI):
	"""CLI записи"""

	pass

class BattleTech_TableCLI(TableCLI):
	"""CLI таблицы."""

	pass
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class BattleTech_Note(Note):
	"""Базовая запись BattleTech."""

	pass

class BattleTech(Table):
	"""Базовая таблица BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "battletech"
	MANIFEST: dict = {
		"object": "table",
		"type": TYPE,
		"modules": [
			{
				"name": "books",
				"type": "battletech:books",
				"is_active": False
			},
			{
				"name": "mechs",
				"type": "battletech:mechs",
				"is_active": False
			},
			{
				"name": "sheets",
				"type": "battletech:sheets",
				"is_active": False
			},
			{
				"name": "sources",
				"type": "battletech:sources",
				"is_active": False
			}
		],
		"common": {
			"recycle_id": True
		}
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def eras(self) -> list[dict]:
		"""Эпохи BattleTech."""

		return [
			{
				"name": "Pre–Star League",
				"start_year": None,
				"end_year": 2570
			},
			{
				"name": "Star League",
				"start_year": 2571,
				"end_year": 2780
			},
			{
				"name": "Early Succession Wars",
				"start_year": 2781,
				"end_year": 2900
			},
			{
				"name": "Late Succession Wars",
				"start_year": 2901,
				"end_year": 3019
			},
			{
				"name": "Succession Wars. Renaissance",
				"start_year": 3020,
				"end_year": 3049
			},
			{
				"name": "Clan Invasion",
				"start_year": 3050,
				"end_year": 3061
			},
			{
				"name": "Civil War",
				"start_year": 3062,
				"end_year": 3067
			},
			{
				"name": "Jihad",
				"start_year": 3068,
				"end_year": 3080
			},
			{
				"name": "Republic Age",
				"start_year": 3081,
				"end_year": 3130
			},
			{
				"name": "Dark Age",
				"start_year": 3131,
				"end_year": 3150
			},
			{
				"name": "IlClan",
				"start_year": 3151,
				"end_year": None
			}
		]

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Note
		self._CLI = BattleTech_TableCLI