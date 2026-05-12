from .TableDescriptor import TableDescriptor
from .Box import Box

from Source.Core import Exceptions

from typing import TYPE_CHECKING
from pathlib import Path
from os import PathLike
import importlib
import os

if TYPE_CHECKING:
	from Source.Core.Base.Manifest.Generator import ManifestGenerator

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class Driver:
	"""Драйвер хранилища."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def storage_directory(self) -> Path | None:
		"""Директория хранилища."""

		return self.__StorageDirectory

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self):
		"""Драйвер хранилища."""
		
		self.__StorageDirectory = None

	def is_box(self, virtual_path: Path) -> bool:
		"""
		Проверяет, представляет ли директория по вирутальному пути контейнер.

		:param virtual_path: Виртуальный путь к директории.
		:type virtual_path: Path
		:return: Возвращает `True`, если директория является контейнером.
		:rtype: bool
		"""

		TotalPath = self.__StorageDirectory / virtual_path / "manifest.json"

		return not TotalPath.exists()

	def mount(self, directory: PathLike):
		"""
		Монтирует указанную директорию как хранилище.

		:param directory: Директория хранилища.
		:type directory: PathLike
		:raises FileNotFoundError: Выбрасывается при отсутствии монтируемой директории.
		"""

		if not os.path.exists(directory): raise FileNotFoundError(directory)
		self.__StorageDirectory = Path(directory)

	def create_box(self, parent_path: Path | None, name: str) -> Box:
		"""
		Создаёт новый контейнер.

		:param parent_path: Путь к родительскому контейнеру.
		:type parent_path: Path | None
		:param name: Название контейнера.
		:type name: str
		:return: Новый контейнер.
		:rtype: Box
		:raises StorageUnmounted: Хранилище отмонтировано.
		"""

		if not self.__StorageDirectory: raise Exceptions.Driver.StorageUnmounted()

		TotalPath = self.__StorageDirectory / parent_path / name
		os.makedirs(TotalPath, exist_ok = True)

		return Box(self, parent_path, name)

	def create_table(self, type: str, name: str, path: Path) -> TableDescriptor:
		"""
		Создаёт новую таблицу.

		:param type: Тип таблицы.
		:type type: str
		:param name: Название таблицы.
		:type name: str
		:param path: Виртуальный путь к контейнеру таблицы.
		:type path: Path
		:return: Дескриптор таблицы.
		:rtype: TableDescriptor
		:raises StorageUnmounted: Хранилище отмонтировано.
		:raises TableAlreadyExists: Таблица уже существует.
		"""

		if not self.__StorageDirectory: raise Exceptions.Driver.StorageUnmounted()

		path = path / name
		TotalPath = self.__StorageDirectory / path

		if TotalPath.exists(): raise Exceptions.Driver.TableAlreadyExists(path)

		os.makedirs(TotalPath, exist_ok = True)

		ManifestGeneratorModule = importlib.import_module(f"Source.Tables.{type}.manifest")
		ManifestGenerator: "ManifestGenerator" = ManifestGeneratorModule.Generator(TotalPath, type)
		Manifest = ManifestGenerator.generate()

		return TableDescriptor(self, self.__WorkTree, path, Manifest)
	
	def get_box(self, virtual_path: Path | None = None) -> Box:
		"""
		Вовзаращает контейнер по вирутальному пути.

		:param virtual_path: Виртуальный путь к контейнеру. При отсутствии будет возвращён корневой контейнер.
		:type virtual_path: Path | None
		:return: Контейнер.
		:rtype: Box
		:raises FileNotFoundError: Вирутальный путь не найден.
		"""

		virtual_path = virtual_path or Path()

		TotalPath = self.__StorageDirectory / virtual_path
		if not TotalPath.exists(): raise FileNotFoundError(TotalPath)

		if virtual_path and str(virtual_path) != ".": return Box(self, virtual_path.parent, virtual_path.name)
		else: return Box(self)