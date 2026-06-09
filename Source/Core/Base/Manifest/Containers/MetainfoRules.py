from ._Base import BaseContainer

from Source.Core import Exceptions

from dublib.Methods.Data import ToIterable

from dataclasses import dataclass
from typing import Iterable

#==========================================================================================#
# >>>>> ВСПОМОГАТЕЛЬНЫЕ СТРУКТУРЫ ДАННЫХ <<<<< #
#==========================================================================================#

@dataclass(frozen = True)
class MetainfoFieldParameters:
	"""Параметры поля метаданных."""

	name: str
	values: tuple[int | float | str] | None
	description: str | None

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
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

class MetainfoRules(BaseContainer):
	"""Правила метаданных."""

	#==========================================================================================#
	# >>>>> СВОЙСТВА <<<<< #
	#==========================================================================================#

	@property
	def is_free_allowed(self) -> bool:
		"""Состояние: разрешены ли неопределённые в правилах поля метаданных."""

		return self.__IsFreeAllowed
	
	@property
	def fields(self) -> tuple[MetainfoFieldParameters]:
		"""Последовательность параметров полей метаданных."""

		return tuple(self.__Fields.values())

	@property
	def fields_names(self) -> tuple[str]:
		"""Последовательность имён явно указанных полей метаданных."""

		return tuple(self.__Fields.keys())
	
	@property
	def rule(self) -> bool:
		"""
		Правило использования метаданных.
		
		* 0 – запрещены все метаданные;
		* 1 – разрешены только определённые поля метаданных;
		* 2 – разрешены все метаданные.
		"""

		if not all((self.__IsFreeAllowed, self.__Fields)): return 0
		elif not self.__IsFreeAllowed: return 1
		else: return 2

	#==========================================================================================#
	# >>>>> ПРИВАТНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def __ParseFields(self) -> dict[str, MetainfoFieldParameters]:
		"""
		Парсит словарь данных полей в объектные представления.

		:return: Список представлений данных полей.
		:rtype: dict[str, MetainfoFieldParameters]
		"""

		FieldsData = dict()

		for Field in self.fields_names:
			Rule: dict = self.__Data["fields"][Field]

			Values = Rule.get("values")
			if Values != None: Values = ToIterable(Values)
			Description = Rule.get("description")
			
			FieldsData[Field] = MetainfoFieldParameters(Field, Values, Description)

		return FieldsData

	#==========================================================================================#
	# >>>>> ПЕРЕОПРЕДЕЛЯЕМЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def _PostInitMethod(self):
		"""Метод, выполняющийся после инициализации объекта."""

		self.__IsFreeAllowed = False
		self.__Fields: dict[str, MetainfoFieldParameters] = self.__ParseFields()

	#==========================================================================================#
	# >>>>> ПУБЛИЧНЫЕ МЕТОДЫ <<<<< #
	#==========================================================================================#

	def add_field(self, field: str, values: Iterable[int | float | str] | None, description: str | None = None, save: bool = True):
		"""
		Создаёт параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param values: Последовательность принимаемых значений или `None` для любого.
		:type values: Iterable[int | float | str] | None
		:param description: Описание поля.
		:type description: str | None
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		"""

		self.__Fields[field] = MetainfoFieldParameters(field, values, description)
		if save: self.save()

	def get_field_parameters(self, field: str) -> MetainfoFieldParameters:
		"""
		Возвращает параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:return: Параметры поля.
		:rtype: MetainfoFieldParameters
		:raises MetainfoFieldNotDescribed: Данные поля не найдены.
		"""

		if field not in self.__Fields: raise Exceptions.Note.MetainfoFieldNotDescribed(field)

		return self.__Fields[field]

	def parse(self, data: dict):
		"""
		Парсит данные из переданного словаря.

		:param data: Словарь данных.
		:type data: dict
		"""

		self.__IsFreeAllowed = bool(data.get("free_allowed"))
		self.__Fields: dict[str, MetainfoFieldParameters] = self.__ParseFields()

	def remove_field(self, field: str, save: bool = True):
		"""
		Удаляет параметры поля метаданных.

		:param field: Имя поля.
		:type field: str
		:param save: Указывает, нужно ли выполнить сохранение манифеста после процедуры.
		:type save: bool
		:raises MetainfoFieldNotDescribed: Поле метаданных не описано.
		"""

		if field not in self.__Fields: raise Exceptions.Note.MetainfoFieldNotDescribed(field)
		del self.__Fields[field]
		if save: self.save()

	def to_dict(self) -> dict:
		"""
		Возвращает словарное представление объекта.

		:return: Словарное представление объекта.
		:rtype: dict
		"""

		return {
			"free_allowed": self.__IsFreeAllowed,
			"fields": {FieldData.name: FieldData.to_dict() for FieldData in self.__Fields.values()}
		}
