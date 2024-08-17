from Source.CLI.Templates import Columns
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.StyledPrinter import Styles, StylesGroup, StyledPrinter, TextStyler
from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionError, ExecutionWarning, ExecutionStatus
from dublib.Methods.Filesystem import NormalizePath
from dublib.Methods.JSON import ReadJSON, WriteJSON
from dublib.CLI.Templates import Confirmation

import os

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class Anime_NoteCLI:
	"""Обработчик взаимодействий с записью через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.__Commands

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		CommandsList = list()

		Com = Command("delpart", "Remove part.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		CommandsList.append(Com)

		Com = Command("downpart", "Omit part in list.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		CommandsList.append(Com)

		Com = Command("editpart", "Edit part.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		Com.add_flag("a", description = "Mark part as announced.")
		Com.add_flag("s", description = "Mark part as skipped.")
		Com.add_flag("u", description = "Mark part as unwatched.")
		Com.add_flag("w", description = "Mark part as watched.")
		Com.add_key("comment", description = "Add comment to part.")
		Com.add_key("link", ParametersTypes.URL, description = "Attach link to part.")
		Com.add_key("name", description = "Set name of part.")
		Com.add_key("number", description = "Set number of part (not index).")
		Com.add_key("series", ParametersTypes.Number, description = "Set series count.")
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		Com.add_argument(ParametersTypes.Number, description = "Estimation.", important = True)
		CommandsList.append(Com)

		Com = Command("mark", "Set bookmark to series.")
		Com.add_argument(ParametersTypes.Number, description = "Part index.", important = True)
		Com.add_argument(ParametersTypes.Number, description = "Bookmark.", important = True)
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.")
		Com.add_argument(ParametersTypes.All, description = "Field name.", important = True)
		Com.add_argument(ParametersTypes.All, description = "Field value.")
		ComPos = Com.create_position("OPERATION", "Type of operation with metainfo.", important = True)
		ComPos.add_flag("set", description = "Create new or update exists field.")
		ComPos.add_flag("unset", description = "Remove field.")
		CommandsList.append(Com)

		Com = Command("newpart", "Create new part.")
		Com.add_argument(description = "Part type.", important = True)
		Com.add_flag("a", description = "Mark part as announced.")
		Com.add_flag("s", description = "Mark part as skipped.")
		Com.add_flag("u", description = "Mark part as unwatched.")
		Com.add_flag("w", description = "Mark part as watched.")
		Com.add_key("comment", description = "Add comment to part.")
		Com.add_key("link", ParametersTypes.URL, description = "Attach link to part.")
		Com.add_key("name", description = "Set name of part.")
		Com.add_key("number", description = "Set number of part (not index).")
		Com.add_key("series", ParametersTypes.Number, description = "Set series count.")
		CommandsList.append(Com)

		Com = Command("set", "Set note values.")
		Com.add_key("altname", description = "Alternative name.")
		Com.add_key("group", ParametersTypes.Number, description = "Group ID.")
		Com.add_key("name", description = "Note name.")
		Com.add_key("status", description = "View status.")
		Com.add_key("tag", description = "Tag.")
		CommandsList.append(Com)

		Com = Command("unset", "Remove alternative names or tags.")
		ComPos = Com.create_position("TARGET", "Target to remove.", important = True)
		ComPos.add_key("altname", ParametersTypes.All, "Index of alternative name or alternative name.")
		ComPos.add_key("tag", description = "Tag.")
		CommandsList.append(Com)

		Com = Command("uppart", "Raise part.")
		Com.add_argument(ParametersTypes.Number, "Part index.", important = True)
		CommandsList.append(Com)

		Com = Command("view", "View note in console.")
		CommandsList.append(Com)

		return CommandsList

	def __View(self):
		"""Выводит форматированные данные записи."""

		#---> Получение данных.
		#==========================================================================================#
		Group = self.__Table.get_group(self.__Note.group_id) if self.__Note.group_id else None
		GroupName = Group["name"] if Group and Group["name"] else None
		Parts = self.__Note.parts
		Options = self.__Table.manifest["viewer"]

		#---> Объявление литералов.
		#==========================================================================================#
		MSG_TotalProgress = f" ({self.__Note.progress}% viewed)" if self.__Note.progress else ""
		MSG_GroupName = f"@{self.__Note.group_id}" if not GroupName else f"@{GroupName}"

		#---> Вывод описания записи.
		#==========================================================================================#
		if self.__Note.name: StyledPrinter(self.__Note.name, decorations = [Styles.Decorations.Bold], end = False)
		print(f"{MSG_TotalProgress} {self.__Note.emoji_status}")
		if self.__Note.estimation: print(f"⭐ {self.__Note.estimation} / {self.__Table.max_estimation}")
		if self.__Note.another_names: StyledPrinter(f"ANOTHER NAMES: ", decorations = [Styles.Decorations.Bold])
		for AnotherName in self.__Note.another_names: StyledPrinter(f"    {AnotherName}", decorations = [Styles.Decorations.Italic])

		#---> Вывод классификаторов записи.
		#==========================================================================================#

		if self.__Note.group_id:
			StyledPrinter(f"GROUP: ", decorations = [Styles.Decorations.Bold], end = False)
			StyledPrinter(MSG_GroupName, decorations = [Styles.Decorations.Italic])

		if self.__Note.metainfo:
			StyledPrinter(f"METAINFO:", decorations = [Styles.Decorations.Bold])
			MetaInfo = self.__Note.metainfo
			
			for Key in MetaInfo.keys():
				CustomMetainfoMarker = "" if Key in self.__Table.metainfo_rules.keys() else "*"
				print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		if self.__Note.tags:
			StyledPrinter(f"TAGS: ", decorations = [Styles.Decorations.Bold], end = False)
			print(", ".join(self.__Note.tags))

		#---> Вывод частей записи.
		#==========================================================================================#

		if Parts:
			StyledPrinter(f"PARTS:", decorations = [Styles.Decorations.Bold])

			for PartIndex in range(0, len(Parts)):

				#---> Объявление литералов.
				#==========================================================================================#
				MSG_PartStatus = ""
				if "watched" in Parts[PartIndex].keys(): MSG_PartStatus = " ✅"
				if "announced" in Parts[PartIndex].keys(): MSG_PartStatus = " ℹ️"
				if "skipped" in Parts[PartIndex].keys(): MSG_PartStatus = " 🚫"
				MSG_Name = " " + Parts[PartIndex]["name"] if "name" in Parts[PartIndex].keys() and Parts[PartIndex]["name"] else ""
				MSG_Number = " " + str(Parts[PartIndex]["number"]) if "number" in Parts[PartIndex].keys() and Parts[PartIndex]["number"] else ""
				MSG_Indent = " " * len(str(PartIndex))
				MSG_Type = Parts[PartIndex]["type"]

				#---> Определение цвета части.
				#==========================================================================================#
				TextColor = None
				if Options["colorize"] and "✅" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Green)
				if Options["colorize"] and "ℹ️" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Cyan)
				if Options["colorize"] and "🚫" in MSG_PartStatus: TextColor = StylesGroup(text_color = Styles.Colors.Blue)

				if "series" in Parts[PartIndex].keys():

					#---> Объявление литералов.
					#==========================================================================================#
					MSG_Mark = str(Parts[PartIndex]["mark"]) + " / " if "mark" in Parts[PartIndex] else ""
					MSG_MarkIndicator = " ⏳" if MSG_Mark else ""
					MSG_Progress = " (" + str(int(Parts[PartIndex]["mark"] / Parts[PartIndex]["series"] * 100)) + "% viewed)" if MSG_Mark else ""
					MSG_Series = Parts[PartIndex]["series"]

					#---> Определение цвета части.
					#==========================================================================================#
					if Options["colorize"] and "⏳" in MSG_MarkIndicator: TextColor = StylesGroup(text_color = Styles.Colors.Yellow)

					#---> Вывод части.
					#==========================================================================================#
					StyledPrinter(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}{MSG_MarkIndicator}", styles = TextColor)
					if not Options["hide_single_series"] or Options["hide_single_series"] and MSG_Series and MSG_Series > 1: StyledPrinter(f"    {MSG_Indent}       {MSG_Mark}{MSG_Series} series{MSG_Progress}", styles = TextColor)

				else:
					StyledPrinter(f"    {PartIndex} ▸ {MSG_Type}{MSG_Number}:{MSG_Name}{MSG_PartStatus}", styles = TextColor)

				if Options["links"] and "link" in Parts[PartIndex].keys(): print(f"    {MSG_Indent}       🔗 " + Parts[PartIndex]["link"])
				if Options["comments"] and "comment" in Parts[PartIndex].keys(): print(f"    {MSG_Indent}       💭 " + Parts[PartIndex]["comment"])

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Anime_Table", note: "Anime_Note"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы;\n
			note – объектное представление записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table
		self.__Note = note
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		Status = None

		if command_data.name == "estimate":
			Status = self.__Note.estimate(command_data.arguments[0])

		if command_data.name == "delpart":
			Response = Confirmation("Are you sure to remove part?")
			
			if Response:
				Status = self.__Note.delete_part(int(command_data.arguments[0]))

		if command_data.name == "downpart":
			Status = self.__Note.down_part(int(command_data.arguments[0]))

		if command_data.name == "editpart":
			Data = dict()
			if "a" in command_data.flags: Data["announced"] = True
			if "w" in command_data.flags:
				Data["watched"] = True
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "s" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = True
			if "u" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if command_data.check_key("link"): Data["link"] = command_data.get_key_value("link")
			if command_data.check_key("comment"): Data["comment"] = command_data.get_key_value("comment")
			if command_data.check_key("name"): Data["name"] = command_data.get_key_value("name")
			if command_data.check_key("number"): Data["number"] = command_data.get_key_value("number")
			if command_data.check_key("series"): Data["series"] = command_data.get_key_value("series")
			Status = self.__Note.edit_part(int(command_data.arguments[0]), Data)

		if command_data.name == "mark":
			Status = self.__Note.set_mark(int(command_data.arguments[0]), int(command_data.arguments[1]))

		if command_data.name == "meta":
			Status = ExecutionStatus(0)
			
			if "set" in command_data.flags:
				Status = self.__Note.set_metainfo(command_data.arguments[0],  command_data.arguments[1])

			if "unset" in command_data.flags:
				Status = self.__Note.delete_metainfo(command_data.arguments[0])

		if command_data.name == "newpart":
			Data = dict()
			if "a" in command_data.flags: Data["announced"] = True
			if "w" in command_data.flags:
				Data["watched"] = True
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "s" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = True
			if "u" in command_data.flags:
				Data["watched"] = "*"
				Data["announced"] = "*"
				Data["skipped"] = "*"
			if "comment" in command_data.keys.keys(): Data["comment"] = command_data.keys["comment"]
			if "link" in command_data.keys.keys(): Data["link"] = command_data.keys["link"]
			if "name" in command_data.keys.keys(): Data["name"] = command_data.keys["name"]
			if "number" in command_data.keys.keys(): Data["number"] = command_data.keys["number"]
			if "series" in command_data.keys.keys(): Data["series"] = command_data.keys["series"]
			Status = self.__Note.add_part(command_data.arguments[0], Data)

		if command_data.name == "set":

			if "altname" in command_data.keys.keys():
				Status = self.__Note.add_another_name(command_data.keys["altname"])

			if "group" in command_data.keys.keys():
				Status = self.__Note.set_group(int(command_data.keys["group"]))

			if "name" in command_data.keys.keys():
				Status = self.__Note.rename(command_data.keys["name"])

			if "status" in command_data.keys.keys():
				Status = self.__Note.set_status(command_data.keys["status"])

			if "tag" in command_data.keys.keys():
				Status = self.__Note.add_tag(command_data.keys["tag"])

		if command_data.name == "unset":

			if "altname" in command_data.keys.keys():
				Status = self.__Note.delete_another_name(command_data.keys["altname"])

			if "tag" in command_data.keys.keys():
				Status = self.__Note.delete_tag(command_data.keys["tag"])

		if command_data.name == "uppart":
			Status = self.__Note.up_part(int(command_data.arguments[0]))

		if command_data.name == "view":
			self.__View()

		return Status

class Anime_TableCLI:
	"""Обработчик взаимодействий с таблицей через CLI."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.__Commands

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		CommandsList = list()

		Com = Command("delgroup", "Remove group.")
		Com.add_argument(ParametersTypes.Number, "Group ID.", important = True)
		CommandsList.append(Com)

		Com = Command("list", "Show list of notes.")
		Com.add_flag("r", "Reverse list.")
		Com.add_key("group", ParametersTypes.Number, "Group ID.")
		Com.add_key("sort", ParametersTypes.Text, "Column name.")
		Com.add_key("search", description = "Part of note name.")
		CommandsList.append(Com)

		Com = Command("new", "Create new note.")
		Com.add_flag("o", "Open new note.")
		CommandsList.append(Com)

		Com = Command("newgroup", "Create new group.")
		Com.add_argument(ParametersTypes.All, "Group name.", important = True)
		CommandsList.append(Com)

		Com = Command("search", "Search notes by part of name.")
		Com.add_argument(description = "Search query.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def __List(self, command_data: ParsedCommandData, search: str | None = None):
			Notes = list()
			Content = {
				"ID": [],
				"Status": [],
				"Name": [],
				"Estimation": [],
				"Group": []
			}
			SortBy = command_data.keys["sort"].title() if "sort" in command_data.keys.keys() else "ID"
			if SortBy == "Id": SortBy = SortBy.upper()
			if SortBy not in Content.keys(): return ExecutionError(-1, "bad_sorting_parameter")
			Reverse = command_data.check_flag("r")
			
			if self.__Table.notes:

				if "group" in command_data.keys.keys():

					for Note in self.__Table.notes:
						if Note.group_id == int(command_data.keys["group"]): Notes.append(Note)

				else: Notes = self.__Table.notes

				if search:
					print("Search:", TextStyler(search, text_color = Styles.Colors.Yellow))
					NotesCopy = list(Notes)
					SearchBuffer = list()

					for Note in NotesCopy:
						Names = list()
						if Note.name: Names.append(Note.name)
						if Note.another_names: Names += Note.another_names

						for Name in Names:
							if search.lower() in Name.lower(): SearchBuffer.append(Note)

					Notes = SearchBuffer
				
				for Note in Notes:
					Name = Note.name if Note.name else ""
					GroupName = self.__Table.get_group(Note.group_id)["name"] if self.__Table.get_group(Note.group_id) else f"@{Note.group_id}"
					if GroupName == "@None": GroupName = ""
					Status = Note.status
					if Status == "announced": Status = TextStyler(Status, text_color = Styles.Colors.Purple)
					if Status == "planned": Status = TextStyler(Status, text_color = Styles.Colors.Cyan)
					if Status == "watching": Status = TextStyler(Status, text_color = Styles.Colors.Yellow)
					if Status == "completed": Status = TextStyler(Status, text_color = Styles.Colors.Green)
					if Status == "dropped": Status = TextStyler(Status, text_color = Styles.Colors.Red)
					Content["ID"].append(Note.id)
					Content["Status"].append(Status)
					Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")
					Content["Estimation"].append(Note.estimation if Note.estimation else "")
					Content["Group"].append(GroupName)

				ContentBuffer = list(Content["Group"])
				while "" in ContentBuffer: ContentBuffer.remove("")
				if len(ContentBuffer) == 0: del Content["Group"]

				if len(Notes): Columns(Content, sort_by = SortBy, reverse = Reverse)
				else: print("Notes not found.")

			else:
				print("Table is empty.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Anime_Table"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table
		self.__Commands = self.__GenerateCommands()

	def execute(self, command_data: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		Status = None

		if command_data.name == "delgroup":
			Status = self.__Table.delete_group(command_data.arguments[0])

		if command_data.name == "list":
			self.__List(command_data)

		if command_data.name == "new":
			Status = self.__Table.create_note()
			if command_data.check_flag("o"): Status["open_note"] = True

		if command_data.name == "newgroup":
			Status = self.__Table.create_group(command_data.arguments[0])

		if command_data.name == "search":
			self.__List(command_data, command_data.arguments[0])

		return Status
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Anime_Note:
	"""Запись о просмотре аниме."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"another_names": [],
		"estimation": None,
		"status": None,
		"group": None,
		"tags": [],
		"metainfo": {},
		"parts": []
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> Anime_NoteCLI:
		"""Класс-обработчик CLI записи."""

		return self.__NoteCLI
	
	@property
	def id(self) -> int:
		"""Идентификатор."""

		return self.__ID
	
	@property
	def name(self) -> str | None:
		"""Название."""

		return self.__Data["name"]

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Data["another_names"]
	
	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		Statuses = {
			"announced": "ℹ️",
			"watching": "▶️",
			"completed": "✅",
			"dropped": "⛔",
			"planned": "🗓️",
			None: ""
		}

		return Statuses[self.__Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self.__Data["estimation"]

	@property
	def group_id(self) -> int | None:
		"""Идентификатор группы."""

		return self.__Data["group"]

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self.__Data["metainfo"]

	@property
	def parts(self) -> list[dict]:
		"""Список частей."""

		return list(self.__Data["parts"])

	@property
	def progress(self) -> float:
		"""Прогресс просмотра."""

		Progress = 0
		MaxProgress = 0
		CurrentProgress = 0
		Parts = self.parts

		if Parts:

			for Part in self.parts:

				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					if "series" in Part.keys() and Part["series"] != None:
						MaxProgress += Part["series"]

					else:
						MaxProgress += 1

			for Part in self.parts:

				if "announced" not in Part.keys() and "skipped" not in Part.keys():

					if "watched" in Part.keys() and "series" in Part.keys() and Part["series"] != None:
						CurrentProgress += Part["series"] if "mark" not in Part.keys() else Part["mark"]

					elif "watched" in Part.keys():
						CurrentProgress += 1

			Progress = round(float(CurrentProgress / MaxProgress * 100), 1)
			if str(Progress).endswith(".0"): Progress = int(Progress)

		return Progress

	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self.__Data["status"]

	@property
	def tags(self) -> list[str]:
		"""Список тегов."""

		return list(self.__Data["tags"])

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GetBasePart(self, part_type: str) -> dict:
		"""
		Возвращает стандартную словарную структуру части.
			part_type – тип части.
		"""

		if part_type in ["season"]: return {
			"type": part_type,
			"number": None,
			"series": None
		}

		if part_type in ["film", "special"]: return {
			"type": part_type,
			"name": None
		}

		if part_type in ["ONA", "OVA", "specials"]: return {
			"type": part_type,
			"series": None
		}

	def __ModifyPart(self, part: dict, data: dict) -> dict:
		"""
		Подставляет типовые значения в часть.
			part – словарное представление части;\n
			data – словарь данных для подстановки в часть.
		"""
		
		for Key in data.keys():

			if data[Key] == "*" and Key in part.keys():
				del part[Key]

			elif data[Key] != "*":
				part[Key] = data[Key]

			#---> Обработка частных случаев.
			#==========================================================================================#

			if "watched" in part.keys() and "mark" in part.keys(): del part["mark"]
			if "skipped" in part.keys() and "mark" in part.keys(): del part["mark"]

		return part

	def __UpdateStatus(self):
		"""Обновляет статус просмотра."""

		if self.__Data["status"] != "dropped":
			Progress = self.progress
			if Progress == None: self.__Data["status"] = None
			elif Progress == 100: self.__Data["status"] = "completed"
			else: self.__Data["status"] = "watching"

		if self.__Data["status"] == "completed":

			for Part in self.__Data["parts"]:

				if "announced" in Part.keys():
					self.__Data["status"] = "announced"
					break

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Anime_Table", note_id: int):
		"""
		Запись о просмотре аниме.
			table – объектное представление таблицы;\n
			note_id – идентификатор записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__ID = note_id
		self.__Table = table
		module = f"{table.module_name}/" if table.module_name else ""
		self.__Path = f"{table.storage}/{table.name}/{module}{self.__ID}.json"
		self.__Data = ReadJSON(self.__Path)
		self.__NoteCLI = Anime_NoteCLI(table, self)

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		Status = ExecutionStatus(0)

		try:
			self.__Data["name"] = name
			self.save()
			Status.message = "Name updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def save(self) -> ExecutionStatus:
		"""Сохраняет запись в локальный файл."""

		Status = ExecutionStatus(0)

		try:
			WriteJSON(self.__Path, self.__Data)

		except: Status = ERROR_UNKNOWN

		return Status

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus(0)

		try:

			if another_name not in self.__Data["another_names"]:
				self.__Data["another_names"].append(another_name)
				self.save()
				Status.message = "Another name added."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def add_part(self, part_type: str, data: dict) -> ExecutionStatus:
		"""
		Добавляет новую часть.
			part_type – тип части;\n
			data – данные для заполнения свойств части.
		"""

		Status = ExecutionStatus(0)

		try:
			Buffer = self.__GetBasePart(part_type)
			Buffer = self.__ModifyPart(Buffer, data)
			self.__Data["parts"].append(Buffer)
			self.__UpdateStatus()
			self.save()
			Status.message = "Part created."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def add_tag(self, tag: str) -> ExecutionStatus:
		"""
		Добавляет тег.
			tag – название тега.
		"""

		Status = ExecutionStatus(0)

		try:

			if tag not in self.__Data["tags"]:
				self.__Data["tags"].append(tag)
				self.save()
				Status.message = "Tag added."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def delete_another_name(self, another_name: int | str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название или его индекс.
		"""

		Status = ExecutionStatus(0)

		try:

			if another_name.isdigit() and another_name not in self.__Data["another_names"]:
				self.__Data["another_names"].pop(int(another_name))

			else:
				self.__Data["another_names"].remove(another_name)

			self.save()
			Status.message = "Another name removed."

		except IndexError:
			Status = ExecutionError(1, "incorrect_another_name_index")

		except:
			Status = ERROR_UNKNOWN

		return Status

	def delete_metainfo(self, key: str) -> ExecutionStatus:
		"""
		Удаляет метаданные.
			key – ключ метаданных.
		"""

		Status = ExecutionStatus(0)

		try:
			del self.__Data["metainfo"][key]
			self.save()
			Status.message = "Metainfo updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def delete_part(self, part_index: int) -> ExecutionStatus:
		"""
		Удаляет часть.
			index – индекс части.
		"""

		Status = ExecutionStatus(0)

		try:
			del self.__Data["parts"][part_index]
			self.__UpdateStatus()
			self.save()
			Status.message = "Part deleted."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def delete_tag(self, tag: int | str) -> ExecutionStatus:
		"""
		Удаляет тег.
			tag – тег или его индекс.
		"""

		Status = ExecutionStatus(0)

		try:

			if tag.isdigit():
				self.__Data["tags"].pop(int(tag))

			else:
				self.__Data["tags"].remove(tag)

			self.save()
			Status.message = "Tag removed."

		except IndexError:
			Status = ExecutionStatus(1, "incorrect_tag_index")

		except IndexError:
			Status = ERROR_UNKNOWN

		return Status

	def down_part(self, part_index: int) -> ExecutionStatus:
		"""
		Опускает часть на одну позицию вниз.
			part_index – индекс части.
		"""

		Status = ExecutionStatus(0)

		try:

			if part_index != len(self.__Data["parts"]) - 1:
				self.__Data["parts"].insert(part_index + 1, self.__Data["parts"].pop(part_index))
				self.save()
				Status.message = "Part downed."

			elif part_index == len(self.__Data["parts"]) - 1:
				Status = ExecutionWarning(1, "unable_down_last_part")

		except:
			Status = ERROR_UNKNOWN

		return Status

	def edit_part(self, part_index: int, data: dict) -> ExecutionStatus:
		"""
		Редактирует свойства части.
			part_index – индекс части;\n
			data – данные для обновления свойств части.
		"""

		Status = ExecutionStatus(0)

		try:
			self.__Data["parts"][part_index] = self.__ModifyPart(self.__Data["parts"][part_index], data)
			self.__UpdateStatus()
			self.save()
			Status.message = "Part edited."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus(0)

		try:

			if estimation <= self.__Table.manifest["max_estimation"]:
				self.__Data["estimation"] = estimation
				self.save()
				Status.message = "Estimation updated."

			else: Status = ExecutionError(1, "max_estimation_exceeded")

		except: Status = ERROR_UNKNOWN

		return Status

	def set_group(self, group_id: int) -> ExecutionStatus:
		"""
		Устанавливает принадлежность к группе.
			group_id – идентификатор группы.
		"""

		Status = ExecutionStatus(0)

		try:
			self.__Data["group"] = group_id
			self.__Table.add_group_element(group_id, self.__ID)
			self.save()
			Status.message = f"Note has been added to @{group_id} group."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_mark(self, part_index: int, mark: int) -> ExecutionStatus:
		"""
		Добавляет закладку на серию.
			part_index – индекс части;\n
			mark – номер серии для постановки закладки (0 для удаления закладки, номер последней серии для пометки всей части как просмотренной).
		"""

		Status = ExecutionStatus(0)

		try:

			if "series" in self.__Data["parts"][part_index].keys():

				if "watched" in self.__Data["parts"][part_index].keys():
					del self.__Data["parts"][part_index]["watched"]
					self.__Data["parts"][part_index]["mark"] = mark
					self.__UpdateStatus()
					self.save()
					Status.message = "Part marked as unseen."

				elif "skipped" in self.__Data["parts"][part_index].keys():
					del self.__Data["parts"][part_index]["skipped"]
					self.__Data["parts"][part_index]["mark"] = mark
					self.__UpdateStatus()
					self.save()
					Status.message = "Part marked as unskipped."

				else:

					if mark < self.__Data["parts"][part_index]["series"] and mark != 0:
						self.__Data["parts"][part_index]["mark"] = mark
						Status.message = "Mark updated."

					elif mark == self.__Data["parts"][part_index]["series"]:
						self.__Data["parts"][part_index]["watched"] = True
						if "mark" in self.__Data["parts"][part_index].keys(): del self.__Data["parts"][part_index]["mark"]
						Status.message = "Part marked as fully viewed."

					elif mark == 0:
						del self.__Data["parts"][part_index]["mark"]
						Status.message = "Mark removed."

					self.save()
					self.__UpdateStatus()

			else:
				Status = ExecutionError(-2, "only_series_supports_marks")

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_metainfo(self, key: str, metainfo: str) -> ExecutionStatus:
		"""
		Задаёт метаданные.
			key – ключ метаданных;\n
			metainfo – значение метаданных.
		"""

		Status = ExecutionStatus(0)

		try:
			if key in self.__Table.metainfo_rules.keys() and self.__Table.metainfo_rules[key] and metainfo not in self.__Table.metainfo_rules[key]: raise MetainfoBlocked()
			self.__Data["metainfo"][key] = metainfo
			self.__Data["metainfo"] = dict(sorted(self.__Data["metainfo"].items()))
			self.save()
			Status.message = "Metainfo updated."

		except MetainfoBlocked:
			Status = NOTE_ERROR_METAINFO_BLOCKED

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус.
			status – статус просмотра.
		"""

		Status = ExecutionStatus(0)
		Statuses = {
			"a": "announced",
			"w": "watching",
			"c": "completed",
			"d": "dropped",
			"p": "planned",
			"*": None
		}

		try:
			if status in Statuses.keys(): status = Statuses[status]
			self.__Data["status"] = status
			self.save()
			Status.message = "Status updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def up_part(self, part_index: int) -> ExecutionStatus:
		"""
		Поднимает часть на одну позицию вверх.
			part_index – индекс части.
		"""

		Status = ExecutionStatus(0)

		try:

			if part_index != 0:
				self.__Data["parts"].insert(part_index - 1, self.__Data["parts"].pop(part_index))
				self.save()
				Status.message = "Part upped."

			elif part_index == 0:
				Status = ExecutionWarning(1, "unable_up_first_part")

		except:
			Status = ERROR_UNKNOWN

		return Status

class Anime_Table:
	"""Таблица просмотров аниме."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "anime"
	MANIFEST: dict = {
		"version": 1,
		"type": TYPE,
		"recycle_id": False,
		"max_estimation": 10,
		"viewer": {
			"links": True,
			"comments": True,
			"colorize": True,
			"hide_single_series": True
		},
		"metainfo_rules": {
			"base": ["game", "manga", "novel", "original", "ranobe"]
		}
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def cli(self) -> Anime_TableCLI:
		"""Класс-обработчик CLI таблицы."""

		return self.__TableCLI

	@property
	def manifest(self) -> dict:
		"""Манифест таблицы."""

		return self.__Manifest.copy()	

	@property
	def modules(self) -> list[str]:
		"""Список типов модулей таблицы."""

		Modules = list()
		Manifest = self.manifest

		if "modules" in Manifest.keys():
			for Module in Manifest["modules"]: Modules.append(Module["type"])

		return Modules

	@property
	def module_name(self) -> str | None:
		"""Название модуля таблицы."""

		return self.__Module

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self.__Name

	@property
	def notes(self) -> list[Anime_Note]:
		"""Список записей."""

		return self.__Notes.values()
	
	@property
	def notes_id(self) -> list[int]:
		"""Список ID записей."""

		return self.__Notes.keys()

	@property
	def storage(self) -> str:
		"""Путь к хранилищу таблиц."""

		return self.__StorageDirectory

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self.__Manifest["max_estimation"]

	@property
	def metainfo_rules(self) -> dict:
		"""Правила метаданных."""

		return self.__Manifest["metainfo_rules"]

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Create(self):
		"""Создаёт таблицу."""

		if not os.path.exists(f"{self.__Path}"): os.makedirs(f"{self.__Path}")
		WriteJSON(f"{self.__Path}/manifest.json", self.MANIFEST)

	def __GenerateNewID(self, id_list: list[int]) -> int:
		"""
		Генерирует новый ID.
			id_list – список существующих ID.
		"""

		NewID = None
		if type(id_list) != list: id_list = list(id_list)

		if self.__Manifest["recycle_id"]:

			for ID in range(1, len(id_list) + 1):

				if ID not in id_list:
					NewID = ID
					break

		if not NewID: NewID = int(max(id_list)) + 1 if len(id_list) > 0 else 1

		return NewID

	def __GetNotesListID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		ListID = list()
		Files = os.listdir(f"{self.__Path}")
		Files = list(filter(lambda File: File.endswith(".json"), Files))

		for File in Files: 
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return ListID

	def __ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		self.__Notes[note_id] = Anime_Note(self, note_id)

	def __ReadNotes(self):
		"""Считывает содержимое всех записей."""

		ListID = self.__GetNotesListID()

		for ID in ListID:
			self.__ReadNote(ID)

	def __SaveGroups(self):
		"""Сохраняет описание группы в локальный файл."""

		if len(self.__Groups.keys()) > 0:
			WriteJSON(f"{self.__Path}/groups.json", self.__Groups)

		else:
			os.remove(f"{self.__Path}/groups.json")

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, storage: str, name: str, module: str | None = None, autocreation: bool = True):
		"""
		Таблица просмотров аниме.
			storage_path – директория хранения таблиц;\n
			name – название таблицы;\n
			module – название модуля таблицы;\n
			autocreation – указывает, нужно ли создавать таблицу при отсутствии таковой. 
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__StorageDirectory = NormalizePath(storage)
		self.__Name = name
		self.__Module = module
		self.__Path = f"{self.__StorageDirectory}/{name}" + (f"/{module}" if module else "")
		self.__Notes = dict()
		self.__Groups = dict()
		self.__TableCLI = Anime_TableCLI(self)
		self.__Manifest = None

		#---> Проверка существования или создание таблицы.
		#==========================================================================================#
		if not os.path.exists(f"{self.__Path}/manifest.json") and autocreation: self.__Create()
		elif not os.path.exists(f"{self.__Path}/manifest.json"): raise FileNotFoundError(f"{self.__Path}/manifest.json")

		#---> Загрузка данных.
		#==========================================================================================#
		self.__Manifest = ReadJSON(f"{self.__Path}/manifest.json")
		if self.__Manifest["type"] != self.TYPE: raise TypeError(f"Only \"{self.TYPE}\" type tables supported.")
		self.__ReadNotes()
		if os.path.exists(f"{self.__Path}/groups.json"): self.__Groups = ReadJSON(f"{self.__Path}/groups.json")

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		Status = ExecutionStatus(0)

		try:
			ID = self.__GenerateNewID(self.__Notes.keys())
			WriteJSON(f"{self.__Path}/{ID}.json", Anime_Note.BASE_NOTE)
			self.__ReadNote(ID)
			Status["note_id"] = ID
			Status.message = f"Note #{ID} created."

		except: Status = ERROR_UNKNOWN

		return Status
	
	def delete_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)
			del self.__Notes[note_id]
			os.remove(f"{self.__Path}/{note_id}.json")
			Status.message = f"Note #{note_id} deleted."

		except: Status = ERROR_UNKNOWN

		return Status

	def get_note(self, note_id: int) -> ExecutionStatus:
		"""
		Возвращает запись.
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)
			if note_id in self.__Notes.keys(): Status.value = self.__Notes[note_id]
			else: Status = TABLE_ERROR_MISSING_NOTE

		except: Status = ERROR_UNKNOWN

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		Status = ExecutionStatus(0)

		try:
			OldPath = self.__Path
			NewPath = self.__Path.split("/")
			NewPath[-1] = name
			self.__Path = "/".join(NewPath)
			os.rename(f"{OldPath}", f"{self.__Path}")
			self.__Name = name
			Status.message = "Table renamed."

		except: Status = ERROR_UNKNOWN

		return Status

	def save_manifest(self) -> ExecutionStatus:
		"""Обновляет файл манифеста."""

		Status = ExecutionStatus(0)

		try:
			WriteJSON(f"{self.__Path}/manifest.json", self.__Manifest)

		except: Status = ERROR_UNKNOWN

		return Status

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_group_element(self, group_id: int, note_id: int) -> ExecutionStatus:
		"""
		Добавляет идентификатор записи в элементы группы.
			group_id – идентификатор группы;\n
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			Group = self.get_group(group_id)
			if note_id not in Group["elements"]: Group["elements"].append(note_id)
			self.__SaveGroups()

		except: Status = ERROR_UNKNOWN

		return Status

	def create_group(self, name: str) -> ExecutionStatus:
		"""
		Создаёт группу для объединения записей.
			name – название группы.
		"""

		Status = ExecutionStatus(0)

		try:
			ID = self.__GenerateNewID(self.__Groups.keys())
			self.__Groups[str(ID)] = {
				"name": name,
				"elements": []
			}
			self.__SaveGroups()
			Status.message = f"Group @{ID} created."


		except:
			Status = ERROR_UNKNOWN

		return Status
		
	def delete_group(self, group_id: int) -> ExecutionStatus:
		"""
		Удаляет группу. 
			group_id – идентификатор группы.
		"""

		Status = ExecutionStatus(0)

		try:
			group_id = str(group_id)
			del self.__Groups[group_id]
			self.__SaveGroups()
			Status.message = f"Group @{group_id} removed."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def get_group(self, group_id: int) -> dict | None:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		Group = None
		group_id = str(group_id)
		if group_id in self.__Groups.keys(): Group = self.__Groups[group_id]

		return Group

	def get_group_notes(self, group_id: int) -> ExecutionStatus:
		"""
		Возвращает словарное представление группы.
			group_id – идентификатор группы.
		"""

		Status = ExecutionStatus(0)

		try:
			NotesList = list()
			
			for Note in self.notes:
				if Note.group == group_id: NotesList.append(Note)

			Status.value = NotesList
		
		except: Status = ERROR_UNKNOWN

		return NotesList