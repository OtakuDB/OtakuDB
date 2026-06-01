from .Attachments import Attachments
from .Metainfo import Metainfo
from .Binds import Binds

from dublib.Methods.Filesystem import ReadJSON, WriteJSON
from dublib.Methods.Data import Copy

from typing import Any, TYPE_CHECKING
from pathlib import Path
import os

if TYPE_CHECKING:
	from Source.Core.Session.Driver import Driver
	from Source.Core.Base.Table import BaseTable

class BaseNote:
	"""Базовая запись."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def attachments(self) -> Attachments:
		"""Оператор вложений."""

		return self._Attachments

	@property
	def binds(self) -> Binds:
		"""Связи записей."""

		return self._Binds

	@property
	def id(self) -> int:
		"""ID записи."""

		return self._ID

	@property
	def metainfo(self) -> Metainfo:
		"""Оператор метаданных."""

		return self._Metainfo

	@property
	def name(self) -> str | None:
		"""Название записи."""

		return self._Data.get("name")
	
	@property
	def searchable_strings(self) -> list[str]:
		"""Список строк, которые индексируются для поисковых запросов."""

		return self._GetSearchableStrings()

	@property
	def table(self) -> "BaseTable":
		"""Таблица, к которой относится запись."""

		return self._Table

	#==========================================================================================#
	# >>>>> НАСЛЕДУЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _LoadData(self):
		"""Считывает данные записи или создаёт локальный файл при отсутствии такового."""

		NoteFullPath = self.get_path()
		self._Data = {
			"name": None,
			"metainfo": dict(),
			"binds": dict(),
			"attachments": dict().fromkeys(self._Table.manifest.attachments.slots.keys(), None)
		} | self._GetEmptyNote()

		if NoteFullPath.exists():
			self._Data = self._Data | ReadJSON(NoteFullPath)
			self._ParseContainers()

		else:
			self._ParseContainers()
			self.save(use_presaver = False)

	def _ParseContainers(self):
		"""Парсит контейнерные типы данных."""

		self._Metainfo = Metainfo(self, self._Data.get("metainfo") or dict())
		self._Attachments = Attachments(self, self._Data.get("attachments") or dict())
		self._Binds = Binds(self, self._Data.get("binds") or dict())

	def _RunPostSaveCallbacksForBinds(self):
		"""Запускает обработку изменений в записях, привязавших текущую запись."""

		Masters = tuple(CurrentNote for CurrentNote in self._Table.notes if self._ID in CurrentNote.binds.local.notes_id)
		for MasterNote in Masters: MasterNote.run_local_bind_callback(self)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _AfterLocalBindSavingCallback(self, note: "BaseNote"):
		"""
		Вызывается после выполнения привязанной записью операции сохранения.

		:param note: Привязанная запись.
		:type note: BaseNote
		"""

		pass

	def _GetEmptyNote(self) -> dict[str, Any]:
		"""
		Возвращает пустую структуру записи.

		Поля _name_, _metainfo_, _binds_, _attachments_ будут добавлены автоматически, но их можно указать для определения порядка.

		:return: Пустая структура записи.
		:rtype: dict[str, Any]
		"""

		return dict()

	def _GetSearchableStrings(self) -> list[str]:
		"""
		Список индексируемых для поисковых запросов строк.

		:return: Список строк, которые индексируются для поисковых запросов.
		:rtype: list[str]
		"""

		Strings = list()

		if self.name: Strings.append(self.name)

		for Key in ("localized_name", "another_name", "another_names"):
			NameObject = self._Data.get(Key)
			if type(NameObject) == list: Strings += NameObject
			elif NameObject: Strings.append(NameObject)

		return Strings

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		pass

	def _PostLocalBindMethod(self, note: "BaseNote"):
		"""
		Метод, выполняющийся после привязки локальной записи.

		:param note: Привязанная запись.
		:type note: BaseNote
		"""

		pass

	def _PreSaveMethod(self):
		"""Метод, выполняющийся перед сохранением записи."""

		pass

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, driver: "Driver", table: "BaseTable", note_id: int):
		"""
		Базовая запись.

		:param table: Таблица.
		:type table: BaseTable
		:param note_id: ID записи.
		:type note_id: int
		:raises ValueError: Обязательный ключ отсутствует в файле записи.
		"""

		self._Driver = driver
		self._Table = table
		self._ID = note_id
		
		self._LoadData()
		self._ParseContainers()
		self._PostInitMethod()

	def delete(self):
		"""Удаляет запись."""

		self._Table.delete_note(self._ID)

	def get_path(self, full: bool = True) -> Path:
		"""
		Возвращает путь к записи.

		:param full: Указывает, требуется полный или виртуальный путь.
		:type full: bool
		:return: Путь к записи.
		:rtype: Path
		"""

		ResultPath = self._Table.path / f"{self._ID}.json"
		if full: ResultPath = self._Driver.storage_directory / ResultPath 

		return ResultPath

	def rename(self, name: str | None):
		"""
		Задаёт имя записи.

		:param name: Новое имя записи.
		:type name: str | None
		"""

		if type(name) == str: name = name.strip()
		self._Data["name"] = name
		self.save()

	def run_local_bind_callback(self, note: "BaseNote"):
		"""
		Запускает обработчик обновления связанной записи.

		:param note: Связанная запись, выполнившая операцию сохранения.
		:type note: BaseNote
		"""

		self._AfterLocalBindSavingCallback(note)

	def set_id(self, id: int):
		"""
		Задаёт новый ID и переименовывает файл записи.

		:param id: Новый ID записи.
		:type id: int
		"""

		OldPath = self.get_path()
		NewPath = OldPath.parent / f"{id}.json"
		os.rename(OldPath, NewPath)
		self._Attachments.move(id)
		self._ID = id

	def save(self, use_presaver: bool = True):
		"""
		Сохраняет данные записи в локальный файл JSON.

		:param use_presaver: Указывает, нужно ли вызывать переопределяемый метод, выполняющийся перед сохранением.
		:type use_presaver: bool
		"""

		WriteJSON(self.get_path(), self.to_dict(use_presaver, copy = False), atomic = True)
		self._RunPostSaveCallbacksForBinds()

	def to_dict(self, use_presaver: bool = True, copy: bool = True) -> dict:
		"""
		Возвращает словарное представление записи.

		:param use_presaver: Указывает, нужно ли вызывать переопределяемый метод, выполняющийся перед сохранением.
		:type use_presaver: bool
		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:return: Словарное представление записи.
		:rtype: dict
		"""

		if use_presaver: self._PreSaveMethod()
		self._Data["metainfo"] = self._Metainfo.to_dict(copy)
		self._Data["attachments"] = self._Attachments.to_dict(copy)
		self._Data["binds"] = self._Binds.to_dict(copy)

		return Copy(self._Data) if copy else self._Data