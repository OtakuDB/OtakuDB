from ..Enums import CollectionStatuses, Statuses, Types

from Source.Interfaces.CLI.Base import BaseTableCLI, BaseNoteCLI
from Source.Interfaces.CLI.Functions import Unstar

from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler
from dublib.CLI.Terminalyzer import Command, ParsedCommandData
from dublib.CLI.Templates.Bus import PrintError

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from ..note import Note

class TableCLI(BaseTableCLI):
	"""Интерпретатор CLI таблицы."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

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
		match note.collection_status:
			case CollectionStatuses.Collected: container["Status"] = "📦 " + FastStyler(CollectionStatuses.Collected.value).colorize.green
			case CollectionStatuses.Ebook: container["Status"] = "🌍 " + FastStyler(CollectionStatuses.Ebook.value).colorize.cyan
			case CollectionStatuses.Wishlist: container["Status"] = "🎁 " + FastStyler(CollectionStatuses.Wishlist.value).colorize.blue
			case CollectionStatuses.Ordered: container["Status"] = "🚚 " + FastStyler(CollectionStatuses.Ordered.value).colorize.yellow

		#---> Code
		#==========================================================================================#
		container["Code"] = note.metainfo["product_code"]

		#---> Name
		#==========================================================================================#
		container["Name"] = note.localized_name or note.name

		#---> Ebook
		#==========================================================================================#
		container["Ebook"] = "✅" if note.attachments.is_slot_occupied("ebook") else "❌"

		#---> Ebook
		#==========================================================================================#
		if note.type: container["Type"] = FastStyler(note.type.value).decorate.italic

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

	def _localname(self, localized_name: str | None):
		"""
		Задаёт локализованное название.

		:param localized_name: Локализованное название.
		:type localized_name: str | None
		"""

		try: self._Note.set_localized_name(localized_name)
		except ValueError as ExceptionData: PrintError(str(ExceptionData))

	def _status(self, command: ParsedCommandData):
		"""
		Задаёт статус прочтения.

		:param command: Данные команды.
		:type command: ParsedCommandData
		"""

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
			case "-d": self._Note.set_collection_status(Types.Dossier)
			case "-cm": self._Note.set_collection_status(Types.CombatManual)
			case "-fom": self._Note.set_collection_status(Types.ForceManual)
			case "-fim": self._Note.set_collection_status(Types.FieldManual)
			case "-h": self._Note.set_collection_status(Types.Handbook)
			case "-so": self._Note.set_collection_status(Types.SpotlightOn)
			case "-sp": self._Note.set_collection_status(Types.ScenarioPack)
			case "-s": self._Note.set_collection_status(Types.Sourcebook)
			case "-ts": self._Note.set_collection_status(Types.TouringStars)

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
			case "collection": self._collection(command)
			case "comment": self._Note.set_comment(Unstar(command.get_position_value("COMMENT")))
			case "localname": self._localname(Unstar(command.get_position_value("LOCALNAME")))
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

		Com = Command("localname", "Set localized name.")
		ComPos = Com.create_position("LOCALNAME", "Localized name. Put * to clear.", important = True)
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
		CommandsList.append(Com)

		Com = Command("type", "Set type of sourcebook.")
		ComPos = Com.create_position("TYPE", "Type of sourcebook.", important = True)
		ComPos.add_flag("-d", description = "Dossier.")
		ComPos.add_flag("-cm", description = "Combat Manual.")
		ComPos.add_flag("-fom", description = "Force Manual.")
		ComPos.add_flag("-fim", description = "Field Manual.")
		ComPos.add_flag("-h", description = "Handbook.")
		ComPos.add_flag("-so", description = "Spotlight On.")
		ComPos.add_flag("-sp", description = "Scenario Pack.")
		ComPos.add_flag("-s", description = "Sourcebook.")
		ComPos.add_flag("-ts", description = "Touring the Stars.")
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
		
		if self._Note.localized_name:
			UsedName = self._Note.localized_name
			Mark = "👑 " if self._Note.another_names else ""
			if self._Note.name: AnotherNames = [Mark + self._Note.name] + AnotherNames

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
		if any((self._Note.type, self._Note.comment)): print(BOLD.get_styled_text("PROPERTIES:"))
		if self._Note.type: print(" " * 4 + f"✒️  Type: {self._Note.type.value}")
		if self._Note.comment: print(" " * 4 + f"💭 Comment: {self._Note.comment}")