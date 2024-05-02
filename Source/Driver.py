from Source.CLI.Templates import Error, ExecutionStatus
from Source.Tables.MediaViews import MediaViewsTable

import shutil
import os

class Driver:
	"""Менеджер таблиц."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА ТОЛЬКО ДЛЯ ЧТЕНИЯ <<<<< #
	#==========================================================================================#

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

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	# В разработке...	

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, storage_dir: str = "Data"):
		"""
		Менеджер таблиц.
			storage_dir – директория хранения таблиц. 
		"""
		
		#---> Генерация динамичкских свойств.
		#==========================================================================================#
		# Директория хранения таблиц.
		self.__StorageDirectory = storage_dir.rstrip("/\\")

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

	def open_table(self, name: str) -> MediaViewsTable | ExecutionStatus:
		"""
		Открывает таблицу и возвращает её дескриптор.
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