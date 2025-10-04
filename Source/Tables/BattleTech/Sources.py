from Source.Core.Base import Module, ModuleCLI, Note, NoteCLI
from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class BattleTech_Sources_NoteCLI(NoteCLI):
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

		Com = Command("code", "Set code.")
		Com.base.add_argument(ParametersTypes.Number, "[METAINFO] Product code of sourcebook.", important = True)
		CommandsList.append(Com)

		Com = Command("collection", "Set collection status.")
		Com.base.add_argument(description = "Status: collected (c), ebook (e), whishlist (w), ordered (o).", important = True)
		CommandsList.append(Com)

		Com = Command("comment", "Set comment to note.")
		Com.base.add_argument(description = "Comment text or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("link", "Attach link to note.")
		Com.base.add_argument(description = "URL or * to remove.", important = True)
		CommandsList.append(Com)

		Com = Command("localname", "Set localized name.")
		Com.base.add_argument(description = "Localized name.", important = True)
		CommandsList.append(Com)

		Com = Command("type", "Set sourcebook type.")
		Com.base.add_argument(description = "One of types: sourcebook (s), scenario pack (p).", important = True)
		CommandsList.append(Com)

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()
		self._Note: BattleTech_Sources_Note

		if parsed_command.name == "altname":
			if parsed_command.check_flag("d"): Status = self._Note.remove_another_name(parsed_command.arguments[0])
			else: Status = self._Note.add_another_name(parsed_command.arguments[0])

		elif parsed_command.name == "code":
			Value = parsed_command.arguments[0]
			if Value == "*": Status = self._Note.remove_metainfo("product_code")
			else: Status = self._Note.set_metainfo("product_code", Value)

		elif parsed_command.name == "collection":
			Status = self._Note.set_collection_status(parsed_command.arguments[0])

		elif parsed_command.name == "comment":
			Status = self._Note.set_comment(parsed_command.arguments[0])

		elif parsed_command.name == "link":
			Status = self._Note.set_link(parsed_command.arguments[0])

		elif parsed_command.name == "localname":
			Status = self._Note.set_localized_name(parsed_command.arguments[0])

		elif parsed_command.name == "type":
			Status = self._Note.set_type(parsed_command.arguments[0])

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированные данные записи."""

		Status = ExecutionStatus()

		try:
			#---> Получение данных.
			#==========================================================================================#
			self._Note: BattleTech_Sources_Note
			self._Table: BattleTech_Sources
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
			if self._Note.emoji_collection_status: print(self._Note.emoji_collection_status + " ", end = "")
			if UsedName: print(FastStyler(UsedName).decorate.bold, end = "")
			if "product_code" in self._Note.metainfo.keys(): print(" [" + str(self._Note.metainfo["product_code"]) + "]", end = "")
			print("")
			for AnotherName in AnotherNames: print(f"    {AnotherName}")

			#---> Вывод свойств.
			#==========================================================================================#
			if self._Note.comment or self._Note.link: print(FastStyler("PROPERTIES:").decorate.bold)
			if self._Note.comment: print(f"    💭 Comment: {self._Note.comment}")
			if self._Note.link: print(f"    🔗 Link: {self._Note.link}")

			#---> Вывод вложений.
			#==========================================================================================#
			Attachments = self._Note.attachments

			if Attachments.count:
				print(FastStyler("ATTACHMENTS:").decorate.bold)
				for Slot in Attachments.slots: print(f"    {Slot}: " + FastStyler(Attachments.get_slot_filename(Slot)).decorate.italic)

		except ZeroDivisionError: Status.push_error(Errors.UNKNOWN)

		return Status

class BattleTech_Sources_ModuleCLI(ModuleCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def _BuildNoteRow(self, note: "BattleTech_Sources_Note") -> dict[str, str]:
		"""
		Строит строку описания записи для таблицы и возвращает словарь в формате: название колонки – данные.
			note – обрабатываемая запись.
		"""

		Row = dict()
		Row["ID"] = note.id

		Status = note.collection_status
		if Status == "collected": Status = TextStyler(Status, text_color = Codes.Colors.Green).get_styled_text()
		elif Status == "ebook": Status = TextStyler(Status, text_color = Codes.Colors.Cyan).get_styled_text()
		elif Status == "ordered": Status = TextStyler(Status, text_color = Codes.Colors.Yellow).get_styled_text()

		Row["Status"] = f"{note.emoji_collection_status} {Status}" if Status else ""
		Row["Code"] = note.code or ""
		Row["Name"] = note.localized_name or note.name
		Row["Ebook"] = "✅" if note.attachments.check_slot_occupation("ebook") else "❌"
		Row["Type"] = FastStyler(note.type.replace("_", " ").title()).decorate.italic if note.type else ""

		return Row
	
#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class BattleTech_Sources_Note(Note):
	"""Запись о соурсбуке BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"localized_name": None,
		"another_names": [],
		"type": "Sourcebook",
		"comment": None,
		"link": None,
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
	def code(self) -> int | None:
		"""Код продукта."""

		Code = None
		if "product_code" in self.metainfo.keys(): Code = self.metainfo["product_code"]

		return Code

	@property
	def collection_status(self) -> str | None:
		"""Статус коллекционирования."""

		return self._Data["collection_status"]

	@property
	def comment(self) -> str | None:
		"""Комментарий."""

		return self._Data["comment"]

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
	def link(self) -> str | None:
		"""Ссылка."""

		return self._Data["link"]

	@property
	def localized_name(self) -> str | None:
		"""Локализованное название."""

		return self._Data["localized_name"]

	@property
	def type(self) -> str | None:
		"""Тип соурсбука."""

		return self._Data["type"]

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = BattleTech_Sources_NoteCLI

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

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
	
	def set_collection_status(self, status: str) -> ExecutionStatus:
		"""
		Задаёт статус коллекционирования.
			status – статус.
		"""

		Status = ExecutionStatus()
		Statuses = {
			"c": "collected",
			"e": "ebook",
			"w": "wishlist",
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

	def set_type(self, type: str) -> ExecutionStatus:
		"""
		Задаёт тип соурсбука.
			type – тип.
		"""

		Status = ExecutionStatus()
		Types = {
			"d": "Dossiers",
			"c": "Combat Manuals",
			"f": "Force Manuals",
			"h": "Handbooks",
			"o": "Spotlight On",
			"t": "Touring the Stars",

			"p": "Scenario Pack",
			"s": "Sourcebook",
			"*": None
		}

		try:
			if type in Types.keys(): type = Types[type]
			self._Data["type"] = type
			self.save()
			if type: Status.push_message("Type updated.")
			else: Status.push_message("Type removed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

class BattleTech_Sources(Module):
	"""Таблица соурсбуков BattleTech."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "battletech:sources"
	MANIFEST: dict = {
		"object": "module",
		"type": TYPE,
		"common": {
			"recycle_id": True,
			"attachments": True
		},
		"metainfo_rules": {
			"product_code": None
		},
		"viewer": {
			"autoclear": False,
			"colorize": True,
			"columns": {
				"ID": True,
				"Status": True,
				"Code": True,
				"Name": True,
				"Ebook": True,
				"Type": True
			}
		}
	}
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Sources_Note
		self._CLI = BattleTech_Sources_ModuleCLI