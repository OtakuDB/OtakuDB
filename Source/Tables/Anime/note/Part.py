from .Enums import PartsTypes

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
	from . import Note

class Part:
	"""Часть тайтла."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def comment(self) -> str | None:
		"""Комментарий."""

		return self.__Data.get("comment")

	@property
	def name(self) -> str | None:
		"""Название части."""

		return self.__Data.get("type")
	
	@property
	def number(self) -> int | None:
		"""Номер части (не путать с индексом)."""

		return self.__Data.get("number")

	@property
	def progress(self) -> float:
		"""Доля просмотра части. Округляется до двух знаков после запятой."""

		if self.viewed == -1: return 1.0

		if self.viewed > 0:
			if self.type == PartsTypes.Film: return 1.0
			if self.series: return round(self.viewed / self.series, 2)

		return 0.0

	@property
	def series(self) -> int | None:
		"""Количество элементов в части. Для фильмов всегда 1."""

		if self.type == PartsTypes.Film: return 1
		else: return self.__Data.get("series")

	@property
	def type(self) -> PartsTypes:
		"""Тип части."""

		return PartsTypes(self.__Data["type"])
	
	@property
	def viewed(self) -> int:
		"""Состояние просмотра: -1 – не планируется, 0 – не просмотрено, 1 и более – количество просмотренных элементов."""

		return self.__Data.get("viewed")

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __Merge(self, data: dict):
		"""
		Выполняет слияние внутренних данных с переданным словарём.

		:param data: Словарь данных части.
		:type data: dict
		"""

		for Key in self.__Data.keys(): self.__Data[Key] = data[Key]
		if self.type == PartsTypes.Film: del self.__Data["series"]

		#---> Обработка Legacy-файлов.
		#==========================================================================================#
		if self.__Data["type"] == "special": self.__Data["type"] = PartsTypes.Specials.value
		if data.get("skipped"): self.__Data["viewed"] = -1
		if data.get("watched"): self.__Data["viewed"] = data.get("series") or 1
		if data.get("mark"): self.__Data["viewed"] = data.get("mark")

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, note: "Note", data: dict):
		"""
		Часть тайтла.

		:param note: Запись.
		:type note: Note
		:param data: Словарное представление данных части.
		:type data: dict
		"""

		self.__Note = note
		self.__Data = {
			"type": None,
			"name": None,

			"number": None,
			"series": None,

			"viewed": 0,
			"comment": None
		}

		self.__Merge(data)

	def rename(self, name: str | None):
		"""
		Переименовывает часть.

		:param name: Название части.
		:type name: str | None
		"""

		self.__Data["name"] = name
		self.__Note.save()

	def set_comment(self, comment: str | None):
		"""
		Задаёт комментарий.

		:param comment: Комментарий.
		:type comment: str | None
		"""

		self.__Data["comment"] = comment
		self.__Note.save()

	def set_number(self, number: int | None):
		"""
		Задаёт номер.

		:param number: Номер части. Служит для идентификации среди одинаковых имён, не путать с индексом.
		:type number: str | None
		"""

		self.__Data["number"] = number
		self.__Note.save()

	def set_series(self, series: int | None):
		"""
		Задаёт количество элементов в части.

		:param series: Количество элементов в части.
		:type series: int | None
		:raises ValueError: Неверное значение или попытка задать для фильма.
		"""

		if type(series) not in (int, type(None)) or type(series) == int and series < 1: raise ValueError("Incorrect series value.")
		if self.type == PartsTypes.Film: raise ValueError("Films not supported series.")
		self.__Data["series"] = series
		self.__Note.save()

	def set_type(self, part_type: PartsTypes):
		"""
		Задаёт тип части.

		:param part_type: Тип части.
		:type part_type: PartsTypes
		:raises ValueError: Неверное значение или попытка задать для фильма.
		"""

		self.__Data["type"] = part_type.value
		self.__Note.save()

	def set_viewed(self, viewed: int):
		"""
		Задаёт состояние просмтра.

		:param viewed: Состояние просмотра: -1 – не планируется, 0 – не просмотрено, 1 и более – количество просмотренных элементов.
		:type viewed: int
		:raises ValueError: Неверное или неподдерживаемое значение.
		"""

		if viewed > 1 and self.type == PartsTypes.Film: raise ValueError("Films not supported series.")
		if viewed < -1: raise ValueError("Minimal value is -1.")
		if self.series and viewed > self.series: raise ValueError("Viewed elements must be less than or same as series.")
		self.__Data["viewed"] = viewed
		self.__Note.save()

	def to_dict(self) -> dict[str, Any]:
		"""
		Возвращает словарное представление части.

		:return: Словарное представление части.
		:rtype: dict[str, Any]
		"""

		return self.__Data.copy()