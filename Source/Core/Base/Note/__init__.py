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

		if self._Path.exists(): self._Data = ReadJSON(self._Path)
		else: self.save()

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

		return {
			"name": None,
			"metainfo": dict(),
			"attachments": dict().fromkeys(self._Table.manifest.attachments.slots.keys(), None)
		}

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
			else: Strings.append(NameObject)

		return Strings

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации класса."""

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
		
		self._Data = self._GetEmptyNote()
		self._LoadData()

		for Key in ("name",):
			if Key not in self._Data: raise ValueError(f"Important key \"{Key}\" missing in note.")

		self._Attachments = Attachments(self._Path.parent, self, self._Data.get("attachments") or dict())
		self._Metainfo = Metainfo(self, self._Data.get("metainfo") or dict())
		
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

	def save(self):
		"""Сохраняет запись атомарно."""

		WriteJSON(self._Path, self._Data, atomic = True)