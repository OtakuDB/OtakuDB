from Source.CLI.Templates import Error, ExecutionStatus
from Source.Tables.MediaViews import MediaViewsTable
from dublib.Methods import ReadJSON, WriteJSON

import shutil
import os

class Driver:
	"""Менеджер таблиц."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

	@property
	def is_mounted(self) -> bool:
		"""Состояние: монтировано ли хранилище."""

		return True if self.__StorageDirectory else False

	@property
	def tables(self) -> list[str]:
		"""Список названий существующих таблиц."""

		# Получение содержимого каталога хранения.
		StorageList = os.listdir(self.__StorageDirectory)
		# Список таблиц.
		Tables = list()

		# Для каждого объекта.
		for Object in StorageList:
	
			# Если объект является каталогом и содержит описание таблицы, записать имя каталога.
			if os.path.isdir(f"{self.__StorageDirectory}/{Object}") and os.path.exists(f"{self.__StorageDirectory}/{Object}/main.json"): Tables.append(Object)

		return Tables

	@property
	def storage_directory(self) -> str | None:
		"""Директория хранилища."""

		return self.__StorageDirectory

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ReadSession(self):
		"""Читает сессионный файл."""

		# Если файл сессии существует.
		if os.path.exists("session.json"):
			# Чтение файла сессии.
			self.__Session = ReadJSON("session.json")

		else:
			# Сохранение файла сессии.
			self.__SaveSession()

	def __SaveSession(self):
		"""Сохраняет сессионный файл."""

		# Сохранение файла сессии.
		WriteJSON("session.json", self.__Session)

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, mount: bool = False):
		"""
		Менеджер таблиц.
			mount – указывает, следует ли монтировать директорию хранилища.
		"""
		
		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Директория хранения таблиц.
		self.__StorageDirectory = None
		# Описание сессии.
		self.__Session = {
			"storage-directory": "Data"
		}

		# Чтение сессии.
		self.__ReadSession()
		# Если включено автомонтирование, выполнить его.
		if mount: self.mount()

	def create_table(self, name: str) -> ExecutionStatus:
		"""
		Создаёт таблицу.
			name – название таблицы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		# Состояние: успешно ли создание.
		try:
			# Создание таблицы.
			MediaViewsTable(self.__StorageDirectory, name)

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def mount(self, storage_dir: str | None = None) -> ExecutionStatus:
		"""
		Указывает каталог хранения таблиц.
			storage_dir – директория хранилища.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)
		# Если директория не определена, взять стандартную из файла сессии.
		storage_dir = self.__Session["storage-directory"] if not storage_dir else storage_dir
		
		# Состояние: успешно ли создание.
		try:
			
			# Если путь существует.
			if os.path.exists(storage_dir): 
				# Запись директории хранилища.
				self.__StorageDirectory = storage_dir
				# Изменение настроек сессии.
				self.__Session["storage-directory"] = storage_dir
				# Сохранение файла сессии.
				self.__SaveSession()

			else:
				# Изменение статуса.
				Status = ExecutionStatus(-2, "incorrect_storage_path")

		except:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "unknown_error")

		return Status

	def open_table(self, name: str) -> MediaViewsTable | ExecutionStatus:
		"""
		Открывает таблицу. Возвращает объектное представление таблицы.
			name – название таблицы.
		"""

		# Таблица.
		Table = None

		try:
			# Создание таблицы.
			Table = MediaViewsTable(self.__StorageDirectory, name, autocreation = False)

		except FileExistsError:
			# Изменение статуса.
			Table = ExecutionStatus(-1, "unknown_error")

		return Table

	def remove_table(self, name: str) -> ExecutionStatus:
		"""
		Удаляет таблицу.
			name – название таблицы.
		"""

		# Статус выполнения.
		Status = ExecutionStatus(0)

		# Состояние: успешно ли удаление.
		try:
			# Удаление таблицы.
			shutil.rmtree(f"{self.__StorageDirectory}/{name}")

		except FileNotFoundError:
			# Изменение статуса.
			Status = ExecutionStatus(-1, "table_not_found")

		return Status