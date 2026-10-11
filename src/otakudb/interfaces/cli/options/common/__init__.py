from typing import TYPE_CHECKING, Any

from pydantic import TypeAdapter

from ....enums import Interfaces
from .models import GlobalInterfaceOptionsModel

if TYPE_CHECKING:
	from .....core.session.data import SessionData

class CommonInterfaceOptions:
	"""Global interface options."""

	#==========================================================================================#
	# >>>>> PROPERTIES <<<<< #
	#==========================================================================================#

	@property
	def autoclear(self) -> bool:
		"""Condition: clear terminal before every `view` command."""

		return self.__options.autoclear

	@property
	def autoview(self) -> bool:
		"""Condition: view table or note after every navigation operation."""

		return self.__options.autoview

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def __init__(self, data: "SessionData"):
		"""
		Global interface options.

		:param data: SessionData
		:type data: SessionData
		"""

		self.__session_data: SessionData = data

		self.__adapter: TypeAdapter[GlobalInterfaceOptionsModel] = TypeAdapter(GlobalInterfaceOptionsModel)
		options: dict[str, Any] = self.__session_data.get_global_interface_options(Interfaces.CLI)
		self.__options: GlobalInterfaceOptionsModel = self.__adapter.validate_python(options)

	def save(self):
		"""Save interface options."""

		options: dict = self.__adapter.dump_python(self.__options)
		self.__session_data.set_global_interface_options(Interfaces.CLI, options)
