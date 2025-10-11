from Source.Core.Base import Table

from Source.Interfaces.CLI.Base import *

#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Otaku(Table):
	"""Базовая таблица Otaku."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "otaku"
	MANIFEST: dict = {
		"object": "table",
		"type": TYPE,
		"modules": [
			{
				"name": "anime",
				"type": "otaku:anime",
				"is_active": False
			},
			{
				"name": "manga",
				"type": "otaku:manga",
				"is_active": False
			},
			{
				"name": "ranobe",
				"type": "otaku:ranobe",
				"is_active": False
			},
			{
				"name": "visual_novels",
				"type": "otaku:visual_novels",
				"is_active": False
			}
		]
	}