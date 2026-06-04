from ..Structs import CollectionStatuses, Statuses, Types

from Source.Interfaces.CLI.Base import BaseTableCLI, BaseNoteCLI
from Source.Interfaces.CLI.Functions import Unstar

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler
from dublib.CLI.Templates.Bus import PrintError, PrintWarning
from dublib.Methods.Data import ToIterable

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..table import Table
	from ..note import Note

class TableCLI(BaseTableCLI):
	"""Интерпретатор CLI таблицы."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _statistics(self):
		"""Выводит статистику чтения произведений."""

		Notes: "tuple[Note]" = self._Table.notes
		Total = len(Notes)
		Novels = 0
		Stories = 0
		Compilations = 0
		Undefined = 0

		Completed = 0

		CollectedBooks = 0
		CollectedEbooks = 0

		for CurrentNote in Notes:
			if CurrentNote.type == Types.Novel: Novels += 1
			elif CurrentNote.type == Types.Story: Stories += 1
			elif CurrentNote.type == Types.Compilation: Compilations += 1
			else: Undefined += 1

			if CurrentNote.status == Statuses.Completed: Completed += 1

			if CurrentNote.collection_status == CollectionStatuses.Ebook: CollectedEbooks += 1
			elif CurrentNote.collection_status == CollectionStatuses.Collected: CollectedBooks += 1

		if Undefined: Undefined = f", {Undefined} undefined"
		else: Undefined = ""
		print(FastStyler("Total books:").decorate.bold, end = "")
		print(f" {Total} ({Novels} novels, {Stories} stories, {Compilations} compilations){Undefined}")

		CompletedPercentage = round(Completed / Total * 100, 2)
		print(FastStyler("Fully readed:").decorate.bold, end = "")
		print(f" {Completed} books ({CompletedPercentage}%)")

		CollectedTotal = CollectedBooks + CollectedEbooks
		CollectedPercentage = round(CollectedTotal / Total * 100, 2)
		print(FastStyler("Collected:").decorate.bold, end = "")
		print(f" {CollectedBooks} books, {CollectedEbooks} ebooks ({CollectedPercentage}%)")

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteCustomCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает кастомную команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "statistics": self._statistics()

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("statistics", "Show statistics of BattleTech books reading.")
		CommandsList.append(Com)

		return CommandsList

	def _GenerateTableRow(self, container: dict[str, None], note: "Note") -> dict[str, str | None]:
		"""
		Генерирует данные для заполнения строки таблицы.

		:param container: Словарь, в котром ключи являются названиями колонок.
		:type container: dict[str, None]
		:param note: Запись.
		:type note: Note
		:return: Словарь с подставленными значениями.
		:rtype: dict[str, str | None]
		"""

		#---> ID
		#==========================================================================================#
		container["ID"] = note.id

		#---> Status
		#==========================================================================================#
		match note.status:
			case Statuses.Announced: container["Status"] = FastStyler(Statuses.Announced.value).colorize.magenta
			case Statuses.Planned: container["Status"] = FastStyler(Statuses.Planned.value).colorize.blue
			case Statuses.Reading: container["Status"] = FastStyler(Statuses.Reading.value).colorize.yellow
			case Statuses.Completed: container["Status"] = FastStyler(Statuses.Completed.value).colorize.green
			case Statuses.Dropped: container["Status"] = FastStyler(Statuses.Dropped.value).colorize.red
			case Statuses.Skipped: container["Status"] = FastStyler(Statuses.Skipped.value).colorize.cyan
			case None: container["Status"] = ""

		container["Status"] = {
			CollectionStatuses.Collected: "📦 ",
			CollectionStatuses.Ebook: "🌍 ",
			CollectionStatuses.Wishlist: "🎁 ",
			CollectionStatuses.Ordered: "🚚 ",
			None: "   "
		}[note.collection_status] + container["Status"]

		#---> Name
		#==========================================================================================#
		container["Name"] = note.localized_name or note.name

		#---> Author
		#==========================================================================================#
		Author = note.metainfo.get_field_value("author")
		AuthorsCount = 0
		if type(Author) == tuple: AuthorsCount = len(Author) - 1
		container["Author"] = Author if not AuthorsCount else Author[0] + f" (and {AuthorsCount} other)"
		
		#---> Publication
		#==========================================================================================#
		container["Publication"] = note.metainfo["publication_date"]

		#---> Type
		#==========================================================================================#
		container["Type"] = note.type.value

		#---> Series
		#==========================================================================================#
		Series = note.metainfo.get_field_value("series")
		Series = ToIterable(Series, iterable_type = list) if Series else list()

		Shrapnel = note.metainfo.get_field_value("shrapnel")
		if Shrapnel: Series.append(f"Shrapnel #{Shrapnel}")

		if Series:
			SeriesCount = len(Series)
			container["Series"] = Series[0]

			if SeriesCount > 1:
				SeriesCount -= 1
				container["Series"] += f" (and {SeriesCount} other)"

		else: container["Series"] = ""

		#---> Estimation
		#==========================================================================================#
		container["Estimation"] = ""

		if note.estimation:
			Estimation = "★ " * note.estimation
			if note.estimation == 5: Estimation = FastStyler(Estimation).colorize.green
			elif note.estimation in (3, 4): Estimation = FastStyler(Estimation).colorize.yellow
			elif note.estimation in (1, 2): Estimation = FastStyler(Estimation).colorize.red
			container["Estimation"] = Estimation

		#---> Era
		#==========================================================================================#
		NoteEra = note.era
		if NoteEra: NoteEra = NoteEra.name
		else: NoteEra = ""
		container["Era"] = NoteEra

		return container

class NoteCLI(BaseNoteCLI):
	"""Интерпретатор CLI записи."""

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ ОБРАБОТЧИКИ КОМАНД <<<<< #
	#==========================================================================================#

	def _altname(self, name: str, remove: bool):
		"""
		Управляет альтернативными названиями.

		:param name: Альтернативное название.
		:type name: str
		:param remove: Переключает режимы добавления/удаления названия.
		:type remove: bool
		"""

		if remove: self._Note.remove_another_name(name)
		else: self._Note.add_another_name(name)

	def _collection(self, command: ParsedCommandData):
		"""
		Задаёт статус коллекционирования.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		Flag = command.get_position_parameter("STATUS")

		match Flag.name:
			case "-c": self._Note.set_collection_status(CollectionStatuses.Collected)
			case "-e": self._Note.set_collection_status(CollectionStatuses.Ebook)
			case "-w": self._Note.set_collection_status(CollectionStatuses.Wishlist)
			case "-o": self._Note.set_collection_status(CollectionStatuses.Ordered)

	def _era(self, command: ParsedCommandData):
		"""
		Задаёт статус коллекционирования.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		if command.check_key("--year"): self._Note.set_era_by_year(command.get_key_value("--year"))
		else:
			try: self._Note.set_era_by_index(command.get_position_value("SOURCE"))
			except ValueError: print("Incorrect era index.")

	def _eras(self):
		"""Выводит список эр BattleTech."""

		self._Table: "Table"

		for Era in self._Table.eras:
			StartYear = Era.start_year or "earlier"
			EndYear = Era.end_year or "now"
			print(FastStyler(str(Era.index).ljust(8)).decorate.bold, end = "")
			print(f": {Era.name} [{StartYear} – {EndYear}]")

	def _estimate(self, estimation: int):
		"""
		Задаёт оценку.

		:param estimation: Оценка.
		:type estimation: int
		"""

		try: self._Note.estimate(estimation or None)
		except ValueError as ExceptionData: PrintError(str(ExceptionData))

	def _localname(self, localized_name: str | None):
		"""
		Задаёт локализованное название.

		:param localized_name: Локализованное название.
		:type localized_name: str | None
		"""

		try: self._Note.set_localized_name(localized_name)
		except ValueError as ExceptionData: PrintError(str(ExceptionData))

	def _scount(self, count: int):
		"""
		Задаёт количество историй.

		:param count: Количество историй.
		:type count: int
		"""

		if count and self._Note.type != Types.Compilation: PrintWarning("Stories count expected only for compilations.")
		self._Note.set_stories_count(count)

	def _shrapnel(self, number: int):
		"""
		Задаёт номер журнала Shrapnel.

		:param number: Номер журнала. `0` для очистки.
		:type number: int
		"""

		if self._Note.type != Types.Story:
			PrintWarning("Shrapnel issue number can be setted only for stories.")
			return
		
		self._SetMetainfo("shrapnel", number or None)

	def _status(self, command: ParsedCommandData):
		"""
		Задаёт статус прочтения.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		if command.get_position_value("STATUS") == "*":
			self._Note.set_status(None)
			return

		Flag = command.get_position_parameter("STATUS")

		match Flag.name:
			case "-a": self._Note.set_status(Statuses.Announced)
			case "-c": self._Note.set_status(Statuses.Completed)
			case "-d": self._Note.set_status(Statuses.Dropped)
			case "-p": self._Note.set_status(Statuses.Planned)
			case "-r": self._Note.set_status(Statuses.Reading)
			case "-s": self._Note.set_status(Statuses.Skipped)

	def _type(self, command: ParsedCommandData):
		"""
		Задаёт тип произведения.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		Flag = command.get_position_parameter("TYPE")

		match Flag.name:
			case "-c": self._Note.set_type(Types.Compilation)
			case "-n": self._Note.set_type(Types.Novel)
			case "-s": self._Note.set_type(Types.Story)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteCustomCommand(self, command: ParsedCommandData):
		"""
		Обрабатывает кастомную команду.
		
		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

		match command.name:
			case "altname": self._altname()
			case "author": self._SetMetainfo("author", command.get_position_value("AUTHOR"))
			case "collection": self._collection(command)
			case "comment": self._Note.set_comment(Unstar(command.get_position_value("COMMENT")))
			case "eras": self._eras()
			case "era": self._era(command)
			case "estimate": self._estimate(command.get_position_value("ESTIMATION"))
			case "localname": self._localname(Unstar(command.get_position_value("LOCALNAME")))
			case "pubdate": self._SetMetainfo("publication_date", command.get_position_value("DATE"))
			case "publisher": self._SetMetainfo("publisher", command.get_position_value("PUBLISHER"))
			case "scount": self._scount(command.get_position_value("COUNT"))
			case "shrapnel": self._shrapnel(command.get_position_value("NUMBER"))
			case "series": self._SetMetainfo("series", command.get_position_value("SERIES"))
			case "status": self._status(command)
			case "type": self._type(command)

	def _GenerateCustomCommands(self) -> list[Command]:
		"""
		Возвращает список кастомных команд интерпретатора.

		:return: Возвращает список кастомных команд интерпретатора.
		:rtype: list[Command]
		"""

		CommandsList = list()

		Com = Command("altname", "Manage alternative names.")
		ComPos = Com.create_position("ALT_NAME", "Alternative name.", important = True)
		ComPos.set_argument()
		Com.base.add_flag("-r", description = "Remove another name if exists.")
		CommandsList.append(Com)

		Com = Command("author", "Set author.", category = "Metainfo")
		ComPos = Com.create_position("AUTHOR", "Author or authors list, splitted by \";\" character. Put * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("collection", "Set collection status.")
		ComPos = Com.create_position("STATUS", "Collection status.", important = True)
		ComPos.add_flag("-c", description = "Collected.")
		ComPos.add_flag("-e", description = "Collected as E-book.")
		ComPos.add_flag("-w", description = "In wishlist.")
		ComPos.add_flag("-o", description = "Ordered or payed.")
		CommandsList.append(Com)

		Com = Command("comment", "Set comment to note.")
		ComPos = Com.create_position("COMMENT", "Comment text. Put * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("era", "Set BattleTech era.")
		ComPos = Com.create_position("SOURCE", "Source of era data.", important = True)
		ComPos.set_argument(ParametersTypes.Integer, "Era index.")
		ComPos.add_key("--year", type = ParametersTypes.UnsignedInteger, description = "Year of book events.")
		CommandsList.append(Com)

		Com = Command("eras", "Show list of BattleTech eras.")
		CommandsList.append(Com)

		Com = Command("estimate", "Set estimation.")
		ComPos = Com.create_position("ESTIMATION", f"Estimation from 1 to 5. Put 0 to clear.", important = True)
		ComPos.set_argument(ParametersTypes.UnsignedInteger)
		CommandsList.append(Com)

		Com = Command("localname", "Set localized name.")
		ComPos = Com.create_position("LOCALNAME", "Localized name. Put * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("pubdate", "Set publication date.", category = "Metainfo")
		ComPos = Com.create_position("DATE", "Publication date. Put * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("publisher", "Set publisher.", category = "Metainfo")
		ComPos = Com.create_position("PUBLISHER", "Publication date. Put * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("scount", "Set stories count (for compilation type).")
		ComPos = Com.create_position("COUNT", f"Stories count. Put 0 to clear.", important = True)
		ComPos.set_argument(ParametersTypes.UnsignedInteger)
		CommandsList.append(Com)

		Com = Command("shrapnel", "Set Shrapnel issue number. Only for stories.", category = "Metainfo")
		ComPos = Com.create_position("NUMBER", "Shrapnel issue number. Put 0 to clear.", important = True)
		ComPos.set_argument(ParametersTypes.UnsignedInteger)
		CommandsList.append(Com)

		Com = Command("series", "Set series.", category = "Metainfo")
		ComPos = Com.create_position("SERIES", "Book series. Put * to clear.", important = True)
		ComPos.set_argument()
		CommandsList.append(Com)

		Com = Command("status", "Set reading status.")
		ComPos = Com.create_position("STATUS", "Reading status.", important = True)
		ComPos.add_flag("-a", description = "Announced.")
		ComPos.add_flag("-r", description = "Reading.")
		ComPos.add_flag("-c", description = "Completed.")
		ComPos.add_flag("-d", description = "Dropped.")
		ComPos.add_flag("-p", description = "Planned.")
		ComPos.add_flag("-s", description = "Skipped.")
		ComPos.set_argument(description = "Put * to clear.")
		CommandsList.append(Com)

		Com = Command("type", "Set type of book.")
		ComPos = Com.create_position("TYPE", "Type of book.", important = True)
		ComPos.add_flag("-c", description = "Compilation.")
		ComPos.add_flag("-n", description = "Novel.")
		ComPos.add_flag("-s", description = "Story.")
		CommandsList.append(Com)

		return CommandsList

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self._Note: "Note"

	def _ViewNote(self):
		"""Отображает запись."""

		#---> Объявление стилей.
		#==========================================================================================#
		BOLD = TextStyler(decorations = Codes.Decorations.Bold)

		#---> Генерация литералов.
		#==========================================================================================#
		UsedName = self._Note.name
		AnotherNames = list(self._Note.another_names)
		StoriesNotes = self._Note.table.binder.local.get_slaves(self._Note.id)
		
		if self._Note.localized_name:
			UsedName = self._Note.localized_name
			if self._Note.name: AnotherNames.insert(0, f"👑 {self._Note.name}" if AnotherNames else self._Note.name)

		CollectionStatusEmojiDetermination = {
			CollectionStatuses.Collected: "📦",
			CollectionStatuses.Ebook: "🌎",
			CollectionStatuses.Ordered: "🚚",
			CollectionStatuses.Wishlist: "🎁",
			None: ""
		}
		StatusEmojiDetermination = {
			Statuses.Announced: "ℹ️",
			Statuses.Reading: "📖",
			Statuses.Completed: "✅",
			Statuses.Dropped: "⛔",
			Statuses.Skipped: "🚫",
			Statuses.Planned: "📋",
			None: ""
		}

		CollectionStatusEmoji = CollectionStatusEmojiDetermination[self._Note.collection_status]
		StatusEmoji = StatusEmojiDetermination[self._Note.status]

		#---> Вывод данных записи.
		#==========================================================================================#
		IsFirstLinePrinted = False

		if UsedName:
			print(BOLD.get_styled_text(UsedName), end = "")
			IsFirstLinePrinted = True

		if CollectionStatusEmoji:
			print(f" {CollectionStatusEmoji}", end = "")
			IsFirstLinePrinted = True

		if StatusEmoji:
			if IsFirstLinePrinted: print(" ", end = "")
			print(StatusEmoji, end = "")
			IsFirstLinePrinted = True

		if IsFirstLinePrinted: print("")
		for CurrentLine in AnotherNames: print(" " * 4 + CurrentLine)

		#---> Вывод свойств записи.
		#==========================================================================================#
		if any((self._Note.type, self._Note.era, self._Note.estimation, self._Note.comment)): print(BOLD.get_styled_text("PROPERTIES:"))
		if self._Note.type: print(" " * 4 + f"✒️  Type: {self._Note.type.value}")
		if self._Note.era: print(" " * 4 + f"🏺 Era: {self._Note.era.name}")
		if self._Note.estimation: print(" " * 4 + f"⭐ Estimation: {self._Note.estimation}")
		if self._Note.comment: print(" " * 4 + f"💭 Comment: {self._Note.comment}")
		if all((not self._Note.table.binder.local.get_slaves(self._Note.id), self._Note.stories_count)): print(" " * 4 + f"📜 Stories: {self._Note.stories_count}")

		#---> Вывод историй.
		#==========================================================================================#
		if StoriesNotes:
			MaxStoriesCount = self._Note.stories_count

			if MaxStoriesCount:
				StoriesCount = len(StoriesNotes)
				MaxStoriesCount = f" ({StoriesCount} / {MaxStoriesCount})"

			else: MaxStoriesCount = ""
			
			print(BOLD.get_styled_text(f"STORIES{MaxStoriesCount}:"))

			for Story in StoriesNotes:
				Story: "Note"

				StoryNames = list()
				if Story.localized_name: StoryNames.append(Story.localized_name)
				if Story.name: StoryNames.append(Story.name)
				StoryNames = " / ".join(StoryNames)

				StatusEmoji = StatusEmojiDetermination[Story.status]
				CollectionStatusEmoji = CollectionStatusEmojiDetermination[Story.collection_status]

				print(" " * 4 + f"> {Story.id}. {StoryNames} {StatusEmoji} {CollectionStatusEmoji}")