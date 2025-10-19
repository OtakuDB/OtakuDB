from Source.Core.Bus import ExecutionStatus
from Source.Core.Messages import Errors
from Source.Core.Exceptions import *

from dublib.Methods.Filesystem import ReadJSON, WriteJSON

from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
	from .Objects import Table, Module, Note

	from Source.Core.Driver import Driver

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
		self.__Local = TableBinds(self.__Module or self.__Table)