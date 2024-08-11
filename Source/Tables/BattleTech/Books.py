from Source.CLI.Templates import Columns
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.StyledPrinter import Styles, StyledPrinter, TextStyler
from dublib.Engine.Bus import ExecutionError, ExecutionStatus
from dublib.Methods.JSON import ReadJSON, WriteJSON

import os

#==========================================================================================#
# >>>>> ОБРАБОТЧИКИ ВЗАИМОДЕЙСТВИЙ С ТАБЛИЦЕЙ <<<<< #
#==========================================================================================#

class BattleTech_Books_NoteCLI:
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

	def __ErasToNames(self, eras_id: list[int]) -> list[str]:
		"""
		Преобразует список ID эпох BattleTech в список названий.
			eras_id – список ID.
		"""

		Names = list()
		for EraID in eras_id: Names.append(self.__Table.eras[EraID])

		return Names

	def __GenerateCommands(self) -> list[Command]:
		"""Генерирует список команд."""

		CommandsList = list()

		Com = Command("comment", "Set comment to note.")
		Com.add_argument(description = "Comment text or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		Com.add_argument(ParametersTypes.Number, description = "Estimation.", important = True)
		CommandsList.append(Com)

		Com = Command("link", "Attach link to note.")
		Com.add_argument(description = "URL or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("mark", "Set bookmark.")
		Com.add_argument(ParametersTypes.Number, description = "Page number or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.")
		Com.add_argument(ParametersTypes.All, description = "Field name.", important = True)
		Com.add_argument(ParametersTypes.All, description = "Field value.")
		ComPos = Com.create_position("OPERATION", "Type of operation with metainfo.", important = True)
		ComPos.add_flag("set", description = "Create new or update exists field.")
		ComPos.add_flag("unset", description = "Remove field.")
		CommandsList.append(Com)

		Com = Command("set", "Set note values.")
		Com.add_key("altname", description = "Alternative name.")
		Com.add_key("era", ParametersTypes.Number, description = "Era ID.")
		Com.add_key("localname", description = "Localized name.")
		Com.add_key("name", description = "Note name.")
		Com.add_key("status", description = "View status.")
		CommandsList.append(Com)

		Com = Command("unset", "Remove alternative names or eras.")
		ComPos = Com.create_position("TARGET", "Target to remove.", important = True)
		ComPos.add_key("altname", ParametersTypes.All, "Index of alternative name or alternative name.")
		Com.add_key("era", ParametersTypes.Number, description = "Era ID.")
		CommandsList.append(Com)

		Com = Command("view", "View note in console.")
		CommandsList.append(Com)

		return CommandsList

	def __View(self):
		"""Выводит форматированные данные записи."""

		#---> Получение данных.
		#==========================================================================================#
		UsedName = None
		AnotherNames = list()

		if self.__Note.localized_name:
			UsedName = self.__Note.localized_name
			AnotherNames.append(self.__Note.name)

		else:
			UsedName = self.__Note.name

		AnotherNames += self.__Note.another_names

		#---> Вывод описания записи.
		#==========================================================================================#
		if UsedName: StyledPrinter(UsedName, decorations = [Styles.Decorations.Bold], end = False)
		print(f" {self.__Note.emoji_status}")
		if self.__Note.estimation: print(f"⭐ {self.__Note.estimation} / {self.__Table.max_estimation}")
		if self.__Note.bookmark: print(f"🔖 {self.__Note.bookmark} page")
		if self.__Note.comment: print(f"💭 {self.__Note.comment}")
		if self.__Note.link: print(f"🔗 {self.__Note.link}")
		if AnotherNames: StyledPrinter(f"ANOTHER NAMES: ", decorations = [Styles.Decorations.Bold])
		for AnotherName in AnotherNames: StyledPrinter(f"    {AnotherName}", decorations = [Styles.Decorations.Italic])

		#---> Вывод классификаторов записи.
		#==========================================================================================#

		if self.__Note.eras:
			StyledPrinter(f"ERAS: ", decorations = [Styles.Decorations.Bold])
			for Era in self.__ErasToNames(self.__Note.eras): StyledPrinter(f"    {Era}", decorations = [Styles.Decorations.Italic])

		if self.__Note.metainfo:
			StyledPrinter(f"METAINFO:", decorations = [Styles.Decorations.Bold])
			MetaInfo = self.__Note.metainfo
			
			for Key in MetaInfo.keys():
				CustomMetainfoMarker = "" if Key in self.__Table.metainfo_rules.keys() else "*"
				print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BattleTech_Books_Table", note: "BattleTech_Books_Note"):
		"""
		Обработчик взаимодействий с таблицей через CLI.
			table – объектное представление таблицы;
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

		if command_data.name == "comment":
			Status = self.__Note.set_comment(command_data.arguments[0])

		if command_data.name == "estimate":
			Status = self.__Note.estimate(command_data.arguments[0])

		if command_data.name == "link":
			Status = self.__Note.set_link(command_data.arguments[0])

		if command_data.name == "mark":
			Status = self.__Note.set_bookmark(command_data.arguments[0])

		if command_data.name == "meta":
			Status = ExecutionStatus(0)
			
			if "set" in command_data.flags:
				Status = self.__Note.set_metainfo(command_data.arguments[0],  command_data.arguments[1])

			if command_data.check_flag("unset"):
				Status = self.__Note.delete_metainfo(command_data.arguments[0])

		if command_data.name == "set":

			if "altname" in command_data.keys.keys():
				Status = self.__Note.add_another_name(command_data.keys["altname"])

			if command_data.check_key("era"):
				Status = self.__Note.add_era(command_data.get_key_value("era"))

			if "localname" in command_data.keys.keys():
				Status = self.__Note.rename(command_data.keys["localname"], localized = True)

			if "name" in command_data.keys.keys():
				Status = self.__Note.rename(command_data.keys["name"])

			if "status" in command_data.keys.keys():
				Status = self.__Note.set_status(command_data.keys["status"])

		if command_data.name == "unset":

			if command_data.check_key("altname"):
				Status = self.__Note.delete_another_name(command_data.get_key_value("altname"))

			if command_data.check_key("era"):
				Status = self.__Note.delete_era(command_data.get_key_value("era"))

		if command_data.name == "view":
			self.__View()

		return Status

class BattleTech_Books_TableCLI:
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

		Com = Command("eras", "Show list of BattleTech eras.")
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
				"Author": [],
				"Estimation": []
			}
			SortBy = command_data.keys["sort"].title() if "sort" in command_data.keys.keys() else "ID"
			if SortBy == "Id": SortBy = SortBy.upper()
			if SortBy not in Content.keys(): return ExecutionError(-1, "bad_sorting_parameter")
			Reverse = command_data.check_flag("r")
			
			if self.__Table.notes:
				Notes = self.__Table.notes

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
					Name = Note.localized_name if Note.localized_name else Note.name
					if not Name: Name = ""
					Author = Note.metainfo["author"] if "author" in Note.metainfo.keys() else ""
					Status = Note.status
					if Status == "announced": Status = TextStyler(Status, text_color = Styles.Colors.Purple)
					if Status == "collected": Status = TextStyler(Status, text_color = Styles.Colors.Blue)
					if Status == "reading": Status = TextStyler(Status, text_color = Styles.Colors.Yellow)
					if Status == "completed": Status = TextStyler(Status, text_color = Styles.Colors.Green)
					if Status == "dropped": Status = TextStyler(Status, text_color = Styles.Colors.Red)
					if Status == "skipped": Status = TextStyler(Status, text_color = Styles.Colors.Cyan)
					Content["ID"].append(Note.id)
					Content["Status"].append(Status)
					Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")
					Content["Author"].append(Author)
					Content["Estimation"].append(Note.estimation if Note.estimation else "")

				if len(Notes): Columns(Content, sort_by = SortBy, reverse = Reverse)
				else: print("Notes not found.")

			else:
				print("Table is empty.")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BattleTech_Books_Table"):
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

		if command_data.name == "eras":
			Eras = self.__Table.eras
			for EraID in Eras.keys(): print(f"    {EraID}: {Eras[EraID]}")

		if command_data.name == "list":
			self.__List(command_data)

		if command_data.name == "new":
			Status = self.__Table.create_note()
			if command_data.check_flag("o"): Status["open_note"] = True

		if command_data.name == "search":
			self.__List(command_data, command_data.arguments[0])

		return Status
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class BattleTech_Books_Note:
	"""Запись о прочтении книги по вселенной BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"localized_name": None,
		"another_names": [],
		"eras": [],
		"estimation": None,
		"comment": None,
		"link": None,
		"bookmark": None,
		"status": None,
		"metainfo": {}
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def another_names(self) -> list[str]:
		"""Список альтернативных названий."""

		return self.__Data["another_names"]

	@property
	def bookmark(self) -> int | None:
		"""Закладка."""

		return self.__Data["bookmark"]

	@property
	def cli(self) -> BattleTech_Books_NoteCLI:
		"""Обработчик CLI записи."""

		return self.__NoteCLI

	@property
	def comment(self) -> str | None:
		"""Комментарий."""

		return self.__Data["comment"]

	@property
	def eras(self) -> list[int]:
		"""Список ID эпох BattleTech."""

		return self.__Data["eras"]

	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		Statuses = {
			"announced": "ℹ️",
			"reading": "📖",
			"completed": "✅",
			"dropped": "⛔",
			"collected": "📦",
			"skipped": "🚫",
			None: ""
		}

		return Statuses[self.__Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self.__Data["estimation"]

	@property
	def id(self) -> int:
		"""Идентификатор."""

		return self.__ID

	@property
	def link(self) -> str | None:
		"""Ссылка."""

		return self.__Data["link"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self.__Data["localized_name"]

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self.__Data["metainfo"]
	
	@property
	def name(self) -> str | None:
		"""Название."""

		return self.__Data["name"]

	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self.__Data["status"]

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "BattleTech_Books_Table", note_id: int):
		"""
		Запись просмотра медиаконтента.
			table – объектное представление таблицы;
			note_id – идентификатор записи.
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__ID = note_id
		self.__Path = f"{table.directory}/{table.name}/books/{self.__ID}.json"
		self.__Table = table
		self.__Data = ReadJSON(self.__Path)
		self.__NoteCLI = BattleTech_Books_NoteCLI(table, self)
	
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

	def add_era(self, era: int) -> ExecutionStatus:
		"""
		Добавляет эру.
			era – ID эры.
		"""

		Status = ExecutionStatus(0)

		try:

			if era in self.__Table.eras.keys():

				if era not in self.__Data["eras"]:
					self.__Data["eras"].append(era)
					self.__Data["eras"] = sorted(self.__Data["eras"])
					self.save()

				Status.message = "Era added."

			else:
				Status = ExecutionError(-2, "incorrect_era_id")

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

	def delete_era(self, era: int) -> ExecutionStatus:
		"""
		Удаляет эру.
			era – ID эры.
		"""

		Status = ExecutionStatus(0)

		try:

			if era in self.__Table.eras.keys():

				if era in self.__Data["eras"]:
					self.__Data["eras"].remove(era)
					self.save()
					Status.message = "Era removed."

			else:
				Status = ExecutionError(-2, "incorrect_era_id")

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

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus(0)

		try:

			if estimation <= self.__Table.options["max_estimation"]:
				self.__Data["estimation"] = estimation
				self.save()
				Status.message = "Estimation updated."

			else:
				Status = ExecutionError(1, "max_estimation_exceeded")

		except:
			Status = ERROR_UNKNOWN

		return Status

	def rename(self, name: str, localized: bool = False) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		Status = ExecutionStatus(0)

		try:
			
			if localized:
				self.__Data["localized_name"] = name
				Status.message = "Localized name updated."

			else:
				self.__Data["name"] = name
				Status.message = "Name updated."
				
			self.save()

		except:
			Status = ERROR_UNKNOWN

		return Status

	def save(self):
		"""Сохраняет запись в локальный файл."""

		WriteJSON(self.__Path, self.__Data)

	def set_bookmark(self, bookmark: int) -> ExecutionStatus:
		"""
		Задаёт заладку.
			bookmark – номер страницы.
		"""

		Status = ExecutionStatus(0)

		try:
			if bookmark == "*": bookmark = None
			self.__Data["bookmark"] = bookmark
			self.save()
			Status.message = "Bookmark updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_comment(self, comment: str) -> ExecutionStatus:
		"""
		Задаёт комментарий.
			comment – комментарий.
		"""

		Status = ExecutionStatus(0)

		try:
			if comment == "*": comment = None
			self.__Data["comment"] = comment
			self.save()
			Status.message = "Comment updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_link(self, link: str) -> ExecutionStatus:
		"""
		Задаёт ссылку.
			link – ссылка.
		"""

		Status = ExecutionStatus(0)

		try:
			if link == "*": link = None
			self.__Data["link"] = link
			self.save()
			Status.message = "Link updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_metainfo(self, key: str, metainfo: str) -> ExecutionStatus:
		"""
		Задаёт метаданные.
			key – ключ метаданных;
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
			"r": "reading",
			"c": "completed",
			"d": "dropped",
			"i": "collected",
			"s": "skipped",
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

class BattleTech_Books_Table:
	"""Таблица прочтения книг по вселенной BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	type = "battletech:books"

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def eras(self) -> list[str]:
		"""Эпохи BattleTech."""

		return self.__Eras

	@property
	def cli(self) -> BattleTech_Books_TableCLI:
		"""Обработчик CLI таблицы."""

		return self.__TableCLI

	@property
	def directory(self) -> str:
		"""Путь к каталогу таблицы."""

		return self.__StorageDirectory

	@property
	def id(self) -> list[BattleTech_Books_Note]:
		"""Идентификатор таблицы."""

		return self.__Notes.values()

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self.__Options["max_estimation"]

	@property
	def metainfo_rules(self) -> dict:
		"""Правила метаданных."""

		return self.__Options["metainfo_rules"]

	@property
	def module(self) -> str:
		"""Название модуля."""

		return self.__Module

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self.__Name

	@property
	def notes(self) -> list[BattleTech_Books_Note]:
		"""Список записей."""

		return self.__Notes.values()
	
	@property
	def notes_id(self) -> list[int]:
		"""Список ID записей."""

		return self.__Notes.keys()

	@property
	def options(self) -> dict:
		"""Словарь опций таблицы."""

		return self.__Options.copy()	

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Create(self):
		"""Создаёт каталог и манифест таблицы."""

		if not os.path.exists(self.__Path): os.makedirs(self.__Path)
		WriteJSON(f"{self.__Path}/manifest.json", self.__Options)

	def __GetNewID(self, container: dict) -> int:
		"""
		Генерирует ID для новой записи или группы.
			container – контейнер записи или группы.
		"""

		NewID = None

		if self.__Options["recycle_id"]:
			ListID = container.keys()

			for ID in range(1, len(ListID) + 1):

				if ID not in ListID:
					NewID = ID
					break

		if not NewID:
			NewID = int(max(container.keys())) + 1 if len(container.keys()) > 0 else 1

		return NewID

	def __GetNotesListID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		ListID = list()
		Files = os.listdir(f"{self.__StorageDirectory}/{self.__Name}")
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

		self.__Notes[note_id] = BattleTech_Books_Note(self, note_id)

	def __ReadNotes(self):
		"""Считывает содержимое всех записей."""

		ListID = self.__GetNotesListID()
		for ID in ListID: self.__ReadNote(ID)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, storage_path: str, name: str, autocreation: bool = True):
		"""
		Таблица прочтения книг по вселенной BattleTech.
			storage_path – директория хранения таблиц;\n
			name – название таблицы;\n
			autocreation – указывает, нужно ли создавать таблицу при отсутствии таковой. 
		"""
		
		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__StorageDirectory = storage_path.rstrip("/\\")
		self.__Name = name
		self.__Path = f"{storage_path}/{name}/books"
		self.__Notes = dict()
		self.__Options = {
			"version": 1,
			"type": self.type,
			"recycle_id": False,
			"max_estimation": 10,
			"viewer": {
				"colorize": True
			},
			"metainfo_rules": {
				"author": None,
				"publisher": None
			}
		}
		self.__Eras = {
			0: "Pre–Star League",
			1: "Star League",
			2: "Succession Wars",
			3: "Clan Invasion",
			4: "Civil War",
			5: "Jihad",
			6: "Dark Age",
			7: "ilClan"
		}
		self.__TableCLI = BattleTech_Books_TableCLI(self)

		if os.path.exists(self.__Path):
			self.__Options = ReadJSON(f"{self.__Path}/manifest.json")
			if self.__Options["type"] != self.type: raise TypeError(f"Only \"{self.type}\" type tables supported.")
			self.__ReadNotes()

		elif autocreation:
			self.__Create()

		else: raise FileExistsError("manifest.json")

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		Status = ExecutionStatus(0)

		try:
			ID = self.__GetNewID(self.__Notes)
			WriteJSON(f"{self.__StorageDirectory}/{self.__Name}/{ID}.json", BattleTech_Books_Note.BASE_NOTE)
			self.__ReadNote(ID)
			Status["note_id"] = ID
			Status.message = f"Note #{ID} created."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		Status = ExecutionStatus(0)

		try:
			os.rename(f"{self.__Path}", f"{self.__Path}")
			self.__Name = name
			Status.message = "Table renamed."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def remove_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)
			del self.__Notes[note_id]
			os.remove(f"{self.__StorageDirectory}/{self.__Name}/{note_id}.json")
			Status.message = "Note removed."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def get_note(self, note_id: int) -> ExecutionStatus:
		"""
		Возвращает объектное представление записи.
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus(0)

		try:
			note_id = int(note_id)

			if note_id in self.__Notes.keys():
				Status.value = self.__Notes[note_id]

			else:
				Status = ExecutionError(-1, "note_not_found")

		except:
			Status = ExecutionError(-1, "unkonwn_error")

		return Status