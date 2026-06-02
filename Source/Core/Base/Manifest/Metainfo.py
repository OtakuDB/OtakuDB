from dublib.Methods.Data import ToIterable

from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
	from . import Manifest

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class MetainfoFieldDescription:
	"""Данные поля метаданных."""

	name: str
	values: tuple[int | float | str] | None
	description: str | None

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление данных.

		:return: Словарное представление данных.
		:rtype: dict
		"""

		Values = self.values
		if Values != None and len(Values) == 1: Values = Values[0]

		return {
			"values": Values,
			"description": self.description
		}

#==========================================================================================#
# >>>>> ОСНОВНОЙ КЛАСС <<<<< #
#==========================================================================================#

class MetainfoRules:
	"""Правила метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_free_allowed(self) -> bool:
		"""Состояние: разрешены ли неопределённые в правилах поля метаданных."""

		return self.__Data["free_allowed"]
	
	@property
	def fields(self) -> tuple[MetainfoFieldDescription]:
		"""Последовательность данных полей."""

		return tuple(self.__Fields.values())

	@property
	def fields_names(self) -> tuple[str]:
		"""Последовательность имён явно указанных полей метаданных."""

		return tuple(self.__Data["fields"].keys())
	
	@property
	def is_enabled(self) -> bool:
		"""Состояние: разрешено ли использование метаданных."""

		return any((self.__Data["free_allowed"], self.__Data["fields"]))

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseFields(self) -> dict[str, MetainfoFieldDescription]:
		"""
		Парсит словарь данных полей в объектные представления.

		:return: Список представлений данных полей.
		:rtype: dict[str, MetainfoFieldDescription]
		"""

		FieldsData = dict()

		for Field in self.fields_names:
			Rule: dict = self.__Data["fields"][Field]

			Values = Rule.get("values")
			if Values != None: Values = ToIterable(Values)
			Description = Rule.get("description")

			FieldsData[Field] = MetainfoFieldDescription(Field, Values, Description)

		return FieldsData

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __init__(self, manifest: "Manifest"):
		"""
		Правила метаданных.

		:param manifest: Манифест таблицы.
		:type manifest: Manifest
		"""

		self.__Manifest = manifest

		self.__Data: dict[str, bool | dict] = {
			"free_allowed": False,
			"fields": dict()
		}
		self.__Fields: dict[str, MetainfoFieldDescription] = self.__ParseFields()

	def get_field(self, field: str) -> MetainfoFieldDescription:
		"""
		Возвращает данные поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Данные поля.
		:rtype: MetainfoFieldDescription
		:raises KeyError: Данные поля не найдены.
		"""

		return self.__Fields[field]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__Data = self.__Data | data
		self.__Fields: dict[str, MetainfoFieldDescription] = self.__ParseFields()

	def remove_field(self, field: str):
		"""
		Удаляет данные поля метаданных.

		:param field: Имя поля.
		:type field: str
		"""

		try:
			del self.__Fields[field]
			self.__Manifest.save()
		except KeyError: pass

	def set_field(self, field: str, values: Iterable[int | float | str] | None, description: str | None = None):
		"""
		Добавляет правило проверки поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param values: Последовательность принимаемых значений или `None` для любого.
		:type values: Iterable[int | float | str] | None
		:param description: Описание поля.
		:type description: str | None
		"""

		self.__Fields[field] = MetainfoFieldDescription(field, values, description)
		self.__Manifest.save()

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"free_allowed": self.is_free_allowed,
			"fields": {FieldData.name: FieldData.to_dict() for FieldData in self.__Fields.values()}
		}
