from typing import TYPE_CHECKING

from dublib.cli.text_styler import FastStyler, TextStyler, codes

from ....core.session.box import Box, RootBox
from ....core.session.table_descriptor import TableDescriptor

if TYPE_CHECKING:
	from ....core.session import Session

class PromptGenerator:
	"""CLI prompt generator."""

	@property
	def prompt(self) -> str:
		"""CLI prompt."""

		storage: str = self.__get_storage_name()
		virtual_path: str = self.__get_virtual_path()
		note: str = ""

		path_separator: str = self.__path_separator if virtual_path else ""
		note_separator: str = self.__note_separator if note else ""

		return f"{storage}{path_separator}{virtual_path}{note_separator}{self.__indicator}"

	def __get_storage_name(self) -> str:
		"""
		Return storage name or driver literal.

		:return: Storage name or driver literal.
		:rtype: str
		"""

		storage: str = "otakudb"

		if self.__session.driver:
			storage = self.__session.driver.storage_path.name

		return self.__bold_magenta.get_styled_text(storage)

	def __get_virtual_path(self) -> str:
		"""
		Return styled virtual path.

		:return: Styled virtual path.
		:rtype: str
		"""

		if self.__session.navigator is None:
			return ""

		current_item: "Box | RootBox | TableDescriptor" = self.__session.navigator.current_item
		current_virtual_path: str = current_item.virtual_path.as_posix()

		if current_virtual_path == ".":
			return ""

		return self.__bold_green.get_styled_text(current_virtual_path)

	def __init__(self, session: "Session"):
		"""
		CLI prompt generator.

		:param session: Interaction session.
		:type session: Session
		"""

		self.__session: "Session" = session

		self.__bold_green: TextStyler = TextStyler(decorations = codes.Decorations.Bold, text_color = codes.Colors.Green)
		self.__bold_magenta: TextStyler = TextStyler(decorations = codes.Decorations.Bold, text_color = codes.Colors.Magenta)

		self.__indicator: str = FastStyler(" > ").decorate.bold
		self.__path_separator: str = FastStyler(":").decorate.bold
		self.__note_separator: str = FastStyler("-").decorate.bold