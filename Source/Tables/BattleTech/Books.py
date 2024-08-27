from Source.Core.Base import Module, ModuleCLI, Note, NoteCLI
from Source.CLI.Templates import Columns
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.StyledPrinter import Styles, StyledPrinter, TextStyler
from dublib.Engine.Bus import ExecutionError, ExecutionStatus

#==========================================================================================#
# >>>>> ОБРАБОТЧИКИ ВЗАИМОДЕЙСТВИЙ С ТАБЛИЦЕЙ <<<<< #
#==========================================================================================#

class BattleTech_Books_NoteCLI(NoteCLI):
	"""Обработчик взаимодействий с записью через CLI."""

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		Com = Command("comment", "Set comment to note.")
		Com.add_argument(description = "Comment text or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("era", "Set era.")
		Com.add_argument(description = "Era ID or name.", important = True)
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

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "comment":
			Status = self._Note.set_comment(parsed_command.arguments[0])

		if parsed_command.name == "era":
			Status = self._Note.set_era(parsed_command.arguments[0])

		if parsed_command.name == "estimate":
			Status = self._Note.estimate(parsed_command.arguments[0])

		if parsed_command.name == "link":
			Status = self._Note.set_link(parsed_command.arguments[0])

		if parsed_command.name == "mark":
			Status = self._Note.set_bookmark(parsed_command.arguments[0])

		if parsed_command.name == "meta":
			Status = ExecutionStatus(0)
			
			if "set" in parsed_command.flags:
				Status = self._Note.set_metainfo(parsed_command.arguments[0],  parsed_command.arguments[1])

			if parsed_command.check_flag("unset"):
				Status = self._Note.delete_metainfo(parsed_command.arguments[0])

		if parsed_command.name == "set":

			if "altname" in parsed_command.keys.keys():
				Status = self._Note.add_another_name(parsed_command.keys["altname"])

			if parsed_command.check_key("era"):
				Status = self._Note.add_era(parsed_command.get_key_value("era"))

			if "localname" in parsed_command.keys.keys():
				Status = self._Note.rename(parsed_command.keys["localname"], localized = True)

			if "name" in parsed_command.keys.keys():
				Status = self._Note.rename(parsed_command.keys["name"])

			if "status" in parsed_command.keys.keys():
				Status = self._Note.set_status(parsed_command.keys["status"])

		if parsed_command.name == "unset":

			if parsed_command.check_key("altname"):
				Status = self._Note.delete_another_name(parsed_command.get_key_value("altname"))

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированные данные записи."""

		Status = ExecutionStatus(0)

		try:
			#---> Получение данных.
			#==========================================================================================#
			UsedName = None
			AnotherNames = list()

			if self._Note.localized_name:
				UsedName = self._Note.localized_name
				AnotherNames.append(self._Note.name)

			else:
				UsedName = self._Note.name

			AnotherNames += self._Note.another_names

			#---> Вывод описания записи.
			#==========================================================================================#
			if UsedName: StyledPrinter(UsedName, decorations = [Styles.Decorations.Bold], end = False)
			print(f" {self._Note.emoji_status}")
			if self._Note.era: print(f"⏳ " + self._Table.eras[self._Note.era])
			if self._Note.estimation: print(f"⭐ {self._Note.estimation} / {self._Table.max_estimation}")
			if self._Note.bookmark: print(f"🔖 {self._Note.bookmark} page")
			if self._Note.comment: print(f"💭 {self._Note.comment}")
			if self._Note.link: print(f"🔗 {self._Note.link}")
			if AnotherNames: StyledPrinter(f"ANOTHER NAMES: ", decorations = [Styles.Decorations.Bold])
			for AnotherName in AnotherNames: StyledPrinter(f"    {AnotherName}", decorations = [Styles.Decorations.Italic])

			#---> Вывод классификаторов записи.
			#==========================================================================================#

			if self._Note.metainfo:
				StyledPrinter(f"METAINFO:", decorations = [Styles.Decorations.Bold])
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		except: Status = ERROR_UNKNOWN

		return Status

class BattleTech_Books_ModuleCLI(ModuleCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		Com = Command("eras", "Show list of BattleTech eras.")
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "eras":
			Eras = self._Module.eras
			for EraID in Eras.keys(): print(f"    {EraID}: {Eras[EraID]}")

		return Status

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _List(self, parsed_command: ParsedCommandData, search: str | None = None) -> ExecutionStatus:
			"""
			Выводит список записей.
				parsed_command – описательная структура команды;\n
				search – поисковый запрос.
			"""

			Status = ExecutionStatus(0)

			try:
				Notes = list()
				Content = {
					"ID": [],
					"Status": [],
					"Name": [],
					"Author": [],
					"Estimation": []
				}
				SortBy = parsed_command.keys["sort"].title() if "sort" in parsed_command.keys.keys() else "ID"
				if SortBy == "Id": SortBy = SortBy.upper()

				if SortBy not in Content.keys():
					Status = ExecutionError(-1, "no_column_to_sort")
					return Status
				
				Reverse = parsed_command.check_flag("r")
				
				if self._Module.notes:
					Notes = self._Module.notes

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
						NoteStatus = Note.status
						if NoteStatus == "announced": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Purple)
						if NoteStatus == "collected": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Blue)
						if NoteStatus == "web": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Blue)
						if NoteStatus == "ordered": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.White)
						if NoteStatus == "wishlist": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.White)
						if NoteStatus == "reading": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Yellow)
						if NoteStatus == "completed": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Green)
						if NoteStatus == "dropped": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Red)
						if NoteStatus == "skipped": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Cyan)
						Content["ID"].append(Note.id)
						Content["Status"].append(NoteStatus if NoteStatus else "–")
						Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")
						Content["Author"].append(Author)
						Content["Estimation"].append(Note.estimation if Note.estimation else "")

					if len(Notes): Columns(Content, sort_by = SortBy, reverse = Reverse)
					else: Status.message = "Notes not found."

				else:
					Status.message = "Table is empty."

			except: Status = ERROR_UNKNOWN

			return Status
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class BattleTech_Books_Note(Note):
	"""Запись о прочтении книги по вселенной BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"localized_name": None,
		"another_names": [],
		"era": None,
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

		return self._Data["another_names"]

	@property
	def bookmark(self) -> int | None:
		"""Закладка."""

		return self._Data["bookmark"]

	@property
	def comment(self) -> str | None:
		"""Комментарий."""

		return self._Data["comment"]

	@property
	def era(self) -> list[int]:
		"""Список ID эпох BattleTech."""

		return self._Data["era"]

	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		Statuses = {
			"announced": "ℹ️",
			"reading": "📖",
			"completed": "✅",
			"dropped": "⛔",
			"collected": "📦",
			"web": "🌍",
			"wishlist": "🎁",
			"ordered": "🚚",
			"skipped": "🚫",
			None: ""
		}

		return Statuses[self._Data["status"]]

	@property
	def estimation(self) -> int | None:
		"""Оценка."""

		return self._Data["estimation"]

	@property
	def link(self) -> str | None:
		"""Ссылка."""

		return self._Data["link"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Data["localized_name"]
	
	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self._Data["metainfo"]
	
	@property
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self._Data["status"]

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = BattleTech_Books_NoteCLI

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

	def remove_another_name(self, another_name: int | str) -> ExecutionStatus:
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

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus(0)

		try:

			if estimation <= self._Module.manifest["max_estimation"]:
				self.__Data["estimation"] = estimation
				self.save()
				Status.message = "Estimation updated."

			else: Status = ExecutionError(1, "max_estimation_exceeded")

		except: Status = ERROR_UNKNOWN

		return Status

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

	def set_era(self, era: str) -> ExecutionStatus:
		"""
		Задаёт эру.
			era – ID или название эры.
		"""

		Status = ExecutionStatus(0)

		try:
			era = str(era)

			if era.isdigit():
				era = int(era)

				if era in self._Module.eras.keys():
					self.__Data["era"] = era
					self.save()
					Status.message = "Era updated."

				else: Status = ExecutionError(-2, "incorrect_era")

			elif era in self._Module.eras.values:
				self.__Data["era"] = list(self._Module.eras.values).index(era)
				self.save()
				Status.message = "Era updated."

			else: Status = ExecutionError(-2, "incorrect_era")

		except:	Status = ERROR_UNKNOWN

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
			"n": "web",
			"w": "wishlist",
			"o": "ordered",
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

class BattleTech_Books(Module):
	"""Таблица прочтения книг по вселенной BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "battletech:books"
	MANIFEST: dict = {
		"object": "module",
		"type": TYPE,
		"common": {
			"recycle_id": True
		},
		"metainfo_rules": {
			"author": None,
			"publisher": None,
			"series": None
		},
		"viewer": {
			"colorize": True
		},
		"custom": {
			"max_estimation": 10
		}
	}

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#
	
	@property
	def eras(self) -> dict:
		"""Эпохи BattleTech."""

		return self._Table.eras

	@property
	def max_estimation(self) -> int:
		"""Максимальная допустимая оценка."""

		return self._Manifest.custom["max_estimation"]
	
	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Books_Note
		self._CLI = BattleTech_Books_ModuleCLI