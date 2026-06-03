from ..Note.Enums import CallbacksTypes

from Source.Core import Exceptions

from dublib.Methods.Data import Copy

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

@dataclass(frozen = True)
class SlotInfo:
	"""Информация о слоте."""

	name: str
	file: str | None

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Attachments:
	"""Вложения."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def count(self) -> int:
		"""Количество вложений."""

		return len(self.__Data["free"]) + sum(1 for slot in self.slots if slot.file)

	@property
	def free(self) -> tuple[Path]:
		"""Последовательность свободных вложений."""

		return tuple(Path(Value) for Value in self.__Data["free"])

	@property
	def slots(self) -> tuple[SlotInfo]:
		"""Последовательность данных слотов."""

		return tuple(SlotInfo(Name, File) for Name, File in self.__Data["slots"].items())

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
			"slots": data.get("slots") or dict(),
			"free": data.get("free") or list()
		}

		if bool(note.table.manifest.attachments.rule): os.makedirs(self.__Note.table.full_path / ".attachments", exist_ok = True)

	def attach(self, file: Path, slot: str | None = None, copy: bool = False):
		"""
		Прикрепляет файл к записи.

		:param file: Путь к файлу.
		:type file: Path
		:param slot: Имя слота. 
		:type slot: str | None
		:param copy: Указывает, нужно ли скопировать файл или переместить. 
		:type copy: bool
		:raises AttachmentSlotAlreadyFilled: Слот уже содержит файл.
		:raises AttachmentsDenied: Вложение запрещено.
		:raises AttachmentSlotMissing: Слот вложения не описан.
		"""
		
		match self.__Note.table.manifest.attachments.rule:
			case 0: raise Exceptions.Note.AttachmentsDenied(False)
			case 1:
				if not slot: raise Exceptions.Note.AttachmentsDenied(True)

		if slot:
			if slot not in self.__Data["slots"]: raise Exceptions.Note.AttachmentSlotMissing(slot)
			if self.is_slot_occupied(slot): raise Exceptions.Note.AttachmentSlotAlreadyFilled(slot)
			self.__Data["slots"][slot] = file.name

		else: self.__Data["free"] = file.name

		AttachmentPath = self.__Note.table.full_path / ".attachments" / str(self.__Note.id)
		os.makedirs(AttachmentPath, exist_ok = True)
		AttachmentPath = AttachmentPath / file

		if copy: shutil.copy(file, AttachmentPath)
		else: os.replace(file, AttachmentPath)
		
		self.__Note.save()
		self.__Note.run_callback(CallbacksTypes.AttachmentsChanged)

	def clear_slot(self, slot: str):
		"""
		Очищает слот.

		:param slot: Имя слота.
		:type slot: str
		:raises AttachmentSlotMissing: Слот вложения не описан.
		"""

		if slot not in self.__Data["slots"]: raise Exceptions.Note.AttachmentSlotMissing(slot)

		AttachmentsDirectory = self.__Note.table.full_path / ".attachments" / str(self.__Note.id)

		try: os.remove(AttachmentsDirectory / self.__Data["slots"][slot])
		except FileNotFoundError: pass

		try: AttachmentsDirectory.rmdir()
		except (FileNotFoundError, OSError): pass

		self.__Data["slots"][slot] = None
		self.__Note.save()
		self.__Note.run_callback(CallbacksTypes.AttachmentsChanged)

	def get_slot_file(self, slot: str) -> str | None:
		"""
		Возвращает имя вложения, находящегося в слоте.

		:param slot: Имя слота.
		:type slot: str
		:return: Имя вложения в слоте.
		:rtype: str | None
		:raises AttachmentSlotMissing: Слот вложения не описан.
		"""

		if slot not in self.__Data["slots"]: raise Exceptions.Note.AttachmentSlotMissing(slot)

		return self.__Data["slots"][slot]

	def is_slot_occupied(self, slot: str) -> bool:
		"""
		Проверяет, занят ли слот вложением.

		:param slot: Имя слота.
		:type slot: str
		:return: Возвращает `True`, если слот содержит вложение.
		:rtype: bool
		"""

		try: return bool(self.get_slot_file(slot))
		except KeyError: return False

	def move(self, new_id: int):
		"""
		Перемещает вложения в каталог соответствующий новому ID записи.

		:param new_id: Новый ID записи.
		:type new_id: int
		"""

		if self.count > 0:
			OldAttachmentsPath = self.__Note.table.full_path / ".attachments" / str(self.__Note.id)
			NewAttachmentsPath =  self.__Note.table.full_path / ".attachments" / str(new_id)
			shutil.move(OldAttachmentsPath, NewAttachmentsPath)

	def to_dict(self, copy: bool = True) -> dict[str, dict[str | None] | list[str]]:
		"""
		Возвращает словарное представление данных вложений.

		:param copy: Указывает, нужно ли вернуть копию внутреннего словаря или оригинал.
		:type copy: bool
		:return: Словарное представление данных вложений.
		:rtype: dict[str, dict[str | None] | list[str]]
		"""

		return Copy(self.__Data) if copy else self.__Data

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