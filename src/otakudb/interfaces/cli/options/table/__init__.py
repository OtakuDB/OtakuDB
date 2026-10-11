from pydantic import TypeAdapter

from .....core import exceptions
from .....core.base.manifest.sections.interfaces_options import InterfacesOptions
from ....enums import Interfaces
from .models import ColumnOptions, TableInterfaceOptionsModel

class TableInterfaceOptions:
	"""Параметры интерфейса таблицы."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def columns(self) -> dict[str, ColumnOptions]:
		"""Dictionary in which key is column name and value is options."""

		return self.__options.columns

	@property
	def custom(self) -> dict:
		"""Custom table view options."""

		return self.__options.custom

	#==========================================================================================#
	# >>>>> PRIVATE METHODS <<<<< #
	#==========================================================================================#

	def __parse(self) -> TableInterfaceOptionsModel:
		"""
		Validate and parse table view options.

		:return: Table view options.
		:rtype: TableInterfaceOptionsModel
		"""

		important_columns: tuple[str, ...] = ("ID", "Name")

		options_data: dict = self.__total.get_options(Interfaces.CLI)
		options: TableInterfaceOptionsModel = self.__adapter.validate_python(options_data)

		for column_name in important_columns:
			if column_name not in options.columns:
				raise exceptions.table.ManifestError(f"Missing important column \"{column_name}\" options in manifest.")

		return options

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, data: "InterfacesOptions"):
		"""
		Table interface options.

		:param data: Interfaces options.
		:type data: InterfacesOptions
		"""

		self.__total: InterfacesOptions = data

		self.__adapter: TypeAdapter[TableInterfaceOptionsModel] = TypeAdapter(TableInterfaceOptionsModel)
		self.__options: TableInterfaceOptionsModel = self.__parse()

	def save(self):
		"""Save table interface options."""

		options_data: dict = self.__adapter.dump_python(self.__options)
		self.__total.set_options(Interfaces.CLI, options_data)
