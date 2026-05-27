from .Attachments import Attachments
from .Metainfo import Metainfo

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from typing import Any, TYPE_CHECKING
import shutil
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
	# >>>>> ЗАЩИЩЁННЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _LoadData(self):
		"""Считывает данные записи или создаёт файл при отсутствии такового."""

		if self._Path.exists():
			self._Data = self._Data | ReadJSON(self._Path)
			self._Metainfo = Metainfo(self, self._Data.get("metainfo") or dict())
			self._Attachments = Attachments(self._Path.parent, self, self._Data.get("attachments") or dict())

		else: self.save(use_presaver = False)

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#	

	def _GetEmptyNote(self) -> dict[str, Any]:
		"""
		Возвращает пустую структуру записи.

		Поля _name_, _metainfo_, _attachments_ будут добавлены автоматически, но их можно указать для определения порядка.

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

		self._Path = self._Driver.storage_directory / self._Table.path / f"{note_id}.json"
		
		self._Data = {
			"name": None,
			"metainfo": dict(),
			"attachments": dict().fromkeys(self._Table.manifest.attachments.slots.keys(), None)
		} | self._GetEmptyNote()
		self._Metainfo = Metainfo(self, self._Data["metainfo"])
		self._Attachments = Attachments(self._Path.parent, self, self._Data["attachments"])
		
		self._LoadData()
		self._PostInitMethod()

	def delete(self):
		"""Удаляет запись."""

		self._Table.delete_note(self._ID)

	def rename(self, name: str | None):
		"""
		Задаёт имя записи.

		:param name: Новое имя записи.
		:type name: str | None
		"""

		if type(name) == str: name = name.strip()
		self._Data["name"] = name
		self.save()

	def set_id(self, id: int):
		"""
		Задаёт новый ID и переименовывает файл записи.

		:param id: Новый ID записи.
		:type id: int
		"""
		
		OldID = self._ID
		OldPath = self._Path
		NewPath = self._Path.parent / f"{id}.json"
		os.rename(self._Path, NewPath)
		self._ID = id
		self._Path = NewPath

		if self.attachments.count > 0:
			OldPath = OldPath.parent / f".attachments/{OldID}"
			NewPath =  OldPath.parent / f".attachments/{self._ID}"
			shutil.move(OldPath, NewPath)

	def save(self, use_presaver: bool = True):
		"""
		Сохраняет данные записи в локальный файл JSON.

		:param use_presaver: Указывает, нужно ли вызывать переопределяемый метод, выполняющийся перед сохранением.
		:type use_presaver: bool, optional
		"""

		if use_presaver: self._PreSaveMethod()
		self._Data["metainfo"] = self._Metainfo.to_dict()
		self._Data["attachments"] = self._Attachments.to_dict()
		WriteJSON(self._Path, self._Data, atomic = True)