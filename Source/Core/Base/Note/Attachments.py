from ..Note.Enums import CallbacksTypes

from Source.Core import Exceptions

from dataclasses import dataclass
from typing import TYPE_CHECKING
from pathlib import Path
import shutil
import os

if TYPE_CHECKING:
	from . import BaseNote

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

class Slot:
	"""Слот."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def file(self) -> str | None:
		"""Имя файла."""

		return self.__File
	
	@property
	def full_path(self) -> Path | None:
		"""Полный путь к файлу."""

		if self.__File: return self.__Attachments.directory / self.__File

	@property
	def name(self) -> str:
		"""Имя слота."""

		return self.__Name

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, attachments: "Attachments", name: str, file: str | None):
		"""
		Слот.

		:param attachments: Вложения.
		:type attachments: Attachments
		:param name: Имя слота.
		:type name: str
		:param file: Имя файла в слоте.
		:type file: str | None
		"""

		self.__Attachments = attachments
		self.__Name = name
		self.__File = file

		self.__Note = self.__Attachments.note

	def attach(self, file: Path, copy: bool = False):
		"""
		Помещает файл в слот вложения записи.

		:param file: Путь к файлу.
		:type file: Path
		:param copy: Указывает, нужно ли скопировать файл или переместить. 
		:type copy: bool
		:raises AttachmentSlotAlreadyFilled: Слот уже содержит файл.
		:raises AttachmentsDenied: Вложение запрещено.
		:raises AttachmentSlotNotDescribed: Слот вложения не описан.
		"""
		
		match self.__Note.table.manifest.attachments.rule:
			case 0: raise Exceptions.Note.AttachmentsDenied(False)
		
		if self.__File: raise Exceptions.Note.AttachmentSlotAlreadyFilled(self.__Name)
		self.__File = file.name


		AttachmentDirectory = self.__Note.table.full_path / ".attachments" / str(self.__Note.id)
		os.makedirs(AttachmentDirectory, exist_ok = True)
		AttachmentPath = AttachmentDirectory / file

		if copy: shutil.copy(file, AttachmentPath)
		else: os.replace(file, AttachmentPath)
		
		self.__Note.save()
		self.__Note.run_callback(CallbacksTypes.AttachmentsChanged)

	def clear(self):
		"""Очищает слот."""

		if not self.__File: return

		try: os.remove(self.full_path)
		except FileNotFoundError: pass

		try: 
			AttachmentsDirectory = self.__Note.table.full_path / ".attachments" / str(self.__Note.id)
			AttachmentsDirectory.rmdir()
		except (FileNotFoundError, OSError): pass

		self.__Note.save()
		self.__Note.run_callback(CallbacksTypes.AttachmentsChanged)

	def is_exists(self) -> bool:
		"""
		Проверяет, существует ли файл вложения.

		:return: Возвращает `True`, если указан файл и он существует.
		:rtype: bool
		"""

		FullPath = self.full_path
		if not FullPath: return False

		return FullPath.exists()

@dataclass(frozen = True)
class ValidationError:
	"""Описание ошибки валидации."""

	slot: str | None
	file: str

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Attachments:
	"""Вложения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def directory(self) -> Path:
		"""Путь к директории вложений записи."""

		return self.__Note.table.full_path / ".attachments" / str(self.__Note.id)

	@property
	def count(self) -> int:
		"""Количество вложений."""

		return len(self.__Data["free"]) + sum(1 for slot in self.slots if slot.file)

	@property
	def free(self) -> tuple[str]:
		"""Последовательность имён файлов свободных вложений."""

		return tuple(Value for Value in self.__Data["free"])

	@property
	def note(self) -> "BaseNote":
		"""Запись, к которой относятся вложения."""

		return self.__Note

	@property
	def slots(self) -> tuple[Slot]:
		"""Последовательность данных слотов."""

		return tuple(self.__Slots.values())

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseSlots(self) -> dict[str, Slot]:
		"""
		Парсит данные слотов в объекты.

		:return: Словарь данных слотов.
		:rtype: dict[str, SlotInfo]
		"""

		Slots = dict()
		for Name, File in self.__Data["slots"].items(): Slots[Name] = Slot(self, Name, File)
		
		return Slots

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "BaseNote", data: dict):
		"""
		Оператор вложений.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь данных вложений.
		:type data: dict
		"""

		self.__Note = note
		self.__Data: dict[str, dict[str | None] | list[str]] = {
			"slots": data.get("slots") or dict().fromkeys(self.__Note.table.manifest.attachments.slots_names),
			"free": data.get("free") or list()
		}

		if bool(note.table.manifest.attachments.rule): os.makedirs(self.__Note.table.full_path / ".attachments", exist_ok = True)

		self.__Slots: dict[str, Slot] = self.__ParseSlots()

	def attach(self, file: Path, copy: bool = False):
		"""
		Прикрепляет свободный файл к записи.

		:param file: Путь к файлу.
		:type file: Path
		:param copy: Указывает, нужно ли скопировать файл или переместить. 
		:type copy: bool
		:raises AttachmentsDenied: Вложение запрещено.
		"""
		
		Rule = self.__Note.table.manifest.attachments.rule
		if Rule < 2: raise Exceptions.Note.AttachmentsDenied(bool(Rule))

		self.__Data["free"] = file.name

		AttachmentsDirectoryPath = self.directory
		os.makedirs(AttachmentsDirectoryPath, exist_ok = True)
		AttachmentPath = AttachmentsDirectoryPath / file

		if copy: shutil.copy(file, AttachmentPath)
		else: os.replace(file, AttachmentPath)
		
		self.__Note.save()
		self.__Note.run_callback(CallbacksTypes.AttachmentsChanged)

	def get_slot(self, slot: str) -> Slot:
		"""
		Возвращает данные слота.

		:param slot: Имя слота.
		:type slot: str
		:return: Данные о слоте.
		:rtype: SlotInfo
		:raises AttachmentSlotNotDescribed: Слот вложения не описан.
		"""

		if slot not in self.__Slots: raise Exceptions.Note.AttachmentSlotNotDescribed(slot)

		return self.__Slots[slot]

	def move(self, new_id: int):
		"""
		Перемещает вложения в каталог, соответствующий новому ID записи.

		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if self.count > 0:
			OldAttachmentsPath = self.__Note.table.full_path / ".attachments" / str(self.__Note.id)
			NewAttachmentsPath =  self.__Note.table.full_path / ".attachments" / str(new_id)
			shutil.move(OldAttachmentsPath, NewAttachmentsPath)

	def to_dict(self) -> dict[str, dict[str | None] | list[str]]:
		"""
		Возвращает словарное представление данных вложений.

		:return: Словарное представление данных вложений.
		:rtype: dict[str, dict[str | None] | list[str]]
		"""

		return {
			"slots": {Name: SlotData.file for Name, SlotData in self.__Slots.items()},
			"free": self.__Data["free"]
		}

	def unnatach(self, filename: str):
		"""
		Удаляет свободное вложение по имени.

		:param filename: Имя вложения.
		:type filename: str
		"""

		try:
			os.remove(self.__Note.table.full_path / ".attachments" / filename)
			self.__Data["free"].remove(filename)
			self.__Note.save()
			self.__Note.run_callback(CallbacksTypes.AttachmentsChanged)

		except (FileNotFoundError, ValueError): pass

	def validate(self) -> tuple[ValidationError]:
		"""
		Проверяет существование заданных файлов вложений.

		:return: Последовательность структур, описывающих отсутствующие вложения.
		:rtype: tuple[ValidationError]
		"""

		Errors = list()
		AttachmentsDirectory = self.directory

		for FreeFile in self.__Data["free"]:
			FilePath = AttachmentsDirectory / FreeFile
			if not FilePath.exists(): Errors.append(ValidationError(None, FreeFile))

		for CurrentSlot in self.__Slots.values():
			if CurrentSlot.file and not CurrentSlot.is_exists(): Errors.append(ValidationError(CurrentSlot.name, CurrentSlot.file))

		return tuple(Errors)