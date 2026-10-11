import sys
from typing import Literal, NoReturn, overload

from dublib.cli.messages.generator import MessagesTypes, generate_message
from dublib.cli.text_styler import get_styled_text_from_html

class Printer:
	"""Output operator."""

	#==========================================================================================#
	# >>>>> PUBLIC METHODS <<<<< #
	#==========================================================================================#

	def emit(self, text: str, message_type: MessagesTypes | None = None, origin: str | None = None, end_line: bool = True, flush: bool = False, parse_html: bool = True):
		"""
		Send message to output stream.

		:param text: Message text.
		:type text: str
		:param message_type: Message type.
		:type message_type: MessagesTypes | None
		:param origin: Message origin.
		:type origin: str | None
		:param end_line: Condition: is newline character at string end required.
		:type end_line: bool
		:param flush: Condition: is flush cached data.
		:type flush: bool
		:param parse_html: Condition: parse message text with `get_styled_text_from_html()`.
		:type parse_html: bool
		"""

		if parse_html: text = get_styled_text_from_html(text)
		styled_text: str = generate_message(text, message_type, origin)
		print(styled_text, end = "\n" if end_line else "", flush = flush)

	#==========================================================================================#
	# >>>>> ШАБЛОНЫ ВЫВОДА БАЗОВЫХ ТИПОВ СООБЩЕНИЙ <<<<< #
	#==========================================================================================#

	@overload
	def critical(self, text: str, origin: str | None = None, end_work: Literal[True] = ...) -> NoReturn: ...
	@overload
	def critical(self, text: str, origin: str | None = None, end_work: Literal[False] = False): ...

	def critical(self, text: str, origin: str | None = None, end_work: bool = False):
		"""
		Print critical error.

		:param text: Message text.
		:type text: str
		:param origin: Message origin.
		:type origin: str | None
		:param end_work: Condition: end script work.
		:type end_work: bool
		"""

		self.emit(text, MessagesTypes.Critical, origin)
		if end_work: sys.exit(1)

	def debug(self, text: str, origin: str | None = None):
		"""
		Print debug message.

		:param text: Message text.
		:type text: str
		:param origin: Message origin.
		:type origin: str | None
		"""

		self.emit(text, MessagesTypes.Debug, origin)

	def error(self, text: str, origin: str | None = None):
		"""
		Print error.

		:param text: Message text.
		:type text: str
		:param origin: Message origin.
		:type origin: str | None
		"""

		self.emit(text, MessagesTypes.Error, origin)

	def warning(self, text: str, origin: str | None = None):
		"""
		Print warning.

		:param text: Message text.
		:type text: str
		:param origin: Message origin.
		:type origin: str | None
		"""

		self.emit(text, MessagesTypes.Warning, origin)
