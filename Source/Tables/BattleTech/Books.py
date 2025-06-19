from Source.Core.Base import Module, ModuleCLI, Note, NoteCLI
from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
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
		Com.base.add_argument(description = "Another name.", important = True)
		Com.base.add_flag("d", "Remove exists name.")
		CommandsList.append(Com)

		Com = Command("author", "Set author.", category = "Metainfo")
		Com.base.add_argument(description = "Author or authors list, splitted by \";\" character.", important = True)
		CommandsList.append(Com)

		Com = Command("collection", "Set collection status.")
		Com.base.add_argument(description = "Status: collected (c), ebook (e), whishlist (w), ordered (o).", important = True)
		CommandsList.append(Com)

		Com = Command("comment", "Set comment to note.")
		Com.base.add_argument(description = "Comment text or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("era", "Set era by timeline year.")
		ComPos = Com.create_position("ERA", "Index or timeline error.", important = True)
		ComPos.add_argument(ParametersTypes.All, "Era index.")
		ComPos.add_key("year", ParametersTypes.All, "Book timeline year.")
		CommandsList.append(Com)

		Com = Command("eras", "Show list of BattleTech eras.")
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		Com.base.add_argument(ParametersTypes.Number, description = "Estimation.", important = True)
		CommandsList.append(Com)

		Com = Command("link", "Attach link to note.")
		Com.base.add_argument(description = "URL or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("localname", "Set localized name.")
		Com.base.add_argument(description = "Localized name.", important = True)
		CommandsList.append(Com)

		Com = Command("pubdate", "Set publication date.", category = "Metainfo")
		Com.base.add_argument(description = "Publication date.", important = True)
		CommandsList.append(Com)

		Com = Command("publisher", "Set publisher.", category = "Metainfo")
		Com.base.add_argument(description = "Publisher.", important = True)
		CommandsList.append(Com)

		Com = Command("series", "Set series.", category = "Metainfo")
		Com.base.add_argument(description = "Series.", important = True)
		CommandsList.append(Com)

		Com = Command("status", "Set reading status.")
		Com.base.add_argument(description = "Status: announced (a), reading (r), completed (c), dropped (d), skipped (s).", important = True)
		CommandsList.append(Com)

		Com = Command("type", "Set type of book.")
		Com.base.add_argument(description = "Type of book: novel, story.", important = True)
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

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
			elif parsed_command.arguments[0] == "*": Status = self._Note.remove_era()
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

		elif parsed_command.name == "type":
			Status = self._Note.set_type(parsed_command.arguments[0])

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированные данные записи."""

		Status = ExecutionStatus()

		try:
			#---> Получение данных.
			#==========================================================================================#
			self._Note: BattleTech_Books_Note
			self._Table: BattleTech_Books
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

			for AnotherName in AnotherNames: print(f"    {AnotherName}")

			#---> Вывод историй.
			#==========================================================================================#
			Stories = self._Note.stories
			if Stories: print(TextStyler("STORIES:").decorate.bold)

			for Story in Stories:
				Localname = Story.localized_name
				if Localname: Localname = " / " + Localname
				print(f"    > {Story.id}. {Story.name}{Localname} {Story.emoji_status}")

			print(TextStyler("PROPERTIES:").decorate.bold)
			if self._Note.type: print("    ✒️  Type: " + self._Note.type.title())
			if Era: print(f"    🏺 Era: {Era}")
			if self._Note.estimation: print(f"    ⭐ Estimation: {self._Note.estimation}")
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
					Data: str = MetaInfo[Key]
					if Key == "author": Data = Data.replace(";", ", ")
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: {Data}")

		except: Status.push_error(Errors.UNKNOWN)

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

		if NoteStatus == "announced": NoteStatus = TextStyler(NoteStatus, text_color = Styles.Colors.Magenta).text
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

		Com = Command("statistics", "Show statistics of BattleTech books.")
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name == "eras":
			Eras = self._Module.eras

			for Era in Eras:
				EraIndex = Era["index"]
				Name = Era["name"]
				StartYear = Era["start_year"] if Era["start_year"] else "earlier"
				EndYear = Era["end_year"] if Era["end_year"] else "now"
				print(TextStyler(str(EraIndex).ljust(8)).decorate.bold, end = "")
				print(f": {Name} [{StartYear} – {EndYear}]")

		elif parsed_command.name == "statistics":
			Notes: list[BattleTech_Books_Note] = self._Module.notes
			Total = len(Notes)
			Novels = 0
			Stories = 0
			Compilations = 0
			Undefined = 0

			Completed = 0

			CollectedBooks = 0
			CollectedEbooks = 0

			for CurrentNote in Notes:
				if CurrentNote.type == "novel": Novels += 1
				elif CurrentNote.type == "story": Stories += 1
				elif CurrentNote.type == "compilation": Compilations += 1
				else: Undefined += 1

				if CurrentNote.status == "completed": Completed += 1

				if CurrentNote.collection_status == "ebook": CollectedEbooks += 1
				elif CurrentNote.collection_status == "collected": CollectedBooks += 1

			if Undefined: Undefined = f", {Undefined} undefined"
			else: Undefined = ""
			print(TextStyler("Total books:").decorate.bold, end = "")
			print(f" {Total} ({Novels} novels, {Stories} stories, {Compilations} compilations){Undefined}")

			CompletedPercentage = round(Completed / Total * 100, 2)
			print(TextStyler("Fully readed:").decorate.bold, end = "")
			print(f" {Completed} books ({CompletedPercentage}%)")

			CollectedTotal = CollectedBooks + CollectedEbooks
			CollectedPercentage = round(CollectedTotal / Total * 100, 2)
			print(TextStyler("Collected:").decorate.bold, end = "")
			print(f" {CollectedBooks} books, {CollectedEbooks} ebooks ({CollectedPercentage}%)")

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
	def stories(self) -> tuple["BattleTech_Books_Note"]:
		"""Записи, являющиеся историями, входящими в книгу."""

		return self._Table.binder.local.get_binded_notes(self._ID)
	
	@property
	def type(self) -> str | None:
		"""Тип книги."""

		return self._Data["type"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = BattleTech_Books_NoteCLI

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def attach(self, path: str, slot: str | None = None, force: bool = False) -> ExecutionStatus:
		"""
		Прикрепляет файл к записи.
			path – путь к файлу;\n
			slot – именной слот для файла;\n
			force – включает режим перезаписи.
		"""

		Status = super().attach(path, slot, force)
		if not Status.has_errors and slot == "ebook" and not self.collection_status: Status.merge(self.set_collection_status("e"))

		return Status

	def add_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Добавляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus()

		try:

			if another_name not in self._Data["another_names"]:
				self._Data["another_names"].append(another_name)
				self.save()
				Status.push_message("Another name added.")

			else: Status.push_message("Another name already exists.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_another_name(self, another_name: str) -> ExecutionStatus:
		"""
		Удаляет альтернативное название.
			another_name – альтернативное название.
		"""

		Status = ExecutionStatus()

		try:
			if another_name in self._Data["another_names"]:
				self._Data["another_names"].remove(another_name)
				self.save()
				Status.push_message("Another name removed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_era(self) -> ExecutionStatus:
		"""Удаляет эру."""

		Status = ExecutionStatus()

		if self._Data["era"]:
			self._Data["era"] = None
			self.save()
			Status.push_message("Era removed.")
		
		return Status

	def estimate(self, estimation: int) -> ExecutionStatus:
		"""
		Выставляет оценку.
			estimation – оценка.
		"""

		Status = ExecutionStatus()

		try:

			if estimation <= 5 and estimation > 0:
				self._Data["estimation"] = estimation
				self.save()
				Status.push_message("Estimation updated.")

			else: Status.push_error("Incorrect estimation value. From 1 to 5 expected.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_comment(self, comment: str) -> ExecutionStatus:
		"""
		Задаёт комментарий.
			comment – комментарий.
		"""

		Status = ExecutionStatus()

		try:
			if comment == "*":
				comment = None
				Status.push_message("Comment removed.")

			else: 
				Status.push_message("Comment updated.")

			self._Data["comment"] = comment
			self.save()

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_era(self, era: float | int | str, is_year: bool = False) -> ExecutionStatus:
		"""
		Задаёт эру.
			era – индекс эры или год событий;\n
			is_year – указывает, является ли идентификатор эры годом событий.
		"""

		Status = ExecutionStatus()

		try:

			if is_year: 
				Year = int(era)
				self._Table: BattleTech_Books

				for Era in self._Table.eras:
					if not Era["start_year"]: Era["start_year"] = 0
					if not Era["end_year"]: Era["end_year"] = 9999

					if Era["index"] >= 0 and Year >= Era["start_year"] and Year <= Era["end_year"]:
						self._Data["era"] = Era["index"]
						self.save()
						Status.push_message("Era updated.")
						break

			else:
				if type(era) == str:
					if "." in era: era = float(era)
					else: era = int(era)

				if era in self._Table.eras_indexes:
					self._Data["era"] = era
					self.save()
					Status.push_message("Era updated.")

				else: Status.push_error("Incorrect era.")

		except:	Status.push_error(Errors.UNKNOWN)

		return Status

	def set_link(self, link: str) -> ExecutionStatus:
		"""
		Задаёт ссылку.
			link – ссылка.
		"""

		Status = ExecutionStatus()

		try:
			if link == "*":
				link = None
				Status.push_message("Link removed.")

			else:
				Status.push_message("Link updated.")

			self._Data["link"] = link
			self.save()

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_localized_name(self, localized_name: str) -> ExecutionStatus:
		"""
		Задаёт локализованное название записи.
			name – локализованное названиие.
		"""

		Status = ExecutionStatus()

		try:

			if localized_name == "*":
				localized_name = None
				Status.push_message("Localized name removed.")

			else:
				Status.push_message("Localized name updated.")

			self._Data["localized_name"] = localized_name
			self.save()

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_collection_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус коллекционирования.
			status – статус.
		"""

		Status = ExecutionStatus()
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
			if status: Status.push_message("Collection status updated.")
			else: Status.push_message("Collection status removed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус прочтения.
			status – статус.
		"""

		Status = ExecutionStatus()
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
			if status: Status.push_message("Status updated.")
			else: Status.push_message("Status removed.")
			

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_type(self, type: str) -> ExecutionStatus:
		"""
		Задаёт тип книги.
			type – имп.
		"""

		Status = ExecutionStatus()
		AllowedTypes = ("novel", "story", "compilation")

		try:
			if type.lower() not in AllowedTypes:
				Status.push_error("Type isn't allowed. Use novel, story or compilation.")
				return Status
			
			if type == "*":
				type = None
				Status.push_message("Type removed.")

			else:
				Status.push_message("Type updated.")

			self._Data["type"] = type
			self.save()

		except: Status.push_error(Errors.UNKNOWN)

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
			"recycle_id": True,
			"attachments": True
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
		}
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

		self._Table: BattleTech_Books
		self._Note = BattleTech_Books_Note
		self._CLI = BattleTech_Books_ModuleCLI