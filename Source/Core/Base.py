from Source.Core.Bus import ExecutionStatus
from Source.CLI.Templates import Columns
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.CLI.Terminalyzer import ParametersTypes, Command, ParsedCommandData
from dublib.Methods.Filesystem import NormalizePath, ReadJSON, WriteJSON
from dublib.CLI.TextStyler import Codes, FastStyler, TextStyler
from dublib.CLI.Templates import Confirmation
from dublib.Methods.System import Clear

from typing import Any, Literal, TYPE_CHECKING
from os import PathLike
import shutil
import os

if TYPE_CHECKING:
	from Source.Core.Driver import Driver

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class ModuleData:
	"""Данные модуля."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_active(self) -> bool:
		"""Состояние: активирован ли модуль."""

		return os.path.exists(f"{self.__Manifest.path}/{self.name}")

	@property
	def name(self) -> str:
		"""Название модуля."""

		return self.__Name

	@property
	def type(self) -> str:
		"""Тип модуля."""

		return self.__Type

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest", name: str, type: str):
		"""
		Данные модуля.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		:param name: Название модуля.
		:type name: str
		:param type: Тип модуля.
		:type type: str
		"""

		self.__Manifest = manifest
		self.__Name = name
		self.__Type = type

class Attachments:
	"""Вложения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def count(self) -> int:
		"""Количество вложений."""

		Count = 0
		if os.path.exists(self.__Path): Count = len(os.listdir(self.__Path))

		return Count

	@property
	def dictionary(self) -> dict:
		"""Словарное представление вложений."""

		Dictionary = {"slots": self.__Slots, "other": self.__Other}
		if self.__Slots == None: del Dictionary["slots"]
		if self.__Other == None: del Dictionary["other"]

		return Dictionary

	@property
	def other(self) -> list[str] | None:
		"""Список других вложений."""

		return self.__Other

	@property
	def slots(self) -> list[str] | None:
		"""Список слотов."""

		Slots = self.__Slots.keys() if self.__Slots != None else None

		return Slots

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __CheckDirectoryForEmpty(self):
		"""Проверяет, пустая ли директория, и удаляет её в случае истинности."""

		if not os.listdir(self.__Path): os.rmdir(self.__Path)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str, data: dict):
		"""
		Вложения.
			path – путь к каталогу вложений записи;\n
			data – словарь вложений.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Path = path
		self.__Slots: dict[str, str] = data["slots"] if "slots" in data.keys() else None
		self.__Other = data["other"] if "other" in data.keys() else None

	def attach(self, path: str, force: bool = False):
		"""
		Прикрепляет файл к записи.
			force – включает перезапись существующего файла.
		"""

		if self.__Other == None: raise AttachmentsDenied(slot = False)
		path = NormalizePath(path)
		Filename = path.split("/")[-1]
		TargetPath = f"{self.__Path}/{Filename}"
		IsFileExists = os.path.exists(TargetPath)
		if IsFileExists and force: os.remove(TargetPath)
		elif IsFileExists: raise FileExistsError(TargetPath)
		self.__Other.append(Filename)
		os.replace(path, TargetPath)

	def attach_to_slot(self, path: str, slot: str, force: bool = False):
		"""
		Помещает файл в слот.
			slot – слот;\n
			force – включает перезапись существующего файла.
		"""

		if self.__Slots == None: raise AttachmentsDenied(slot = True)
		path = NormalizePath(path)
		Filename = path.split("/")[-1]
		TargetPath = f"{self.__Path}/{Filename}"
		IsFileExists = os.path.exists(TargetPath)
		if IsFileExists and force: os.remove(TargetPath)
		elif IsFileExists: raise FileExistsError(TargetPath)
		os.replace(path, f"{self.__Path}/{Filename}")
		self.__Slots[slot] = Filename

	def clear_slot(self, slot: str):
		"""
		Очищает слот.
			slot – слот.
		"""

		if self.check_slot_occupation(slot):
			os.remove(f"{self.__Path}/{self.__Slots[slot]}")
			self.__Slots[slot] = None
			self.__CheckDirectoryForEmpty()

	def check_slot_occupation(self, slot: str) -> bool:
		"""
		Проверяет, занят ли слот файлом.
			slot – слот.
		"""

		if slot in self.__Slots.keys() and self.__Slots[slot]: return True

		return False

	def get_slot_filename(self, slot: str) -> str:
		"""
		Возвращает название файла в слоте.
			slot – слот.
		"""

		return self.__Slots[slot]

	def unattach(self, filename: str):
		"""
		Удаляет вложение.
			filename – имя файла.
		"""

		os.remove(f"{self.__Path}/{filename}")
		self.__Other.remove(filename)
		self.__CheckDirectoryForEmpty()

#==========================================================================================#
# >>>>> МЕНЕДЖЕР СВЯЗЕЙ <<<<< #
#==========================================================================================#

class IntermoduleBinds:
	"""Межмодульные связи записей."""

	def __init__(self, table: "Table", module: "Module", driver: "Driver"):
		"""
		Межмодульные связи записей.
			table – родительская таблица;\n
			module – текущий модуль;\n
			driver – драйвер таблиц.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table
		self.__Module = module
		self.__Driver = driver

		self.__Path = f"{self.__Table.path}/general-binds.json"
		self.__Data: dict[str, list[str]] = dict()

		if os.path.exists(self.__Path): self.__Data = ReadJSON(self.__Path)

	def bind_note(self, parent_note_id: int, child_note_identificator: str) -> ExecutionStatus:
		"""
		Привязывает к родительской записи дочернюю.
			parent_note_id – ID записи, к которой выполняется привязка;\n
			child_note_identificator – идентификатор записи в другом модуле.
		"""

		ChildModuleName, ChildNoteID = child_note_identificator.split("-")
		ChildNoteID = int(ChildNoteID)
		Status = self.__Driver.load_module(self.__Table, ChildModuleName)
		ParentNoteIdentificator = f"{self.__Module.name}-{parent_note_id}"
		TargetModule: Module = None

		if Status: TargetModule = Status.value
		else: return Status

		if ChildNoteID not in TargetModule.notes_id:
			Status.push_error(Errors.Module.NO_NOTE)
			return Status

		Binds = list(self.get_binded_notes_identificators(parent_note_id))
		Binds.append(child_note_identificator)
		Binds = tuple(set(Binds))
		self.__Data[ParentNoteIdentificator] = Binds
		self.save()

		return Status

	def fix_bindings_by_note_id(self, note_id: int, new_note_id: int, save: bool = False):
		"""
		Заменяет все вхождения ID записи на новый ID.
			note_id – текущий ID записи;\n
			new_note_id – новый ID записи;\n
			save – выполнить автоматическое сохранение (может привести к ошибке записи JSON, если не все изменения внесены в связи).
		"""

		Data = self.__Data.copy()
		OldNoteIdentificator = f"{self.__Module.name}-{note_id}"
		NewNoteIdentificator = f"{self.__Module.name}-{new_note_id}"

		for Identificator in Data.keys():
			if OldNoteIdentificator == Identificator:
				self.__Data[NewNoteIdentificator] = self.__Data[Identificator]
				del self.__Data[Identificator]

		Data = self.__Data.copy()

		for Identificator in Data.keys():
			if OldNoteIdentificator in self.__Data[Identificator]: self.__Data[Identificator] = [NewNoteIdentificator if ID == OldNoteIdentificator else ID for ID in self.__Data[Identificator]]

		if save: self.save()

	def fix_bindings_by_module_name(self, old_name: str, name: str, save: bool = False):
		"""
		Заменяет все вхождения названия модуля на новое.
			old_name – прежнее название модуля;\n
			name – новое название модуля;\n
			save – выполнить автоматическое сохранение (может привести к ошибке записи JSON, если не все изменения внесены в связи).
		"""

		Data = self.__Data.copy()

		for Identificator in Data.keys():
			if Identificator.startswith(f"{old_name}-"):
				NoteID = Identificator.split("-")[-1]
				NewIdentificator = f"{name}-{NoteID}"
				self.__Data[NewIdentificator] = self.__Data[Identificator]
				del self.__Data[Identificator]
				
		Data = self.__Data.copy()

		for Identificator in Data.keys():
			Buffer = list(Data[Identificator])

			for NoteIdentificator in Data[Identificator]:
				if NoteIdentificator.startswith(f"{old_name}-"):
					NoteID = NoteIdentificator.split("-")[-1]
					Buffer.remove(NoteIdentificator)
					Buffer.append(f"{name}-{NoteID}")

			self.__Data[Identificator] = tuple(sorted(Buffer))

		if save: self.save()

	def get_binded_notes(self, note_id: int) -> tuple["Note"]:
		"""
		Возвращает объекты привязанных записей.
			note_id – ID записи, для которой запрашиваются связанные объекты.
		"""

		Binds = self.get_binded_notes_identificators(note_id)
		Notes = list()
		
		for Bind in Binds:
			ModuleName = Bind.split("-")[0]
			NoteID = Bind.split("-")[-1]
			TargetModule: Module = self.__Driver.load_module(self.__Table, ModuleName).value
			Notes.append(TargetModule.get_note(int(NoteID)).value)

		return tuple(Notes)

	def get_binded_notes_identificators(self, note_id: int) -> tuple[int]:
		"""
		Возвращает последовательность ID привязанных записей.
			note_id – ID записи, для которой запрашиваются связи.
		"""

		Binds = tuple()
		NoteIdentificator = f"{self.__Module.name}-{note_id}"

		for ParentNoteIdentificator in self.__Data.keys():

			if ParentNoteIdentificator == NoteIdentificator:
				Binds = tuple(self.__Data[ParentNoteIdentificator])
				break

		if Binds: Binds = tuple(sorted(Binds))

		return Binds
	
	def remove_binding(self, parent_note_id: int, child_note_identificator: str):
		"""
		Удаляет привязку дочерней записи.
			parent_note_id – ID записи, у которой удаляется привязка;\n
			child_note_identificator – идентификатор записи в другом модуле.
		"""

		ChildModuleName, ChildNoteID = child_note_identificator.split("-")
		ChildNoteID = int(ChildNoteID)
		ParentNoteIdentificator = f"{self.__Module.name}-{parent_note_id}"

		Binds = list(self.get_binded_notes_identificators(parent_note_id))
		try: Binds.remove(child_note_identificator)
		except ValueError: pass
		if Binds: self.__Data[ParentNoteIdentificator] = Binds
		else: del self.__Data[ParentNoteIdentificator]
		self.save()

	def save(self):
		"""Сохраняет табличные связи в JSON."""

		if not self.__Data and os.path.exists(self.__Path): os.remove(self.__Path)
		else: WriteJSON(self.__Path, self.__Data)

class TableBinds:
	"""Внутритабличные связи записей."""

	def __init__(self, table: "Table | Module"):
		"""
		Внутритабличные связи записей.
			table – родительская таблица.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table

		self.__Path = f"{self.__Table.path}/binds.json"
		self.__Data: dict[str, list[int]] = dict()

		if os.path.exists(self.__Path): self.__Data = ReadJSON(self.__Path)

	def bind_note(self, parent_note_id: int, child_note_id: int) -> ExecutionStatus:
		"""
		Привязывает к родительской записи дочернюю.
			parent_note_id – ID записи, к которой выполняется привязка;\n
			child_note_id – ID записи, которую привязывают.
		"""

		Status = ExecutionStatus()

		if child_note_id not in self.__Table.notes_id:
			Status.push_error(Errors.Table.NO_NOTE)
			return Status

		Binds = list(self.get_binded_notes_id(parent_note_id))
		Binds.append(child_note_id)
		Binds = tuple(set(Binds))
		self.__Data[str(parent_note_id)] = Binds
		self.save()

		return Status

	def fix_bindings(self, note_id: int, new_note_id: int, save: bool = False):
		"""
		Заменяет все вхождения ID записи на новый ID.
			note_id – текущий ID записи;\n
			new_note_id – новый ID записи;\n
			save – выполнить автоматическое сохранение (может привести к ошибке записи JSON, если не все изменения внесены в связи).
		"""

		Data = self.__Data.copy()

		for NoteID in Data.keys():
			if str(note_id) == NoteID:
				self.__Data[str(new_note_id)] = self.__Data[NoteID]
				del self.__Data[NoteID]

		Data = self.__Data.copy()

		for NoteID in Data.keys():
			if note_id in self.__Data[NoteID]: self.__Data[NoteID] = [new_note_id if ID == note_id else ID for ID in self.__Data[NoteID]]

		if save: self.save()

	def get_binded_notes(self, note_id: int) -> tuple["Note"]:
		"""
		Возвращает объекты привязанных записей.
			note_id – ID записи, для которой запрашиваются связанные объекты.
		"""

		Binds = self.get_binded_notes_id(note_id)
		BindsObjects = list()
		
		for NoteID in Binds: BindsObjects.append(self.__Table.get_note(NoteID).value)

		return tuple(BindsObjects)

	def get_binded_notes_id(self, note_id: int) -> tuple[int]:
		"""
		Возвращает последовательность ID привязанных записей.
			note_id – ID записи, для которой запрашиваются связи.
		"""

		Binds = tuple()

		for ParentNoteID in self.__Data.keys():

			if int(ParentNoteID) == note_id:
				Binds = tuple(self.__Data[ParentNoteID])
				break

		if Binds: Binds = tuple(sorted(Binds))

		return Binds
	
	def remove_binding(self, parent_note_id: int, child_note_id: int):
		"""
		Удаляет привязку дочерней записи.
			parent_note_id – ID записи, у которой удаляется привязка;\n
			child_note_id – ID записи, привязку которой удаляют.
		"""

		Binds = list(self.get_binded_notes_id(parent_note_id))
		try: Binds.remove(child_note_id)
		except ValueError: pass
		if Binds: self.__Data[str(parent_note_id)] = Binds
		else: del self.__Data[str(parent_note_id)]
		self.save()

	def save(self):
		"""Сохраняет табличные связи в JSON."""

		if not self.__Data and os.path.exists(self.__Path): os.remove(self.__Path)
		else: WriteJSON(self.__Path, self.__Data)

class Binder:
	"""Менеджер связей объектов."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def general(self) -> IntermoduleBinds | None:
		"""Межмодульные связи объектов."""

		return self.__General
	
	@property
	def local(self) -> TableBinds:
		"""Внутритабличные связи записей."""

		return self.__Local

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table", module: "Module | None" = None):
		"""
		Менеджер связей объектов.
			driver – драйвер таблиц;\n
			table – родительская таблица;\n
			module – модуль таблицы.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self.__Table = table
		self.__Module = module
		self.__Driver = driver

		self.__General = IntermoduleBinds(self.__Table, self.__Module, self.__Driver) if module else None
		self.__Local = TableBinds(self.__Table)

#==========================================================================================#
# >>>>> МАНИФЕСТ <<<<< #
#==========================================================================================#

class ColumnsOptions:
	"""Опции отображения колонок таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def important_columns(self) -> tuple[str]:
		"""Список обязательных колонок."""

		return ("ID", "Name")

	@property
	def is_available(self) -> bool:
		"""Указывает, доступны ли настройки отображения колонок таблицы."""

		IsAvailable = False
		if len(list(self.__Data.keys())): IsAvailable = True

		return IsAvailable

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Опции отображения колонок таблицы.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data: dict[str, bool] = dict()
		for Column in self.important_columns: self.__Data[Column] = True

	def __getitem__(self, column: str) -> bool | None:
		"""
		Возвращает статус отображения колонки.

		:param column: Название колонки в любом регистре.
		:type column: Manifest
		"""

		return self.__Data.get(column)

	def check_column(self, column: str) -> bool:
		"""
		Проверяет, описано ли правило для колонки.

		:param column: Название колонки. Проверка нечувствительна к регистру.
		:type column: str
		:return: Состояние присутствия колонки в списке.
		:rtype: bool
		"""

		return column in self.__Data
	
	def edit_column_status(self, column: str, status: bool):
		"""
		Задаёт статус отображения для колонки.

		:param column: Название колонки.
		:type column: str
		:param status: Статус отображения.
		:type status: bool
		:raises KeyError: Выбрасывается при отсутствии колонки.
		"""

		if column not in self.__Data.keys(): raise KeyError(column)
		self.__Data[column] = status
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = data
		for Column in self.important_columns: self.__Data[Column] = True

	def set_columns(self, columns: tuple[str]):
		"""
		Задаёт последовательность колонок.

		:param tuple: Последовательность колонок.
		:type tuple: tuple[str]
		"""

		Buffer: dict[str, bool] = dict()

		for Column in columns:
			Value = self.__getitem__(Column)
			if Value == None: Value = True
			Buffer[Column] = True

		for Column in self.important_columns:
			if Column not in Buffer: Buffer[Column] = True

		self.__Data = Buffer
		self.__Manifest.save()

	def to_dict(self) -> dict:
		"""Возвращает словарь опций отображения."""

		return self.__Data.copy()

class CommonOptions:
	"""Общие опции таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_attachments_enabled(self) -> bool:
		"""Указывает, разрешено ли прикреплять файлы к записям."""

		return self.__Data["attachments"]

	@property
	def recycle_id(self) -> bool:
		"""Указывает, необходимо ли занимать освободившиеся ID."""

		return self.__Data["recycle_id"]

	@property
	def slots(self) -> dict[str, str | None]:
		"""Определения слотов, предназначенных для особого взаимодействия."""

		return self.__Data["slots"].copy()

	#==========================================================================================#
	# >>>>> МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""Общие опции таблицы."""

		self.__Manifest = manifest

		self.__Data = {
			"recycle_id": True,
			"attachments": False,
			"slots": {}
		}

	def switch_recycle_id(self, status: bool):
		"""
		Переключает состояние утилизации свободных ID.

		:param status: Состояние утилизации свободных ID.
		:type status: bool
		"""

		self.__Data["recycle_id"] = status
		self.__Manifest.save()

	def enable_attachments(self, status: bool):
		"""
		Переключает использование вложений.

		:param status: Состояние использования вложений.
		:type status: bool
		"""

		self.__Data["attachments"] = status
		self.__Manifest.save()

	def add_slot(self, slot: str, description: str | None):
		"""
		Резервирует слот вложений для особого взаимодействия.

		:param slot: Название слота.
		:type slot: str
		:param description: Описание слота.
		:type description: str | None
		"""

		self.__Data["slots"][slot] = description
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def remove_slot(self, slot: str):
		"""
		Удаляет слот вложений.

		:param slot: Название слота.
		:type slot: str
		"""

		try: 
			del self.__Data["slots"][slot]
			self.__Manifest.save()
		except KeyError: pass

	def to_dict(self) -> dict[str, bool | dict]:
		"""
		Возвращает словарное представление общих опций.

		:return: Словарное представление общих опций.
		:rtype: dict[str, bool | dict]
		"""

		return self.__Data.copy()

class MetainfoRules:
	"""Правила метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def fields(self) -> tuple[str]:
		"""Список названий полей с правилами."""

		return tuple(self.__Data.keys())
	
	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Правила метаданных.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data = dict()

	def __getitem__(self, key: str) -> list | tuple | None:
		"""
		Возвращает правило.

		:param key: Ключ правила.
		:type key: str
		:return: Правило.
		:rtype: Any
		"""

		return self.__Data[key]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data

	def remove_rule(self, name: str):
		"""
		Удаляет правило проверки поля метаданных.

		:param name: Название поля метаданных.
		:type name: str
		"""

		try: 
			del self.__Data[name]
			self.__Manifest.save()
		except KeyError: pass

	def set_rule(self, name: str, rule: list | tuple | None):
		"""
		Добавляет правило проверки поля метаданных.

		:param name: Название поля метаданных.
		:type name: str
		:param rule: Правило проверки. `None` – любое значение, `list | tuple` – одно и зуказанных значений. 
		:type rule: list | tuple | None
		"""

		self.__Data[name] = rule
		self.__Manifest.save()

class ViewerOptions:
	"""Опции просмоторщика записей."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def autoclear(self) -> bool | None:
		"""Указывает, следует ли очищать консоль перед выводом списков и просмотром содержимого."""

		Option = None
		if "autoclear" in self.__Data.keys(): Option = self.__Data["autoclear"]

		return Option
	
	@property
	def colorize(self) -> bool | None:
		"""Указывает, следует ли окрашивать элементы консольного интерфейса."""

		Option = None
		if "colorize" in self.__Data.keys(): Option = self.__Data["colorize"]

		return Option

	@property
	def columns(self) -> ColumnsOptions:
		"""Опции отображения колонок таблицы."""

		return self.__Columns

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Опции просмоторщика записей.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data = {
			"autoclear": True,
			"colorize": True,
			"columns": {}
		}

		self.__Columns = ColumnsOptions(manifest)
		self.__Columns.parse(self.__Data["columns"])

	def enable_autoclear(self, status: bool):
		"""
		Переключает режим автоочистки консоли перед отображением объектов.

		:param status: Состояние автоочистки.
		:type status: bool
		"""

		self.__Data["autoclear"] = status
		self.__Manifest.save()

	def enable_colorize(self, status: bool):
		"""
		Переключает режим раскраски вывода.

		:param status: Состояние раскраски вывода.
		:type status: bool
		"""

		self.__Data["colorize"] = status
		self.__Manifest.save()

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data
		self.__Columns.parse(self.__Data["columns"])

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление опций.

		:return: Словарное представление опций.
		:rtype: dict
		"""

		Data = self.__Data.copy()
		Data["columns"] = self.__Columns.to_dict()

		return Data

class Manifest:
	"""Манифест таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def common(self) -> CommonOptions:
		"""Общие опции таблиц."""

		return self.__Common

	@property
	def custom(self) -> dict:
		"""Дополнительные опции."""

		return self.__Custom.copy()

	@property
	def metainfo_rules(self) -> MetainfoRules:
		"""Опции метаданных."""

		return self.__MetainfoRules

	@property
	def modules(self) -> tuple[ModuleData]:
		"""Список модулей таблицы."""

		return self.__Modules
	
	@property
	def path(self) -> str:
		"""Путь к директории таблицы."""

		return self.__Path

	@property
	def type(self) -> str:
		"""Тип таблицы."""

		return self.__Type
	
	@property
	def viewer(self) -> ViewerOptions:
		"""Опции просмоторщика записей."""

		return self.__ViewerOptions

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseModules(self, modules_data: list[dict] | None) -> list[ModuleData]:
		"""
		Парсит данные модулей в структуры.

		:param modules_data: Данные модулей.
		:type modules_data: list[dict]
		:return: Структуры данных модулей.
		:rtype: list[ModuleData]
		"""

		if not modules_data: return tuple()

		Modules = list()
		for Module in modules_data: Modules.append(ModuleData(self, Module["name"], Module["type"]))

		return Modules

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, path: str):
		"""
		Манифест таблицы.

		:param path: Путь к директории таблицы.
		:type path: str
		"""

		self.__Path = path

		self.__Object = None
		self.__Type = None
		self.__Common = CommonOptions(self)
		self.__MetainfoRules = MetainfoRules(self)
		self.__ViewerOptions = ViewerOptions(self) 
		self.__Custom = dict()
		self.__Modules = list()

		self.__SuppressSaving = False

	def add_module(self, module: ModuleData):
		"""
		Добавялет данные модуля в манифест.

		:param module: Данные модуля.
		:type module: ModuleData
		"""

		self.__Modules.append(module)
		self.save()

	def load(self):
		"""
		Загружает данные манифеста.
		
		:return: Манифест.
		:rtype: Manifest
		"""

		Data = ReadJSON(f"{self.__Path}/manifest.json")
		self.__Object = Data["object"]
		self.__Type = Data["type"]
		self.__Common.parse(Data.get("common") or dict())
		self.__MetainfoRules.parse(Data.get("metainfo_rules") or dict())
		self.__ViewerOptions.parse(Data.get("viewer") or dict())
		self.__Custom = Data.get("custom") or dict()
		self.__Modules = self.__ParseModules(Data.get("modules") or dict())

		return self

	def save(self) -> ExecutionStatus:
		"""
		Сохраняет манифест.

		:return: Статус выполнения.
		:rtype: ExecutionStatus
		"""

		Status = ExecutionStatus()

		try:
			if not self.__SuppressSaving: WriteJSON(f"{self.__Path}/manifest.json", self.to_dict())
			
		except: Status.push_error(Errors.UNKNOWN)

		return Status

	def suppress_saving(self, status: bool):
		"""
		Переключает подавление сохранения.

		:param status: Статус подавление сохранения.
		:type status: bool
		"""

		self.__SuppressSaving = status

	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление манифеста.

		:return: Словарное представление манифеста.
		:rtype: dict[str, Any]
		"""

		Data = {
			"object": self.__Object,
			"type": self.__Type,
			"common": self.__Common.to_dict(),
			"metainfo_rules": {},
			"viewer": {
				"autoclear": False,
				"colorize": True,
				"columns": {}
			},
			"custom": self.__Custom.copy()
		}

		ModulesBuffer = list()
		for Module in self.__Modules: ModulesBuffer.append({"name": Module.name, "type": Module.type, "is_active": Module.is_active})
		if ModulesBuffer: Data["modules"] = tuple(ModulesBuffer)

		return Data

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ ЗАПОЛНЕНИЯ МАНИФЕСТА <<<<< #
	#==========================================================================================#

	def set_object(self, object: Literal["module", "table"]):
		"""
		Задаёт тип объекта.

		:param type: Тип описываемого манифестом объекта.
		:type type: Literal["module", "table"]
		"""

		if object not in ("module", "table"): raise ValueError(f"Incorrect object: \"{object}\".")
		self.__Object = object

	def set_type(self, type: str):
		"""
		Задаёт название типа таблицы.

		:param type: Название типа таблицы. Для модуля используется шаблон `{TABLE}:{MODULE}`.
		:type type: str
		"""

		self.__Type = type

#==========================================================================================#
# >>>>> CLI <<<<< #
#==========================================================================================#

class NoteCLI:
	"""CLI записи."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()

		Com = Command("attach", "Attach files to note.")
		ComPos = Com.create_position("FILE", important = True)
		ComPos.add_argument(ParametersTypes.ValidPath, description = "Path to file.")
		Com.base.add_flag("f", "Enable attachments overwrite.")
		Com.base.add_key("slot", ParametersTypes.Text, "Name of slot for attachment.")
		CommandsList.append(Com)

		Com = Command("bind", "Bind another note to this.")
		ComPos = Com.create_position("NOTE", "Target note for binding.", important = True)
		ComPos.add_argument(description = "Note identificator in module-id format.")
		Com.base.add_flag("r", "Remove binding if exists.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete note.")
		Com.base.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("meta", "Manage note metainfo fields.", category = "Metainfo")
		Com.base.add_argument(description = "Field name.", important = True)
		Com.base.add_argument(description = "Field value.")
		ComPos = Com.create_position("OPERATION", "Type of operation with metainfo.", important = True)
		ComPos.add_flag("set", description = "Create new or update exists field.")
		ComPos.add_flag("del", description = "Remove field.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename note.")
		Com.base.add_argument(description = "New name.", important = True)
		CommandsList.append(Com)

		Com = Command("slots", "Print slots info.")
		CommandsList.append(Com)

		Com = Command("unattach", "Unattach files from note.")
		ComPos = Com.create_position("FILE", important = True)
		ComPos.add_argument(description = "Attachment name.")
		ComPos.add_key("slot", ParametersTypes.Text, "Name of attachment slot.")
		CommandsList.append(Com)

		Com = Command("view", "View note in console.")
		CommandsList.append(Com)

		return CommandsList + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		return Status

	def _View(self) -> ExecutionStatus:
		"""Выводит форматированное представление записи."""

		Status = ExecutionStatus()

		try:
			#---> Вывод описания.
			#==========================================================================================#
			if self._Note.name: print(FastStyler(self._Note.name).decorate.bold)

			#---> Вывод связей.
			#==========================================================================================#
			
			if self._Note.binded_notes:
				print(FastStyler(f"BINDED NOTES:").decorate.bold)
				
				for Note in self._Note.binded_notes:
					Name = f". {Note.name}" if Note.name else ""
					print(f"    > {Note.id}{Name}")

			#---> Вывод вложений.
			#==========================================================================================#
			Attachments = self._Note.attachments

			if Attachments.count:
				print(FastStyler("ATTACHMENTS:").decorate.bold)

				if Attachments.slots != None:
					for Slot in Attachments.slots: print(f"    {Slot}: " + FastStyler(Attachments.get_slot_filename(Slot), decorations = Codes.Decorations.Italic))

				if Attachments.other != None:
					for Filename in Attachments.other: print("    " + TextStyler(Filename, decorations = Codes.Decorations.Italic))

			#---> Вывод метаданных.
			#==========================================================================================#

			if self._Note.metainfo:
				print(FastStyler(f"METAINFO:").decorate.bold)
				MetaInfo = self._Note.metainfo
				
				for Key in MetaInfo.keys():
					CustomMetainfoMarker = "" if Key in self._Table.manifest.metainfo_rules.fields else "*"
					print(f"    {CustomMetainfoMarker}{Key}: " + str(MetaInfo[Key]))

		except: Status.push_error(Errors.UNKNOWN)

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table", note: "Note"):
		"""
		CLI записи.
			driver – драйвер таблиц;\n
			table – объектное представление таблицы;\n
			note – объектное представление записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Driver = driver
		self._Table = table
		self._Note = note

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команду.
			command_data – описательная структура команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name == "attach":
			Slot = parsed_command.get_key_value("slot")
			Force = parsed_command.check_flag("f")
			Status = self._Note.attach(parsed_command.arguments[0], Slot, Force)

		elif parsed_command.name == "bind":
			if parsed_command.check_flag("r"): self._Note.remove_note_binding(parsed_command.arguments[0])
			else: self._Note.bind_note(parsed_command.arguments[0])

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation(f"Are you sure to delete #{self._Note.id} note?")
			
			if Response:
				Status = self._Table.delete_note(self._Note.id)
				if Status: Status["interpreter"] = "module" if self._Table.is_module else "table"

		elif parsed_command.name == "meta":
			if parsed_command.check_flag("set"): Status = self._Note.set_metainfo(parsed_command.arguments[0], parsed_command.arguments[1])
			if parsed_command.check_flag("del"): Status = self._Note.remove_metainfo(parsed_command.arguments[0])

		elif parsed_command.name == "rename":
			Status = self._Note.rename(parsed_command.arguments[0])

		elif parsed_command.name == "slots":
			Info = self._Note.slots_info

			if Info:
				TableData = {
					"Slot": list(),
					"Description": list()
				}

				for Slot in Info.keys():
					TableData["Slot"].append(Slot)
					TableData["Description"].append(Info[Slot])

				Columns(TableData, sort_by = "Slot")

			else: print("No slots info.")

		elif parsed_command.name == "unattach":
			Slot = parsed_command.get_key_value("slot")
			Filename = parsed_command.arguments[0] if len(parsed_command.arguments) else None
			Status = self._Note.unattach(Filename, Slot)

		elif parsed_command.name == "view":
			if self._Table.manifest.viewer.autoclear: Clear()
			self._View()

		else:
			Status = self._ExecuteCustomCommands(parsed_command)

		return Status

class BaseTableCLI:
	"""Базовый CLI таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def base_commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = list()
		
		Com = Command("chid", "Change ID of note.")
		ComPos = Com.create_position("NOTE", important = True)
		ComPos.add_argument(ParametersTypes.Number, "Exists note ID.")
		ComPos = Com.create_position("ID", important = True)
		ComPos.add_argument(ParametersTypes.Number, "New note ID")
		ComPos = Com.create_position("MODE", "Mode of ID changing.")
		ComPos.add_flag("o", "Overwtite exists note.")
		ComPos.add_flag("s", "Swipe with exists note.")
		ComPos.add_flag("i", "Insert to exists note place.")
		CommandsList.append(Com)

		Com = Command("columns", "Edit columns showing options.")
		ComPos = Com.create_position("OPERATION", "Type of operation for option. If not specified, prints current options.")
		ComPos.add_key("disable", description = "Hide column in list of notes.")
		ComPos.add_key("enable", description = "Show column in list of notes.")
		CommandsList.append(Com)

		Com = Command("delete", "Delete table.")
		Com.base.add_flag("y", "Automatically confirms deletion.")
		CommandsList.append(Com)

		Com = Command("new", "Create new note.")
		Com.base.add_flag("o", "Open new note.")
		CommandsList.append(Com)

		Com = Command("rename", "Rename current table or module.")
		Com.base.add_argument(description = "New table or module name.", important = True)
		CommandsList.append(Com)

		Com = Command("search", "Search notes by part of name.")
		Com.base.add_argument(description = "Search query.", important = True)
		Com.base.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		Com = Command("view", "Show list of notes.")
		Com.base.add_flag("r", "Reverse list.")
		Com.base.add_key("sort", description = "Set sort by column name.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def base_commands_names(self) -> tuple[str]:
		"""Список названий базовых команд."""

		return tuple(Command.name for Command in self.base_commands)

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _AddRowToTableContent(self, content: dict[str, list], note: "Note") -> dict[str, list]:
		"""
		Добавляет строчку в таблицу и выполняет проверки содержимого.
			content – содержимое таблицы;\n
			row – данные строчки.
		"""

		Row = self._BuildNoteRow(note)

		for Column in content.keys():
			Data = ""
			if Column in Row.keys() and Row[Column] != None: Data = Row[Column]
			if Column == "Name": Data = Data if len(Data) < 60 else Data[:60] + "…"
			content[Column].append(Data)

		return content

	def _ExecuteBaseCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""
		
		Status = ExecutionStatus()

		if parsed_command.name == "chid":
			Mode = None
			if parsed_command.check_flag("i"): Mode = "i"
			elif parsed_command.check_flag("o"): Mode = "o"
			elif parsed_command.check_flag("s"): Mode = "s"
			Status = self._BaseTable.change_note_id(parsed_command.arguments[0], parsed_command.arguments[1], Mode)

		elif parsed_command.name == "columns":
			
			if parsed_command.check_key("disable"):
				ColumnName = parsed_command.get_key_value("disable")
				Status = self._BaseTable.edit_column_status(ColumnName, False)

			elif parsed_command.check_key("enable"):
				ColumnName = parsed_command.get_key_value("enable")
				Status = self._BaseTable.edit_column_status(ColumnName, True)

			else:
				Data = self._BaseTable.manifest.viewer.columns.to_dict()
				TableData = {
						"Column": [],
						"Status": []
					}
				
				for Name in Data.keys():
					ColumnStatus = Data[Name]
					ColumnStatus = FastStyler("enabled").colorize.green if ColumnStatus else FastStyler("disabled").colorize.red
					TableData["Column"].append(Name)
					TableData["Status"].append(ColumnStatus)

				Columns(TableData, sort_by = "Column")

		elif parsed_command.name == "new":
			Status = self._BaseTable.create_note()
			if parsed_command.check_flag("o") and Status: Status.emit_navigate(Status.value.id)

		elif parsed_command.name == "delete":
			Response = parsed_command.check_flag("y")
			if not Response: Response = Confirmation(f"Are you sure to delete \"{self._BaseTable.name}\" table?")
			
			if Response:
				Status = self._BaseTable.delete()

				if not Status.has_errors:
					Status.push_message("Module deleted." if self._Module else "Table deleted.")
					Status.emit_close()

		elif parsed_command.name == "search":
			Status = self._View(parsed_command, parsed_command.arguments[0])
		
		elif parsed_command.name == "view":
			Status = self._View(parsed_command)

		return Status

	def _View(self, parsed_command: ParsedCommandData, search: str | None = None) -> ExecutionStatus:
			"""
			Выводит список записей.
				parsed_command – описательная структура команды;\n
				search – поисковый запрос.
			"""
			
			Status = ExecutionStatus()

			try:
				Content = dict()
				SortBy = parsed_command.check_key("sort") or "ID"
				IsReverse = parsed_command.check_flag("r")
				for Column in self._BaseTable.manifest.viewer.columns.to_dict().keys(): Content[Column] = list()
				Notes: list["Note"] = self._Module.notes if self._Module else self._Table.notes

				if SortBy not in Content.keys():
						Status.push_error("no_column_to_sort")
						return Status

				if not Notes:
					Status.push_message("Table is empty.")
					return Status 
				
				if self._BaseTable.manifest.viewer.autoclear: Clear()
				
				if search:
					print("Search:", FastStyler(search).colorize.yellow)
					Notes = [Note for Note in Notes if any(search.lower() in Variant.lower() for Variant in Note.searchable)]
				
				for Note in Notes: Content = self._AddRowToTableContent(Content, Note)

				if Notes:

					for ColumnName in list(Content.keys()):
						if self._BaseTable.manifest.viewer.columns[ColumnName] == False: del Content[ColumnName]

					Columns(Content, SortBy, IsReverse)

				else: Status.push_message("Notes not found.")

			except: Status.push_error(Errors.UNKNOWN)

			return Status

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _BuildNoteRow(self, note: "Note") -> dict[str, str]:
		"""
		Строит строку описания записи для таблицы и возвращает словарь в формате: название колонки – данные.
			note – обрабатываемая запись.
		"""

		Row = dict()
		Row["ID"] = note.id
		Row["Name"] = note.name

		return Row

	def _GenereateCustomCommands(self) -> list[Command]:
		"""Генерирует дексрипторы дополнительных команд."""

		CommandsList = list()

		# Инициализация команд...

		return CommandsList

	def _ExecuteCustomCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает дополнительные команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "Table", module: "Module | None" = None):
		"""
		Базовый CLI таблицы.
			driver – драйвер таблиц;\n
			table – таблица;\n
			module – модуль.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Driver = driver
		self._Table = table
		self._Module = module

		self._BaseTable = module if module else table

class TableCLI(BaseTableCLI):
	"""CLI таблицы."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def moduled_commands(self) -> list[Command]:
		"""Список дескрипторов команд для таблицы с модулями."""

		CommandsList = list()

		Com = Command("init", "Initialize module.")
		ComPos = Com.create_position("MODULE", "Module name.", important = True)
		ComPos.add_argument()
		Com.base.add_flag("o", "Open initialized module.")
		CommandsList.append(Com)

		Com = Command("list", "List of modules.")
		CommandsList.append(Com)

		return CommandsList

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		CommandsList = self.base_commands + self._GenereateCustomCommands()
		if self._Table.manifest.modules: CommandsList += self.moduled_commands

		return CommandsList

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _ExecuteModuledTableCommands(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды таблицы с модулями.
			parsed_command – описательная структура команды.
		"""
		
		Status = ExecutionStatus()

		if parsed_command.name == "init":
			Modules = self._Table.manifest.modules

			if Modules:
				Type = None

				for Module in Modules:
					if Module.name == parsed_command.arguments[0]: Type = Module.type

				if Type:
					Status.emit_initialize_module(Type)
					if parsed_command.check_flag("o"): Status.emit_navigate(parsed_command.arguments[0])

				else: Status.push_error(Errors.Driver.NO_MODULE_TYPE)

			else: Status.push_error(Errors.Driver.MODULES_NOT_SUPPORTED)

		elif parsed_command.name == "list":
			Modules = self._Table.manifest.modules

			if Modules:
				TableData = {
					"Module": [],
					"Type": [],
					"Status": []
				}

				for Module in Modules:
					ModuleStatus = TextStyler(text_color = Codes.Colors.Green).get_styled_text("active") 
					if not Module.is_active: ModuleStatus = TextStyler(text_color = Codes.Colors.Red).get_styled_text("inactive") 
					TableData["Module"].append(Module.name)
					TableData["Type"].append(FastStyler(Module.type).decorate.italic)
					TableData["Status"].append(ModuleStatus)
				
				Columns(TableData, sort_by = "Module")

			else: Status.push_message("No modules in table.")

		return Status

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name in self.base_commands_names: Status += self._ExecuteBaseCommands(parsed_command)
		elif self._Table.manifest.modules: Status += self._ExecuteModuledTableCommands(parsed_command)
		else: Status += self._ExecuteCustomCommands(parsed_command)

		return Status
	
class ModuleCLI(BaseTableCLI):
	"""CLI модуля."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def commands(self) -> list[Command]:
		"""Список дескрипторов команд."""

		return self.base_commands + self._GenereateCustomCommands()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def execute(self, parsed_command: ParsedCommandData) -> ExecutionStatus:
		"""
		Обрабатывает команды.
			parsed_command – описательная структура команды.
		"""

		Status = ExecutionStatus()

		if parsed_command.name in self.base_commands_names: Status += self._ExecuteBaseCommands(parsed_command)
		else: Status += self._ExecuteCustomCommands(parsed_command)

		return Status

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
	def cli(self) -> NoteCLI:
		"""Класс-обработчик CLI записи."""

		return self._CLI
	
	@property
	def id(self) -> int:
		"""ID записи."""

		return self._ID
	
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

		self._CLI = NoteCLI

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, table: "Table", note_id: int):
		"""
		Базовая запись.
			table – таблица;\n
			note_id – ID записи.
		"""

		#---> Генерация динамичкских атрибутов.
		#==========================================================================================#
		self._Table = table
		self._ID = note_id
		self._Path = self.__GeneratePath(point = f"{note_id}.json")
		self._Data = ReadJSON(self._Path)
		self._CLI = None

		#---> Пост-процессинг.
		#==========================================================================================#
		self._PostInitMethod()

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
	def cli(self) -> TableCLI:
		"""Класс-обработчик CLI таблицы."""

		return self._CLI

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
		self._CLI = TableCLI

	def _PostOpenMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#
	
	def __init__(self, driver: "Driver", storage: PathLike, name: str):
		"""
		Базовая таблица.

		:param driver: Драйвер.
		:type driver: Driver
		:param storage: Путь к каталогу таблицы.
		:type storage: PathLike
		:param name: Название таблицы.
		:type name: str
		"""
		
		self._StorageDirectory = NormalizePath(storage)
		self._Name = name

		self._Path = f"{self._StorageDirectory}/{name}"
		self._Notes: dict[int, Note] = dict()
		self._Manifest = None
		self._Binder = Binder(driver, self)
		self._IsModule = False
		self._Note = None
		self._CLI = None

		self._PostInitMethod()

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
		self._CLI = ModuleCLI

	def _PostOpenMethod(self):
		"""Метод, выполняющийся после чтения данных таблицы."""

		pass

	#==========================================================================================#
	# >>>>> ОБЯЗАТЕЛЬНЫЕ ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", storage: PathLike, table: Table, name: str):
		"""
		Базовый модуль.

		:param driver: Драйвер.
		:type driver: Driver
		:param storage: Путь к каталогу модуля.
		:type storage: PathLike
		:param table: Таблица, к которой привязан модуль.
		:type table: Table
		:param name: Название модуля.
		:type name: str
		"""
		
		self._StorageDirectory = NormalizePath(storage)
		self._Table = table
		self._Name = name

		self._Path = f"{self._StorageDirectory}/{table.name}/{name}"
		self._Notes = dict()
		self._Manifest = None
		self._Binder = Binder(driver, self._Table, self)
		self._IsModule = True
		self._Note = None
		self._CLI = None

		self._PostInitMethod()

	def rename(self, name: str) -> ExecutionStatus:
		"""
		Переименовывает таблицу.
			name – новое название.
		"""

		OldName = self._Name
		Status = super().rename(name)
		if not Status.has_errors: self._Binder.general.fix_bindings_by_module_name(OldName, self._Name, save = True)

		return Status