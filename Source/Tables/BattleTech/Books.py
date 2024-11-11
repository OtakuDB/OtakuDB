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

		Com = Command("altname", "Manage another names.")
		Com.add_argument(description = "Another name.", important = True)
		Com.add_flag("d", "Remove exists name.")
		CommandsList.append(Com)

		Com = Command("collection", "Set collection status.")
		Com.add_argument(description = "Status: collected (c), ebook (e), whishlist (w), ordered (o).", important = True)
		CommandsList.append(Com)

		Com = Command("comment", "Set comment to note.")
		Com.add_argument(description = "Comment text or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("era", "[METAINFO] Set era.")
		Com.add_argument(description = "Era ID or name.", important = True)
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		Com.add_argument(ParametersTypes.Number, description = "Estimation.", important = True)
		CommandsList.append(Com)

		Com = Command("link", "Attach link to note.")
		Com.add_argument(description = "URL or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("localname", "Set localized name.")
		Com.add_argument(description = "Localized name.", important = True)
		CommandsList.append(Com)

		Com = Command("mark", "Set bookmark.")
		Com.add_argument(ParametersTypes.Number, description = "Page number or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.")
		Com.add_argument(description = "Field name.", important = True)
		Com.add_argument(description = "Field value.")
		ComPos = Com.create_position("OPERATION", "Type of operation with metainfo.", important = True)
		ComPos.add_flag("set", description = "Create new or update exists field.")
		ComPos.add_flag("del", description = "Remove field.")
		CommandsList.append(Com)

		Com = Command("status", "Set reading status.")
		Com.add_argument(description = "Status: announced (a), reading (r), completed (c), dropped (d), skipped (s).", important = True)
		CommandsList.append(Com)

		Com = Command("type", "[METAINFO] Set type of book.")
		Com.add_argument(description = "Type of book: novel, story.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus(0)

		if parsed_command.name == "altname":
			if parsed_command.check_flag("d"): Status = self._Note.remove_another_name(parsed_command.arguments[0])
			else: Status = self._Note.add_another_name(parsed_command.arguments[0])

		elif parsed_command.name == "collection":
			Status = self._Note.set_collection_status(parsed_command.arguments[0])

		elif parsed_command.name == "comment":
			Status = self._Note.set_comment(parsed_command.arguments[0])

		elif parsed_command.name == "era":
			Status = self._Note.set_era(parsed_command.arguments[0])

		elif parsed_command.name == "estimate":
			Status = self._Note.estimate(parsed_command.arguments[0])

		elif parsed_command.name == "link":
			Status = self._Note.set_link(parsed_command.arguments[0])

		elif parsed_command.name == "localname":
			Status = self._Note.set_localized_name(parsed_command.arguments[0])

		elif parsed_command.name == "mark":
			Status = self._Note.set_bookmark(parsed_command.arguments[0])

		elif parsed_command.name == "meta":
			Status = ExecutionStatus(0)
			
			if parsed_command.check_flag("set"):
				Status = self._Note.set_metainfo(parsed_command.arguments[0],  parsed_command.arguments[1])

			if parsed_command.check_flag("del"):
				Status = self._Note.remove_metainfo(parsed_command.arguments[0])

		elif parsed_command.name == "status":
			Status = self._Note.set_status(parsed_command.arguments[0])

		elif parsed_command.name == "type":
			Status = self._Note.set_type(parsed_command.arguments[0])

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
			if self._Note.emoji_collection_status: print(" " + self._Note.emoji_collection_status, end = "")
			print(f" {self._Note.emoji_status}", end = "")
			print("")
			for AnotherName in AnotherNames: StyledPrinter(f"    {AnotherName}", decorations = [Styles.Decorations.Italic])
			StyledPrinter("PROPERTIES:", decorations = [Styles.Decorations.Bold])
			if self._Note.type: print("    ✒️  Type: " + self._Note.type.title())
			if self._Note.era: print("    🏺 Era: " + self._Table.eras[self._Note.era]["name"])
			if self._Note.estimation: print(f"    ⭐ Estimation:{self._Note.estimation}")
			if self._Note.bookmark: print(f"    🔖 Bookmark: {self._Note.bookmark} page")
			if self._Note.comment: print(f"    💭 Comment: {self._Note.comment}")
			if self._Note.link: print(f"    🔗 Link: {self._Note.link}")

			Attachments = self._Note.attachments

			if Attachments:
				StyledPrinter("ATTACHMENTS:", decorations = [Styles.Decorations.Bold])
				for Slot in Attachments.slots: print(f"    {Slot}: " + TextStyler(Attachments.get_slot_filename(Slot), decorations = [Styles.Decorations.Italic]))

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

			for EraID in range(len(Eras)):
				Name = Eras[EraID]["name"]
				StartYear = Eras[EraID]["start_year"] if Eras[EraID]["start_year"] else "earlier"
				EndYear = Eras[EraID]["end_year"] if Eras[EraID]["end_year"] else "now"

				print(f"    {EraID}: {Name} [{StartYear} – {EndYear}]")

		return Status

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
					"Type": [],
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
						Type = Note.type or ""
						Estimation = ""

						if Note.estimation:
							Estimation = "★ " * Note.estimation
							if Note.estimation in [5]: Estimation = TextStyler(Estimation, text_color = Styles.Colors.Green)
							if Note.estimation in [3, 4]: Estimation = TextStyler(Estimation, text_color = Styles.Colors.Yellow)
							if Note.estimation in [1, 2]: Estimation = TextStyler(Estimation, text_color = Styles.Colors.Red)

						NoteStatus = Note.status
						if not Name: Name = ""
						if not NoteStatus: NoteStatus = "–"
						Author = Note.metainfo["author"] if "author" in Note.metainfo.keys() else ""
						if NoteStatus == "announced": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Purple)
						if NoteStatus == "planned": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Blue)
						if NoteStatus == "reading": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Yellow)
						if NoteStatus == "completed": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Green)
						if NoteStatus == "dropped": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Red)
						if NoteStatus == "skipped": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Cyan)
						if Note.emoji_collection_status: NoteStatus = Note.emoji_collection_status + " " + NoteStatus
						else: NoteStatus = "   " + NoteStatus
						Content["ID"].append(Note.id)
						Content["Status"].append(NoteStatus)
						Content["Name"].append(Name if len(Name) < 60 else Name[:60] + "…")
						Content["Author"].append(Author)
						Content["Type"].append(Type)
						Content["Estimation"].append(Estimation)

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
		"type": "novel",
		"era": None,
		"estimation": None,
		"comment": None,
		"link": None,
		"bookmark": None,
		"status": None,
		"collection_status": None,
		"metainfo": {},
		"attachments": {
			"slots": {
				"ebook": None
			}
		}
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
	def collection_status(self) -> str | None:
		"""Статус коллекционирования."""

		return self._Data["collection_status"]

	@property
	def comment(self) -> str | None:
		"""Комментарий."""

		return self._Data["comment"]

	@property
	def era(self) -> list[int]:
		"""Эра."""

		return self._Data["era"]

	@property
	def emoji_collection_status(self) -> str:
		"""Статус коллекционирования в видзе эмодзи."""

		Statuses = {
			"collected": "📦",
			"ebook": "🌍",
			"wishlist": "🎁",
			"ordered": "🚚",
			None: ""
		}

		return Statuses[self._Data["collection_status"]]

	@property
	def emoji_status(self) -> str:
		"""Статус просмотра в видзе эмодзи."""

		Statuses = {
			"announced": "ℹ️",
			"reading": "📖",
			"completed": "✅",
			"dropped": "⛔",
			"skipped": "🚫",
			"planned": "📋",
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
	
	@property
	def type(self) -> str | None:
		"""Тип книги."""

		return self._Data["type"]

	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = BattleTech_Books_NoteCLI

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< # Natural Selection
	#==========================================================================================#

	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus(0)

		try:

			if another_name not in self._Data["another_names"]:
				self._Data["another_names"].append(another_name)
				self.save()
				Status.message = "Another name added."

			else: Status.message = "Another name already exists."

		except: Status = ERROR_UNKNOWN

		return Status

	def remove_another_name(self, another_name: int | str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название или его индекс.
		"""

		Status = ExecutionStatus(0)

		try:

			if another_name.isdigit() and another_name not in self._Data["another_names"]:
				self._Data["another_names"].pop(int(another_name))

			else:
				self._Data["another_names"].remove(another_name)

			self.save()
			Status.message = "Another name removed."

		except IndexError:
			Status = ExecutionError(1, "incorrect_another_name_index")

		except: Status = ERROR_UNKNOWN

		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus(0)

		try:

			if estimation <= 5:
				self._Data["estimation"] = estimation
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
			self._Data["bookmark"] = bookmark
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
			self._Data["comment"] = comment
			self.save()
			Status.message = "Comment updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_era(self, era: int, is_year: bool = False) -> ExecutionStatus:
		"""
		Задаёт эру.
			era – ID эры или год событий;\n
			is_year – указывает, является ли идентификатор эры годом событий.
		"""

		Status = ExecutionStatus(0)

		try:
			era = int(era)

			if era in range(len(self._Table.eras)):
				self._Data["era"] = era
				self.save()
				Status.message = "Era updated."

			else: Status = ExecutionError(-1, "incorrect_era")

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
			self._Data["link"] = link
			self.save()
			Status.message = "Link updated."

		except:
			Status = ERROR_UNKNOWN

		return Status

	def set_localized_name(self, localized_name: str) -> ExecutionStatus:
		"""
		Задаёт локализованное название записи.
			name – локализованное названиие.
		"""

		Status = ExecutionStatus(0)

		try:

			if localized_name == "*":
				localized_name = None
				Status.message = "Localized name removed."

			else:
				Status.message = "Localized name updated."

			self._Data["localized_name"] = localized_name
			self.save()

		except: Status = ERROR_UNKNOWN

		return Status

	def set_collection_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус коллекционирования.
			status – статус.
		"""

		Status = ExecutionStatus(0)
		Statuses = {
			"c": "collected",
			"e": "ebook",
			"w": "whishlist",
			"o": "ordered",
			"*": None
		}

		try:
			if status in Statuses.keys(): status = Statuses[status]
			self._Data["collection_status"] = status
			self.save()
			Status.message = "Collection status updated."

		except: Status = ERROR_UNKNOWN

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус прочтения.
			status – статус.
		"""

		Status = ExecutionStatus(0)
		Statuses = {
			"a": "announced",
			"r": "reading",
			"c": "completed",
			"d": "dropped",
			"s": "skipped",
			"p": "planned",
			"*": None
		}

		try:
			if status in Statuses.keys(): status = Statuses[status]
			self._Data["status"] = status
			self.save()
			Status.message = "Status updated."

		except: Status = ERROR_UNKNOWN

		return Status

	def set_type(self, type: str) -> ExecutionStatus:
		"""
		Задаёт тип книги.
			type – имп.
		"""

		Status = ExecutionStatus(0)

		try:
			if type == "*": type = None
			self._Data["type"] = type
			self.save()
			Status.message = "Type updated."

		except: Status = ERROR_UNKNOWN

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
			"series": None,
			"type": ["fanfiction", "novel", "story"]
		},
		"viewer": {
			"colorize": True
		},
		"custom": {}
	}

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#
	
	@property
	def eras(self) -> list[dict]:
		"""Эпохи BattleTech."""

		return self._Table.eras
	
	#==========================================================================================#
	# >>>>> ПЕРЕГРУЖАЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Books_Note
		self._CLI = BattleTech_Books_ModuleCLI