from Source.Core.Base import Module, ModuleCLI, Note, NoteCLI
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.Engine.Bus import ExecutionError, ExecutionStatus
from dublib.Methods.Data import RemoveRecurringSubstrings
from dublib.CLI.TextStyler import Styles, TextStyler

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class BattleTech_Books_NoteCLI(NoteCLI):
	"""Обработчик взаимодействий с записью через CLI."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		Com = Command("altname", "Manage another names.")
		Com.add_argument(description = "Another name.", important = True)
		Com.add_flag("d", "Remove exists name.")
		CommandsList.append(Com)

		Com = Command("author", "[METAINFO] Set author.")
		Com.add_argument(description = "Author or authors list, splitted by \";\" character.", important = True)
		CommandsList.append(Com)

		Com = Command("collection", "Set collection status.")
		Com.add_argument(description = "Status: collected (c), ebook (e), whishlist (w), ordered (o).", important = True)
		CommandsList.append(Com)

		Com = Command("comment", "Set comment to note.")
		Com.add_argument(description = "Comment text or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("era", "Set era by timeline year.")
		ComPos = Com.create_position("ERA", "Index or timeline error.", important = True)
		ComPos.add_argument(ParametersTypes.All, "Era index.")
		ComPos.add_key("year", ParametersTypes.All, "Book timeline year.")
		CommandsList.append(Com)

		Com = Command("eras", "Show list of BattleTech eras.")
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

		Com = Command("pubdate", "[METAINFO] Set publication date.")
		Com.add_argument(description = "Publication date.", important = True)
		CommandsList.append(Com)

		Com = Command("publisher", "[METAINFO] Set publisher.")
		Com.add_argument(description = "Publisher.", important = True)
		CommandsList.append(Com)

		Com = Command("series", "[METAINFO] Set series.")
		Com.add_argument(description = "Series.", important = True)
		CommandsList.append(Com)

		Com = Command("status", "Set reading status.")
		Com.add_argument(description = "Status: announced (a), reading (r), completed (c), dropped (d), skipped (s).", important = True)
		CommandsList.append(Com)

		Com = Command("story", "Manage stories names.")
		Com.add_argument(description = "Story name.", important = True)
		Com.add_flag("del", "Remove exists story.")
		Com.add_key("localname", description = "Localized story name.")
		CommandsList.append(Com)

		Com = Command("type", "Set type of book.")
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

		elif parsed_command.name == "author":
			Value = parsed_command.arguments[0]

			if Value == "*":
				Status = self._Note.remove_metainfo("author")

			else:
				Value = RemoveRecurringSubstrings(Value, " ")
				Value = Value.replace("; ", ";").replace(" ;", ";")
				Status = self._Note.set_metainfo("author", Value)

		elif parsed_command.name == "collection":
			Status = self._Note.set_collection_status(parsed_command.arguments[0])

		elif parsed_command.name == "comment":
			Status = self._Note.set_comment(parsed_command.arguments[0])

		elif parsed_command.name == "era":
			if parsed_command.check_key("year"): Status = self._Note.set_era(parsed_command.get_key_value("year"), is_year = True)
			elif parsed_command.arguments[0] == "*": self._Note.remove_era()
			else: Status = self._Note.set_era(parsed_command.arguments[0])

		elif parsed_command.name == "eras":
			Eras = self._Table.eras

			for Era in Eras:
				EraIndex = Era["index"]
				Name = Era["name"]
				StartYear = Era["start_year"] if Era["start_year"] else "earlier"
				EndYear = Era["end_year"] if Era["end_year"] else "now"

				print(f"    {EraIndex}: {Name} [{StartYear} – {EndYear}]")

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

		elif parsed_command.name == "pubdate":
			Value = parsed_command.arguments[0]
			if Value == "*": Status = self._Note.remove_metainfo("publication_date")
			else: Status = self._Note.set_metainfo("publication_date", Value)

		elif parsed_command.name == "publisher":
			Value = parsed_command.arguments[0]
			if Value == "*": Status = self._Note.remove_metainfo("publisher")
			else: Status = self._Note.set_metainfo("publisher", Value)

		elif parsed_command.name == "series":
			Value = parsed_command.arguments[0]
			if Value == "*": Status = self._Note.remove_metainfo("series")
			else: Status = self._Note.set_metainfo("series", Value)

		elif parsed_command.name == "status":
			Status = self._Note.set_status(parsed_command.arguments[0])

		elif parsed_command.name == "story":
			if parsed_command.check_flag("d"): Status = self._Note.remove_story(parsed_command.arguments[0])
			else: Status = self._Note.add_story(parsed_command.arguments[0], parsed_command.get_key_value("localname"))

		elif parsed_command.name == "type":
			Status = self._Note.set_type(parsed_command.arguments[0])

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированные данные записи."""

		Status = ExecutionStatus(0)

		try:
			#---> Получение данных.
			#==========================================================================================#
			self._Note: "BattleTech_Books_Note"
			self._Table: "BattleTech_Books"
			UsedName = None
			Era = None
			AnotherNames = list()

			if self._Note.localized_name:
				UsedName = self._Note.localized_name
				AnotherNames.append(self._Note.name)

			else: UsedName = self._Note.name

			AnotherNames += self._Note.another_names

			#---> Вывод описания записи.
			#==========================================================================================#
			if UsedName: print(TextStyler(UsedName).decorate.bold, end = "")
			if self._Note.emoji_collection_status: print(" " + self._Note.emoji_collection_status, end = "")
			print(f" {self._Note.emoji_status}", end = "")
			print("")

			if self._Note.era != None:

				for CurrentEra in self._Table.eras:
					if CurrentEra["index"] == self._Note.era: Era = CurrentEra["name"]

			for AnotherName in AnotherNames: print(TextStyler(f"    {AnotherName}").decorate.bold)

			for StoryIndex in range(len(self._Note.stories.keys())):
				Index = StoryIndex + 1 
				Story =  list(self._Note.stories.keys())[StoryIndex]
				Localname =  list(self._Note.stories.values())[StoryIndex]
				if Localname: Localname = " / " + Localname
				print(TextStyler(f"    > {Index}. {Story}{Localname}").decorate.bold + " [story]")

			print(TextStyler("PROPERTIES:").decorate.bold)
			if self._Note.type: print("    ✒️  Type: " + self._Note.type.title())
			if Era: print(f"    🏺 Era: {Era}")
			if self._Note.estimation: print(f"    ⭐ Estimation: {self._Note.estimation}")
			if self._Note.bookmark: print(f"    🔖 Bookmark: {self._Note.bookmark} page")
			if self._Note.comment: print(f"    💭 Comment: {self._Note.comment}")
			if self._Note.link: print(f"    🔗 Link: {self._Note.link}")

			Attachments = self._Note.attachments

			if Attachments.count:
				print(TextStyler("ATTACHMENTS:").decorate.bold)
				for Slot in Attachments.slots: print(f"    {Slot}: " + TextStyler(Attachments.get_slot_filename(Slot)).decorate.italic)

			#---> Вывод классификаторов записи.
			#==========================================================================================#

			if self._Note.metainfo:
				print(TextStyler(f"METAINFO:").decorate.bold)
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					Data = MetaInfo[Key]
					if Key == "author": Data = Data.replace(";", ", ")
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: {Data}")

		except: Status = ERROR_UNKNOWN

		return Status

class BattleTech_Books_ModuleCLI(ModuleCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _BuildNoteRow(self, note: "BattleTech_Books_Note") -> dict[str, str]:
		"""
		Строит строку описания записи для таблицы и возвращает словарь в формате: название колонки – данные.
			note – обрабатываемая запись.
		"""

		Row = dict()

		Name = note.localized_name if note.localized_name else note.name
		Type = note.type or ""
		Era = TextStyler(note.era_name).decorate.italic if note.era_name else ""
		Publication = note.metainfo["publication_date"] if "publication_date" in note.metainfo and note.metainfo["publication_date"] else ""
		Series = TextStyler(note.metainfo["series"]).decorate.italic if "series" in note.metainfo else ""
		Estimation = ""

		if note.estimation:
			Estimation = "★ " * note.estimation
			if note.estimation in [5]: Estimation = TextStyler(Estimation, text_color = Styles.Colors.Green).text
			if note.estimation in [3, 4]: Estimation = TextStyler(Estimation, text_color = Styles.Colors.Yellow).text
			if note.estimation in [1, 2]: Estimation = TextStyler(Estimation, text_color = Styles.Colors.Red).text

		NoteStatus = note.status
		if not Name: Name = ""
		if not NoteStatus: NoteStatus = "–"
		Author = note.metainfo["author"] if "author" in note.metainfo.keys() else ""

		if ";" in Author:
			AuthorsCount = Author.count(";")
			Author = Author.split(";")[0] + " " + TextStyler(f"(and {AuthorsCount} other)").decorate.italic

		if NoteStatus == "announced": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Purple).text
		if NoteStatus == "planned": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Blue).text
		if NoteStatus == "reading": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Yellow).text
		if NoteStatus == "completed": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Green).text
		if NoteStatus == "dropped": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Red).text
		if NoteStatus == "skipped": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Cyan).text
		if note.emoji_collection_status: NoteStatus = note.emoji_collection_status + " " + NoteStatus
		else: NoteStatus = "   " + NoteStatus

		Row["ID"] = note.id
		Row["Status"] = NoteStatus
		Row["Name"] = note.localized_name if note.localized_name else note.name
		Row["Author"]= Author
		Row["Publication"] = Publication
		Row["Type"] = Type
		Row["Series"] = Series
		Row["Estimation"] = Estimation
		Row["Era"] = Era

		return Row

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

			for Era in Eras:
				EraIndex = Era["index"]
				Name = Era["name"]
				StartYear = Era["start_year"] if Era["start_year"] else "earlier"
				EndYear = Era["end_year"] if Era["end_year"] else "now"
				print(TextStyler(str(EraIndex).ljust(8)).decorate.bold, end = "")
				print(f": {Name} [{StartYear} – {EndYear}]")

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
		"stories": {},
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
	def era(self) -> float | int | None:
		"""Индекс эры."""

		return self._Data["era"]
	
	@property
	def era_name(self) -> str | None:
		"""Название эры."""

		Name = None
		
		for Era in self._Table.eras:

			if self.era == Era["index"]:
				Name = Era["name"]
				break

		return Name

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
	def status(self) -> str | None:
		"""Статус просмотра."""

		return self._Data["status"]
	
	@property
	def stories(self) -> dict[str, str]:
		"""Словарь историй и их локализованных названий."""

		if "stories" not in self._Data.keys(): self._Data["stories"] = dict()

		return self._Data["stories"]
	
	@property
	def type(self) -> str | None:
		"""Тип книги."""

		return self._Data["type"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def searchable(self) -> list[str]:
		"""Список строк, которые представляют контент для поисковых запросов."""

		Strings = super().searchable
		Stories = list(self.stories.keys()) + list(self.stories.values())
		if Stories: Strings += Stories 

		return Strings

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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
	
	def add_story(self, name: str, localname: str | None = None) -> ExecutionStatus:
		"""
		Добавляет историю.
			name – название истории;\n
			localname – локализованное название истории.
		"""

		Status = ExecutionStatus(0)

		try:
			if "stories" not in self._Data.keys(): self._Data["stories"] = list()

			if name not in self._Data["stories"]:
				self._Data["stories"][name] = localname
				self.save()
				Status.message = "Story added."

			else: Status.message = "Stroty already exists."

		except: Status = ERROR_UNKNOWN

		return Status

	def remove_era(self) -> ExecutionStatus:
		"""Удаляет эру."""

		Status = ExecutionStatus(0)

		self._Data["era"] = None
		self.save()
		Status.message = "Era removed."
		
		return Status

	def remove_story(self, name: str) -> ExecutionStatus:
		"""
		Удаляет историю.
			name – название истории.
		"""

		Status = ExecutionStatus(0)

		try:
			del self._Data["stories"][name]
			self.save()
			Status.message = "Story removed."

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

	def set_era(self, era: float | int | str, is_year: bool = False) -> ExecutionStatus:
		"""
		Задаёт эру.
			era – индекс эры или год событий;\n
			is_year – указывает, является ли идентификатор эры годом событий.
		"""

		Status = ExecutionStatus(0)

		try:
			if is_year: 
				Year = int(era)

				for Era in self._Table.eras:
					if not Era["start_year"]: Era["start_year"] = 0
					if not Era["end_year"]: Era["end_year"] = 9999
					if Era["index"] >= 0 and Year > Era["start_year"] and Year < Era["end_year"]: self._Data["era"] = Era["index"]
					self.save()
					Status.message = "Era updated."

			else:
				if type(era) == str:
					if "." in era: era = float(era)
					else: era = int(era)

				if era in self._Table.eras_indexes:
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
			"publication_date": None,
			"publisher": None,
			"series": None
		},
		"viewer": {
			"autoclear": False,
			"columns": {
				"ID": True,
				"Status": True,
				"Name": True,
				"Author": True,
				"Publication": True,
				"Type": True,
				"Series": True,
				"Era": True,
				"Estimation": True
			}
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
	
	@property
	def eras_indexes(self) -> list[int, float]:
		"""Индексы эпох BattleTech."""

		return self._Table.eras_indexes
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Books_Note
		self._CLI = BattleTech_Books_ModuleCLI