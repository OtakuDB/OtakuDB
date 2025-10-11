from Source.Core.Base import Manifest, ModuleData
from Source.Core.Base import Table

from os import PathLike

from Source.Interfaces.CLI.Base import *

#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class BattleTech(Table):
	"""Базовая таблица BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "battletech"

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def eras(self) -> list[dict]:
		"""Эпохи BattleTech."""

		return [
			{
				"index": -1,
				"name": "Clan Homeworlds",
				"start_year": None,
				"end_year": None
			},
			{
				"index": 0,
				"name": "Pre–Star League",
				"start_year": None,
				"end_year": 2570
			},
			{
				"index": 1,
				"name": "Star League",
				"start_year": 2571,
				"end_year": 2780
			},
			{
				"index": 2.1,
				"name": "Succession Wars. Early",
				"start_year": 2781,
				"end_year": 2900
			},
			{
				"index": 2.2,
				"name": "Succession Wars. LosTech",
				"start_year": 2901,
				"end_year": 3019
			},
			{
				"index": 2.3,
				"name": "Succession Wars. Renaissance",
				"start_year": 3020,
				"end_year": 3049
			},
			{
				"index": 3,
				"name": "Clan Invasion",
				"start_year": 3050,
				"end_year": 3061
			},
			{
				"index": 4,
				"name": "Civil War",
				"start_year": 3062,
				"end_year": 3067
			},
			{
				"index": 5,
				"name": "Jihad",
				"start_year": 3068,
				"end_year": 3080
			},
			{
				"index": 6.1,
				"name": "Dark Age. Republic",
				"start_year": 3081,
				"end_year": 3130
			},
			{
				"index": 6.2,
				"name": "Dark Age",
				"start_year": 3131,
				"end_year": 3150
			},
			{
				"index": 7,
				"name": "IlClan",
				"start_year": 3151,
				"end_year": None
			}
		]

	@property
	def eras_indexes(self) -> list[int, float]:
		"""Индексы эпох BattleTech."""

		Indexes = list()
		for Era in self.eras: Indexes.append(Era["index"])

		return Indexes
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyManifest(self, path: PathLike) -> Manifest:
		"""
		Возвращает пустой манифест. Переопределите для настройки.

		:param path: Путь к каталогу таблицы.
		:type path: PathLike
		:return: Пустой манифест.
		:rtype: Manifest
		"""

		Buffer = super()._GetEmptyManifest(path)
		Buffer.set_type(self.TYPE)
		Buffer.add_module(ModuleData(Buffer, "books", "battletech:books"))
		Buffer.add_module(ModuleData(Buffer, "mechs", "battletech:mechs"))
		Buffer.add_module(ModuleData(Buffer, "sources", "battletech:sources"))

		return Buffer