from .Session import Session

from Source.Interfaces.CLI.Interpreter import Interpreter

from typing import Literal

class SessionsManager:
	"""Менеджер сессий."""

	def create_session(self) -> Session:
		"""
		Инициализирует сессию.

		:return: Сессия.
		:rtype: Session
		"""

		return Session()
	
	def run_interface(self, session: Session, interface: Literal["cli"] | None = None):
		"""
		_summary_

		:param session: _description_
		:type session: Session
		:param interface: Идентификатор интерфейса. По умолчанию: _cli_.
		:type interface: Literal["cli"] | None
		"""

		{
			"cli": Interpreter
		}[interface or "cli"](session).run()