from .Structs import Attachments, Interfaces, SupportedInterfaces
from .Manifest import Manifest
from .Binder import Binder

from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

# Интерфейсы.
from Source.Interfaces.CLI.Base import TableCLI, ModuleCLI, NoteCLI

from dublib.Methods.Filesystem import NormalizePath, ReadJSON, WriteJSON
from dublib.CLI.TextStyler import FastStyler

from typing import TYPE_CHECKING
from os import PathLike
import shutil
import os

if TYPE_CHECKING:
	from Source.Core.Session import Session

#==========================================================================================#
# >>>>> ОСНОВНЫЕ КЛАССЫ <<<<< #
#==========================================================================================#

class Note:
	"""Базовая запись."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	BASE_NOTE = {
		"name": None,
		"metainfo": {}
	}

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> Attachments:
		"""Данные вложений."""

		AttachmentsData = None
		Path = self.__GeneratePath(point = f".attachments/{self._ID}")
		AttachmentsDictionary = dict()
		if "attachments" in self._Data: AttachmentsDictionary = self._Data["attachments"]
		AttachmentsData = Attachments(Path, AttachmentsDictionary)

		return AttachmentsData
	
	@property
	def binded_notes(self) -> tuple["Note"]:
		"""Связанные записи."""

		return self._Table.binder.local.get_binded_notes(self._ID)

	@property
	def id(self) -> int:
		"""ID записи."""

		return self._ID
	
	@property
	def interfaces(self) -> SupportedInterfaces:
		"""Поддерживаемые интерфейсы."""

		return self._Interfaces

	@property
	def metainfo(self) -> dict:
		"""Метаданные."""

		return self._Data["metainfo"]

	@property
	def name(self) -> str | None:
		"""Название записи."""

		return self._Data["name"]

	@property
	def slots_info(self) -> dict[str, str]:
		"""Словарь описаний данных слотов вложений."""

		return self._GetSlotsInfo()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def searchable(self) -> list[str]:
		"""Список строк, которые представляют контент для поисковых запросов."""

		Strings = list()

		Strings.append(self._Data["name"])
		if "localized_name" in self._Data.keys(): Strings.append(self._Data["localized_name"])
		if "another_name" in self._Data.keys() and type(self._Data["another_name"]) == str: Strings.append(self._Data["another_name"])
		if "another_names" in self._Data.keys() and type(self._Data["another_names"]) == list: Strings += self._Data["another_names"]

		Strings = list(filter(lambda Element: bool(Element), Strings))

		return Strings

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __GeneratePath(self, point: str | None = None) -> str:
		"""
		Генерирует используемый путь.
			point – добавляемое к пути таблицы значение.
		"""

		Path = None
		if not point: point = ""
		if self._Table.is_module: Path = f"{self._Table.storage}/{self._Table.table.name}/{self._Table.name}/{point}"
		else: Path = f"{self._Table.storage}/{self._Table.name}/{point}"
		Path = NormalizePath(Path)

		return Path

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetSlotsInfo(self) -> dict[str, str]:
		"""
		Возвращает словарь описаний слотов вложений.

		:return: Словарь описаний данных слотов вложений. Ключ – название слота, значение – описание.
		:rtype: dict[str, str]
		"""

		return dict()

	def _PostBindMethod(self):
		"""Метод, выполняющийся после изменения привязанных записей."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		pass

	def _SpecifyInterfaces(self) -> SupportedInterfaces:
		"""
		Определяет объекты с реализацией интерфейсов.

		:return: Контейнер поддерживаемых интерфейсов.
		:rtype: SupportedInterfaces
		"""

		self._Interfaces[Interfaces.CLI] = NoteCLI

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Table", note_id: int):
		"""
		Базовая запись.
			table – таблица;\n
			note_id – ID записи.
		"""

		self._Table = table
		self._ID = note_id

		self._Path = self.__GeneratePath(point = f"{note_id}.json")
		self._Data = ReadJSON(self._Path)
		self._Interfaces = SupportedInterfaces()
		
		self._PostInitMethod()
		self._SpecifyInterfaces()

	def get_interface(self, interface: Interfaces) -> "NoteCLI":
		"""
		Инициализирует интерпретатор интерфейса.

		:param interface: Тип интерфейса.
		:type interface: Interfaces
		:return: Интерпретатор интерфейса.
		:rtype: NoteCLI
		"""

		return self.interfaces[interface](self._Table, self)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РЕДАКТИРОВАНИЯ <<<<< #
	#==========================================================================================#

	def attach(self, path: str, slot: str | None = None, force: bool = False) -> ExecutionStatus:
		"""
		Прикрепляет файл к записи.
			path – путь к файлу;\n
			slot – именной слот для файла;\n
			force – включает режим перезаписи.
		"""

		Status = ExecutionStatus()

		try:
			if not self._Table.manifest.common.is_attachments_enabled: 
				Status.push_error(Errors.Note.ATTACHMENTS_DISABLED)
				return Status
			
			path = NormalizePath(path)

			if not os.path.exists(path):
				Status.push_error(Errors.PATH_NOT_FOUND)
				return Status
			
			Path = self.__GeneratePath(point = f".attachments/{self._ID}")
			if not os.path.exists(Path): os.makedirs(Path)
			AttachmentsData = self._Data["attachments"] if "attachments" in self._Data.keys() else None
			AttachmentsObject = Attachments(Path, AttachmentsData)

			if slot:
				AttachmentsObject.attach_to_slot(path, slot, force)
				Status.push_message(f"File \"{path}\" attached to #{self._ID} note on slot \"{slot}\".")

			else:
				AttachmentsObject.attach(path, force)
				Status.push_message(f"File \"{path}\" attached to #{self._ID} note.")

			self._Data["attachments"] = AttachmentsObject.dictionary
			self.save()
			
		except AttachmentsDenied: Status.push_error(Errors.Note.ATTACHMENT_DENIED)

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def bind_note(self, note_id: int | str) -> ExecutionStatus:
		"""
		Привязывает другую запись к текущей.
			note_id – ID записи в текущей таблице или идентификатор записи в другом модуле.
		"""

		Status = ExecutionStatus()
		if type(note_id) == str and note_id.isdigit(): note_id = int(note_id)

		if type(note_id) == int: Status += self._Table.binder.local.bind_note(self.id, note_id)
		elif type(note_id) == str: Status += self._Table.binder.general.bind_note(self.id, note_id)

		self._PostBindMethod()

		return Status

	def remove_metainfo(self, key: str) -> ExecutionStatus:
		"""
		Удаляет поле метаданных.
			key – ключ поля.
		"""

		Status = ExecutionStatus()

		try:
			del self._Data["metainfo"][key]
			self.save()
			Status.push_message("Metainfo field removed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def remove_note_binding(self, note_id: int | str) -> ExecutionStatus:
		"""
		Удаляет привязку записи к текущей.
			note_id – ID записи в текущей таблице или идентификатор записи в другом модуле.
		"""

		Status = ExecutionStatus()

		try:
			if type(note_id) == str and note_id.isdigit(): note_id = int(note_id)

			if type(note_id) == int: self._Table.binder.local.remove_binding(self.id, note_id)
			elif type(note_id) == str: self._Table.binder.general.remove_binding(self.id, note_id)

		except: Status.push_error(Errors.UNKNOWN)

		self._PostBindMethod()

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает запись.
			name – название записи.
		"""

		Status = ExecutionStatus()
		name = name.strip()

		try:
			if name == "*":
				name = None
				Status.push_message("Note name removed.")

			else:
				Status.push_message("Note renamed.")

				if name in tuple(Element.name for Element in self._Table.notes):
					Status.push_warning("Note with same name already exists.")

			self._Data["name"] = name
			self.save()
			
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def save(self) -> ExecutionStatus:
		"""Сохраняет запись."""

		Status = ExecutionStatus()

		try: WriteJSON(self._Path, self._Data)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_id(self, id: int) -> ExecutionStatus:
		"""
		Задаёт новое значение ID.
			id – идентификатор.
		"""

		Status = ExecutionStatus()

		try:
			OldPath = self._Path
			self._Path = self.__GeneratePath(f"{id}.json")
			os.rename(OldPath, self._Path)
			
			if self.attachments.count > 0:
				OldPath = self.__GeneratePath(f".attachments/{self._ID}")
				NewPath = self.__GeneratePath(f".attachments/{id}")
				shutil.move(OldPath, NewPath)

			self._Table.binder.local.fix_bindings(self._ID, id, save = True)
			self._Table.binder.general.fix_bindings_by_note_id(self._ID, id, save = True)
			self._ID = id

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def set_metainfo(self, key: str, data: str) -> ExecutionStatus:
		"""
		Задаёт значение поля метаданных.
			key – ключ поля;\n
			data – значение.
		"""

		Status = ExecutionStatus()
		data = data.strip()
		
		try:
			Rules = self._Table.manifest.metainfo_rules
			if key in Rules.fields and Rules[key] and data not in Rules[key]: raise MetainfoBlocked()
			if type(data) == str and data.isdigit(): data = int(data)
			self._Data["metainfo"][key] = data
			self._Data["metainfo"] = dict(sorted(self._Data["metainfo"].items()))
			self.save()
			Status.push_message("Metainfo field updated.")

		except MetainfoBlocked: Status.push_error(Errors.Note.METAINFO_BLOCKED)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def unattach(self, filename: str | None = None, slot: str | None = None) -> ExecutionStatus:
		"""
		Удаляет вложение по имени файла или слоту.
			filename – имя файла;\n
			slot – слот.
		"""

		Status = ExecutionStatus()

		if not filename and not slot:
			Status.push_error("no_filename_or_slot_to_unattach")
			return Status

		try:
			Path = self.__GeneratePath(point = f".attachments/{self._ID}")
			AttachmentsData = self._Data["attachments"] if "attachments" in self._Data.keys() else None
			AttachmentsObject = Attachments(Path, AttachmentsData)

			if filename:
				AttachmentsObject.unattach(filename)
				Status.push_message(f"File \"{filename}\" unattached.")

			else: 
				AttachmentsObject.clear_slot(slot)
				Status.push_message(f"Attachment slot \"{slot}\" cleared.")

			self._Data["attachments"] = AttachmentsObject.dictionary
			self.save()

			AttachmentsDirectory = self.__GeneratePath(point = ".attachments")
			if not os.listdir(AttachmentsDirectory): os.rmdir(AttachmentsDirectory)

		except: Status.push_error(Errors.UNKNOWN)

		return Status

class Table:
	"""Базовая таблица."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "table"

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def binder(self) -> Binder:
		"""Менеджер связей объектов."""

		return self._Binder

	@property
	def interfaces(self) -> SupportedInterfaces:
		"""Поддерживаемые интерфейсы."""

		return self._Interfaces

	@property
	def is_module(self) -> bool:
		"Указывает, является ли таблица модулем."

		return self._IsModule

	@property
	def manifest(self) -> Manifest:
		"""Манифест таблицы."""

		return self._Manifest

	@property
	def name(self) -> str:
		"""Название таблицы."""

		return self._Name

	@property
	def notes(self) -> tuple[Note]:
		"""Список записей."""

		return tuple(self._Notes.values())
	
	@property
	def notes_id(self) -> list[int]:
		"""Список ID записей."""

		return self._Notes.keys()

	@property
	def path(self) -> str:
		"""Путь к директории таблицы."""

		return self._Path

	@property
	def session(self) -> "Session":
		"""Сессия."""

		return self._Session

	@property
	def storage(self) -> str:
		"""Путь к хранилищу таблиц."""

		return self._StorageDirectory

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GenerateNewID(self, id_View: list[int]) -> int:
		"""
		Генерирует новый ID.
			id_View – список существующих ID.
		"""

		NewID = None
		if type(id_View) != list: id_View = list(id_View)

		if self.manifest.common.recycle_id:

			for ID in range(1, len(id_View) + 1):

				if ID not in id_View:
					NewID = ID
					break

		if not NewID: NewID = int(max(id_View)) + 1 if len(id_View) > 0 else 1

		return NewID

	def _GetNotesID(self) -> list[int]:
		"""Возвращает список ID записей в таблице, полученный путём сканирования файлов JSON."""

		ListID = list()
		Files = os.listdir(self._Path)
		Files = list(filter(lambda File: File.endswith(".json"), Files))

		for File in list(Files): 
			if not File.replace(".json", "").isdigit(): Files.remove(File)

		for File in Files: ListID.append(int(File.replace(".json", "")))
		
		return ListID

	def _ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		self._Notes[note_id] = self._Note(self, note_id)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyManifest(self, path: PathLike) -> Manifest:
		"""
		Возвращает пустой манифест. Переопределите для настройки.

		:param path: Путь к каталогу таблицы.
		:type path: PathLike
		:return: Пустой манифест.
		:rtype: Manifest
		"""

		Buffer = Manifest(path)
		Buffer.suppress_saving(True)
		Buffer.set_object("table")

		return Buffer

	def _PostCreateMethod(self):
		"""Метод, выполняющийся после создания таблицы."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = Note

	def _PostOpenMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	def _SpecifyInterfaces(self) -> SupportedInterfaces:
		"""
		Определяет объекты с реализацией интерфейсов.

		:return: Контейнер поддерживаемых интерфейсов.
		:rtype: SupportedInterfaces
		"""

		self._Interfaces[Interfaces.CLI] = TableCLI

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, session: "Session", storage: PathLike, name: str):
		"""
		Базовая таблица.

		:param session: Сессия.
		:type session: Session
		:param storage: Путь к каталогу таблицы.
		:type storage: PathLike
		:param name: Название таблицы.
		:type name: str
		"""
		
		self._Session = session
		self._StorageDirectory = NormalizePath(storage)
		self._Name = name

		self._Path = f"{self._StorageDirectory}/{name}"
		self._Notes: dict[int, Note] = dict()
		self._Manifest = None
		self._Binder = Binder(self._Session.driver, self)
		self._Interfaces = SupportedInterfaces()
		self._IsModule = False
		self._Note = None
		
		self._PostInitMethod()
		self._SpecifyInterfaces()

	def get_interface(self, interface: Interfaces) -> "TableCLI":
		"""
		Инициализирует интерпретатор интерфейса.

		:param interface: Тип интерфейса.
		:type interface: Interfaces
		:return: Интерпретатор интерфейса.
		:rtype: TableCLI
		"""

		return self.interfaces[interface](self)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РЕДАКТИРОВАНИЯ <<<<< #
	#==========================================================================================#

	def change_note_id(self, note_id: int | str, new_id: int | str, mode: str | None = None) -> ExecutionStatus:
		"""
		Изменяет ID записи согласно указанному режиму.
			note – ID существующей записи;\n
			new_id – новый ID;\n
			mode – режим: i – вставка, o – перезапись, s – обмен.
		"""

		Status = ExecutionStatus()
		IsTargetNoteExists = new_id in self._Notes.keys()
		
		if note_id not in self._Notes.keys():
			Status.push_error(Errors.Table.NO_NOTE)
			Status["print"] = note_id
			return Status

		if IsTargetNoteExists and not mode:
			Status.push_error("Table.ERROR_NOTE_ALREADY_EXISTS")
			return Status
		
		if mode not in [None, "i", "o", "s"]:
			Status.push_error("Table.UNKNOWN_CHID_MODE")
			return Status

		try:
			note_id = int(note_id)
			new_id = int(new_id)

		except ValueError:
			Status.push_error(Errors.Table.INCORRECT_NOTE_ID)
			return Status
		
		if IsTargetNoteExists:
			
			if mode == "i":
				self.change_note_id(note_id, 0)
				NotesID = list(self._Notes.keys())
				NotesID = sorted(NotesID)
				Buffer = list(NotesID)

				for ID in Buffer:
					if ID < new_id: NotesID.remove(ID)

				Buffer = list(NotesID)
				NewBuffer = list()
				IsFirst = True

				for ID in Buffer:

					if ID + 1 in Buffer:
						NewBuffer.append(ID)

					elif IsFirst: 
						NewBuffer.append(ID)
						break

				NotesID = NewBuffer
				if note_id in NotesID: NotesID.remove(note_id)
				NotesID.reverse()

				for ID in NotesID: Status = self.change_note_id(ID, ID + 1)
				if Status.has_errors: return Status
				Status = self.change_note_id(0, new_id)
				if Status.has_errors: return Status
				Status.push_message(f"Note #{note_id} inserted to position #{new_id}.")

			elif mode == "o":
				self.delete_note(new_id)
				self._Notes[note_id].set_id(new_id)
				Status.push_message(f"Note #{new_id} overwritten.")

			elif mode == "s":
				self._Notes[0] = self._Notes[new_id]
				self._Notes[0].set_id(0)

				self._Notes[new_id] = self._Notes[note_id]
				self._Notes[new_id].set_id(new_id)
				
				self._Notes[note_id] = self._Notes[0]
				self._Notes[note_id].set_id(note_id)

				del self._Notes[0]

				Status.push_message(f"Note #{note_id} and #{new_id} swiped.")

		else:
			self._Notes[new_id] = self._Notes[note_id]
			self._Notes[new_id].set_id(new_id)
			del self._Notes[note_id]
			if note_id: Status.push_message(f"Note #{note_id} changed ID to #{new_id}.")

		return Status

	def create(self) -> ExecutionStatus:
		"""Создаёт таблицу."""

		Status = ExecutionStatus()

		try:

			if not os.path.exists(self._Path):
				os.makedirs(self._Path)

			else:
				Status.push_error(Errors.Driver.TABLE_ALREADY_EXISTS)
				return Status

			self._Manifest = self._GetEmptyManifest(self._Path)
			self._Manifest.suppress_saving(False)
			self._Manifest.save()

			self._PostCreateMethod()
			Status.value = self

		except: Status.push_message(Errors.UNKNOWN)

		return Status

	def create_note(self) -> ExecutionStatus:
		"""Создаёт запись."""

		Status = ExecutionStatus()

		try:
			ID = self._GenerateNewID(self._Notes.keys())
			BaseNoteStruct = self._Note.BASE_NOTE.copy()
			if self.manifest.common.is_attachments_enabled: BaseNoteStruct["attachments"] = {"slots": {}, "other": []}
			WriteJSON(f"{self._Path}/{ID}.json", BaseNoteStruct)
			self._ReadNote(ID)
			Status.value = self.get_note(ID).value
			Status.push_message(f"Note #{ID} created.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def delete(self) -> ExecutionStatus:
		"""Удаляет таблицу."""

		Status = ExecutionStatus()

		try: shutil.rmtree(self._Path)
		except FileNotFoundError: Status.push_error(Errors.Driver.PATH_NOT_FOUND)

		return Status

	def delete_note(self, note_id: int) -> ExecutionStatus:
		"""
		Удаляет запись из таблицы. 
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus()

		try:
			note_id = int(note_id)
			del self._Notes[note_id]
			os.remove(f"{self._Path}/{note_id}.json")
			Status.emit_close()
			Status.push_message(f"Note #{note_id} deleted.")

		except KeyError: Status.push_error(Errors.Table.NO_NOTE)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def edit_column_status(self, column: str, status: bool) -> ExecutionStatus:
		"""
		Переключает отображение колонки при просмотре списка записей.
			column – название колонки в любом регистре;\n
			status – статус отображения.
		"""

		Status = ExecutionStatus()
		Columns = self._Manifest.viewer.columns

		if Columns.is_available:
			
			if Columns.check_column(column):
				Columns.edit_column_status(column, status)
				Status.push_message("Column status changed.")

			else:
				ColumnBold = FastStyler(column).decorate.bold
				Status.push_error(f"Option for {ColumnBold} not available or column missing.")

		else: Status.push_message("Colums options not available for this table.")

		return Status

	def get_note(self, note_id: int) -> ExecutionStatus:
		"""
		Возвращает запись.
			note_id – идентификатор записи.
		"""

		Status = ExecutionStatus()

		try:
			note_id = int(note_id)
			if note_id in self._Notes.keys(): Status.value = self._Notes[note_id]
			else: Status.push_error(Errors.Table.NO_NOTE)

		except ValueError: Status.push_error(Errors.Table.INCORRECT_NOTE_ID)
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def open(self) -> ExecutionStatus:
		"""Загружает данные таблицы."""

		Status = ExecutionStatus()

		try:
			self._Manifest = Manifest(self._Path).load()
			ListID = self._GetNotesID()
			for ID in ListID: self._ReadNote(ID)
			AttachmentsDirectory = f"{self._Path}/.attachments"
			if not os.path.exists(AttachmentsDirectory) and self._Manifest.common.is_attachments_enabled: os.makedirs(AttachmentsDirectory)
			if os.path.exists(AttachmentsDirectory) and not os.listdir(AttachmentsDirectory): os.rmdir(AttachmentsDirectory)
			self._PostOpenMethod()
			Status.value = self

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		Status = ExecutionStatus()

		try:
			OldPath = self._Path
			NewPath = self._Path.split("/")
			NewPath[-1] = name
			NewPath =  "/".join(NewPath)
			os.rename(OldPath, NewPath)
			self._Path = NewPath
			self._Name = name
			Status.push_message("Table renamed.")

		except: Status.push_error(Errors.UNKNOWN)

		return Status
	
class Module(Table):
	"""Базовый модуль."""

	#==========================================================================================#
	# >>>>> СТАТИЧЕСКИЕ АТРИБУТЫ <<<<< #
	#==========================================================================================#

	TYPE: str = "module"

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def interfaces(self) -> SupportedInterfaces:
		"""Поддерживаемые интерфейсы."""

		return self._Interfaces

	@property
	def table(self) -> Table:
		"""Таблица, к которой привязан модуль."""

		return self._Table
	
	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ReadNote(self, note_id: int):
		"""
		Считывает содержимое записи.
			note_id – идентификатор записи.
		"""

		self._Notes[note_id] = self._Note(self, note_id)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyManifest(self, path: PathLike) -> Manifest:
		"""
		Возвращает пустой манифест. Переопределите для настройки.

		:param path: Путь к каталогу таблицы.
		:type path: PathLike
		:return: Пустой манифест.
		:rtype: Manifest
		"""

		Buffer = super()._GetEmptyManifest(path)
		Buffer.set_object("module")

		return Buffer

	def _PostCreateMethod(self):
		"""Метод, выполняющийся после создания таблицы."""

		pass

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

		self._Note = Note

	def _PostOpenMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	def _SpecifyInterfaces(self) -> SupportedInterfaces:
		"""
		Определяет объекты с реализацией интерфейсов.

		:return: Контейнер поддерживаемых интерфейсов.
		:rtype: SupportedInterfaces
		"""

		self._Interfaces[Interfaces.CLI] = ModuleCLI

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, session: "Session", storage: PathLike, table: Table, name: str):
		"""
		Базовый модуль.

		:param session: Сессия.
		:type session: Session
		:param storage: Путь к каталогу модуля.
		:type storage: PathLike
		:param table: Таблица, к которой привязан модуль.
		:type table: Table
		:param name: Название модуля.
		:type name: str
		"""
		
		self._Session = session
		self._StorageDirectory = NormalizePath(storage)
		self._Table = table
		self._Name = name

		self._Path = f"{self._StorageDirectory}/{table.name}/{name}"
		self._Notes = dict()
		self._Manifest = None
		self._Binder = Binder(self._Session.driver, self._Table, self)
		self._Interfaces = SupportedInterfaces()
		self._IsModule = True
		self._Note = None

		self._PostInitMethod()
		self._SpecifyInterfaces()

	def get_interface(self, interface: Interfaces) -> "ModuleCLI":
		"""
		Инициализирует интерпретатор интерфейса.

		:param interface: Тип интерфейса.
		:type interface: Interfaces
		:return: Интерпретатор интерфейса.
		:rtype: ModuleCLI
		"""

		return self.interfaces[interface](self._Table, self)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ РЕДАКТИРОВАНИЯ <<<<< #
	#==========================================================================================#

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		OldName = self._Name
		Status = super().rename(name)
		if not Status.has_errors: self._Binder.general.fix_bindings_by_module_name(OldName, self._Name, save = True)

		return Status