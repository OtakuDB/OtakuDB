import os
import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ....core import exceptions
from .enums import CallbacksTypes

if TYPE_CHECKING:
	from pathlib import Path

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

		return self.__file
	
	@property
	def full_path(self) -> Path | None:
		"""Полный путь к файлу."""

		if self.__file:
			return self.__attachments.directory / self.__file

	@property
	def name(self) -> str:
		"""Имя слота."""

		return self.__name

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

		self.__attachments: "Attachments" = attachments
		self.__name: str = name
		self.__file: str | None = file

		self.__note: "BaseNote" = self.__attachments.note

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
		
		match self.__note.table.manifest.attachments.rule:
			case 0: raise exceptions.note.attachments.AttachmentsDeniedError(False)
		
		if self.__file:
			raise exceptions.note.attachments.AttachmentSlotAlreadyFilledError(self.__name)

		self.__file = file.name

		attachment_path: "Path" = self.__attachments.directory / file

		if copy: shutil.copy(file, attachment_path)
		else: os.replace(file, attachment_path)
		
		self.__note.save()
		self.__note.run_callback(CallbacksTypes.AttachmentsChanged)

	def clear(self):
		"""Очищает слот."""

		if not self.full_path:
			return

		self.full_path.unlink(missing_ok = True)

		self.__note.save()
		self.__note.run_callback(CallbacksTypes.AttachmentsChanged)

	def is_exists(self) -> bool:
		"""
		Проверяет, существует ли файл вложения.

		:return: Возвращает `True`, если указан файл и он существует.
		:rtype: bool
		"""

		full_path: "Path | None" = self.full_path

		if not full_path:
			return False

		return full_path.exists()

@dataclass(frozen = True)
class AttachmentFileErrorData:
	"""Attachment file error data."""

	slot: str | None
	file: str

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Attachments[N: "BaseNote" = "BaseNote"]:
	"""Вложения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def directory(self) -> Path:
		"""Note attachments directory."""

		return self.__note_attachments_directory

	@property
	def count(self) -> int:
		"""Attachments count."""

		return len(self.__free) + sum(1 for slot in self.slots if slot.file)

	@property
	def free(self) -> tuple[str, ...]:
		"""Free attachments files names."""

		return tuple(self.__free)

	@property
	def note(self) -> N:
		"""Note to which the attachments belong."""

		return self.__note

	@property
	def slots(self) -> tuple[Slot, ...]:
		"""Slots info."""

		return tuple(self.__slots.values())

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __parse_slots(self, slota_data: dict[str, str | None]) -> dict[str, Slot]:
		"""
		Parse slots info raw data into typed objects.

		:param slota_data: Raw slots data dictionary.
		:type slota_data: dict[str, str  |  None]
		:return: Dictionary in wich key is slot name and value is slot info.
		:rtype: dict[str, Slot]
		"""

		return {name: Slot(self, name, file) for name, file in slota_data.items()}

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: N, data: dict):
		"""
		Оператор вложений.

		:param note: Запись.
		:type note: BaseNote
		:param data: Словарь данных вложений.
		:type data: dict
		"""

		self.__note: N = note

		self.__note_attachments_directory: "Path" = self.__note.table.full_path / ".attachments" / str(self.__note.id)

		if bool(note.table.manifest.attachments.rule):
			self.__note_attachments_directory.mkdir(parents = True, exist_ok = True)

		self.__slots: dict[str, Slot] = self.__parse_slots(data.get("slots") or dict.fromkeys(self.__note.table.manifest.attachments.slots_names))
		self.__free: list[str] = data.get("free", [])

	def attach(self, file: "Path", copy: bool = False):
		"""
		Make free attachment.

		:param file: File path.
		:type file: Path
		:param copy: Enable file copying instead replacing.
		:type copy: bool
		:raises AttachmentsDeniedError: Attachments denied.
		"""
		
		rule: int = self.__note.table.manifest.attachments.rule

		if rule < 2:
			raise exceptions.note.attachments.AttachmentsDeniedError(bool(rule))

		self.__free.append(file.name)

		attachment_path: "Path" = self.__note_attachments_directory / file

		if copy: shutil.copy(file, attachment_path)
		else: os.replace(file, attachment_path)
		
		self.__note.save()
		self.__note.run_callback(CallbacksTypes.AttachmentsChanged)

	def get_slot(self, slot: str) -> Slot:
		"""
		Возвращает данные слота.

		:param slot: Имя слота.
		:type slot: str
		:return: Данные о слоте.
		:rtype: SlotInfo
		:raises AttachmentSlotNotDescribedError: Слот вложения не описан.
		"""

		if slot not in self.__slots:
			raise exceptions.note.attachments.AttachmentSlotNotDescribedError(slot)

		return self.__slots[slot]

	def move(self, new_id: int):
		"""
		Перемещает вложения в каталог, соответствующий новому ID записи.

		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if self.count > 0:
			old_note_attachments_path: "Path" = self.__note_attachments_directory
			new_note_attachments_path = old_note_attachments_path.with_stem(str(new_id))
			shutil.move(old_note_attachments_path, new_note_attachments_path)

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"slots": {name: slot.file for name, slot in self.__slots.items()},
			"free": self.__free
		}

	def unattach(self, filename: str):
		"""
		Delete free attachment.

		:param filename: Attachment file name.
		:type filename: str
		:raises FileNotFoundError: Attachment file not found.
		"""

		attachment_path: "Path" = self.__note_attachments_directory / filename
		attachment_path.unlink()

		self.__free.remove(filename)

		self.__note.save()
		self.__note.run_callback(CallbacksTypes.AttachmentsChanged)

	def validate(self) -> tuple[AttachmentFileErrorData, ...]:
		"""
		Проверяет существование заданных файлов вложений.

		:return: Последовательность структур, описывающих отсутствующие вложения.
		:rtype: tuple[AttachmentFileErrorData, ...]
		"""

		errors: list[AttachmentFileErrorData] = []

		for free_file in self.__free:
			file_path: "Path" = self.__note_attachments_directory / free_file

			if not file_path.exists():
				errors.append(AttachmentFileErrorData(None, free_file))

		for slot in self.__slots.values():
			if slot.file and not slot.is_exists():
				errors.append(AttachmentFileErrorData(slot.name, slot.file))

		return tuple(errors)