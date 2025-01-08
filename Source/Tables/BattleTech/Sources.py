from Source.Core.Base import Module, ModuleCLI, Note, NoteCLI
from Source.CLI.Templates import Columns
from Source.Core.Exceptions import *
from Source.Core.Errors import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.CLI.TextStyler import Styles, TextStyler
from dublib.Engine.Bus import ExecutionError, ExecutionStatus

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

		Com = Command("code", "Set code.")
		Com.add_argument(description = "Code of sourcebook.", important = True)
		CommandsList.append(Com)

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

		if parsed_command.name == "code":
			Status = self._Note.set_code(parsed_command.arguments[0])

		elif parsed_command.name == "comment":
			Status = self._Note.set_comment(parsed_command.arguments[0])

		elif parsed_command.name == "era":
			Status = self._Note.set_era(parsed_command.arguments[0])

		elif parsed_command.name == "estimate":
			Status = self._Note.estimate(parsed_command.arguments[0])

		elif parsed_command.name == "link":
			Status = self._Note.set_link(parsed_command.arguments[0])

		elif parsed_command.name == "mark":
			Status = self._Note.set_bookmark(parsed_command.arguments[0])

		elif parsed_command.name == "meta":
			Status = ExecutionStatus(0)
			
			if "set" in parsed_command.flags:
				Status = self._Note.set_metainfo(parsed_command.arguments[0],  parsed_command.arguments[1])

			if parsed_command.check_flag("unset"):
				Status = self._Note.delete_metainfo(parsed_command.arguments[0])

		elif parsed_command.name == "set":

			if "localname" in parsed_command.keys.keys():
				Status = self._Note.set_localized_name(parsed_command.keys["localname"])

			if "name" in parsed_command.keys.keys():
				Status = self._Note.rename(parsed_command.keys["name"])

			if "status" in parsed_command.keys.keys():
				Status = self._Note.set_status(parsed_command.keys["status"])

		elif parsed_command.name == "unset":

			if parsed_command.check_key("altname"):
				Status = self._Note.delete_another_name(parsed_command.get_key_value("altname"))

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированные данные записи."""

		Status = ExecutionStatus(0)

		try:
			#---> Получение данных.
			#==========================================================================================#
			UsedName = ""
			AnotherNames = list()

			if self._Note.localized_name:
				UsedName = self._Note.localized_name
				AnotherNames.append(self._Note.name)

			else:
				UsedName = self._Note.name

			if len(UsedName) and self._Note.code: UsedName = f"{UsedName} [{self._Note.code}]"

			#---> Вывод описания записи.
			#==========================================================================================#
			if UsedName: print(TextStyler(UsedName).decorate.bold, end = "")
			print(f" {self._Note.emoji_status}")
			if self._Note.bookmark: print(f"🔖 {self._Note.bookmark} page")
			if self._Note.comment: print(f"💭 {self._Note.comment}")
			if self._Note.link: print(f"🔗 {self._Note.link}")
			if AnotherNames: print(TextStyler(f"ANOTHER NAMES: ").decorate.bold)
			for AnotherName in AnotherNames: print(TextStyler(f"    {AnotherName}").decorate.italic)

			#---> Вывод классификаторов записи.
			#==========================================================================================#

			if self._Note.metainfo:
				print(TextStyler(f"METAINFO:").decorate.bold)
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		except: Status = ERROR_UNKNOWN

		return Status

class BattleTech_Sources_ModuleCLI(ModuleCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
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
					"Type": []
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
							if Note.localized_name: Names.append(Note.localized_name)

							for Name in Names:
								if search.lower() in Name.lower(): SearchBuffer.append(Note)

						Notes = SearchBuffer
					
					for Note in Notes:
						Name = Note.localized_name if Note.localized_name else Note.name
						if not Name: Name = ""
						Type = Note.metainfo["type"] if "type" in Note.metainfo.keys() else ""
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
						Content["Type"].append(Type)

					if len(Notes): Columns(Content, sort_by = SortBy, reverse = Reverse)
					else: Status.message = "Notes not found."

				else:
					Status.message = "Table is empty."

			except: Status = ERROR_UNKNOWN

			return Status

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
		"code": None,
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
	def bookmark(self) -> int | None:
		"""Закладка."""

		return self._Data["bookmark"]

	@property
	def code(self) -> int | None:
		"""Код."""

		return self._Data["code"]

	@property
	def comment(self) -> str | None:
		"""Комментарий."""

		return self._Data["comment"]

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
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._CLI = BattleTech_Sources_NoteCLI

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

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

	def set_code(self, code: str) -> ExecutionStatus:
		"""
		Задаёт код соурсбука.
			code – код.
		"""

		Status = ExecutionStatus(0)

		try:

			if code == "*":
				code = None
				Status.message = "Code removed."

			else:
				code = int(code)
				Status.message = "Code updated."

			self._Data["code"] = code
			self.save()

		except: Status = ERROR_UNKNOWN

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
			self._Data["status"] = status
			self.save()
			Status.message = "Status updated."

		except:
			Status = ERROR_UNKNOWN

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
			"recycle_id": True
		},
		"metainfo_rules": {
			"type": ["handbook", "sourcebook"]
		},
		"viewer": {
			"colorize": True
		},
		"custom": {}
	}

	#==========================================================================================#
	# >>>>> ДОПОЛНИТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#
	
	@property
	def eras(self) -> dict:
		"""Эпохи BattleTech."""

		return self._Table.eras
	
	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = BattleTech_Sources_Note
		self._CLI = BattleTech_Sources_ModuleCLI