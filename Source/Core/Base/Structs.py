from Source.Core.Exceptions import *

from dublib.Methods.Filesystem import NormalizePath

from typing import Any, TYPE_CHECKING
import enum
import os

if TYPE_CHECKING:
	from Source.Core.Base import Manifest

#==========================================================================================#
# >>>>> ПЕРЕЧИСЛЕНИЯ <<<<< #
#==========================================================================================#

class Interfaces(enum.Enum):
	CLI = "cli"
	API = "api"
	WEB = "web"

class ObjectsTypes(enum.Enum):
	Table = "table"
	Module = "module"
	Note = "note"
	Extension = "extension"

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class SupportedInterfaces:
	"""Поддерживаемые объектом интерфейсы."""

	def __init__(self):
		"""Поддерживаемые объектом интерфейсы."""

		self.__Interfaces = dict()

		for Element in tuple(Element for Element in Interfaces): self.__Interfaces[Element] = None

	def __setitem__(self, interface: Interfaces, interpreter: Any):
		"""
		Выбирает класс с реализацией интерфейса для объекта.

		:param interface: Тип интерфейса.
		:type interface: Interfaces
		:param interpreter: Класс реализации интерфейса или `None` для отключения.
		:type interpreter: Any
		:raise KeyError: Выбрасывается в случае указания неизвестного интерфейса.
		"""
		
		if interface not in self.__Interfaces: raise KeyError(f"Unknown interface \"{interface}\".")
		self.__Interfaces[interface] = interpreter

	def __getitem__(self, interface: Interfaces) -> Any:
		"""
		Возвращает интерпретатор интерфейса. 

		:param interface: Тип интерфейса.
		:type interface: Interfaces
		:return: Класс реализации интерфейса или `None`, если таковой недоступен.
		:rtype: Any
		:raise KeyError: Выбрасывается в случае указания неизвестного интерфейса.
		"""

		return self.__Interfaces[interface]

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