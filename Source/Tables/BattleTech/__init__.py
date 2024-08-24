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
	def eras(self) -> dict:
		"""Эпохи BattleTech."""

		return {
			0: "Pre–Star League",
			1: "Star League",
			2: "Succession Wars",
			3: "Clan Invasion",
			4: "Civil War",
			5: "Jihad",
			6: "Dark Age",
			7: "ilClan"
		}

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Note
		self._CLI = BattleTech_TableCLI