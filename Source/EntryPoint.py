import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from Source.Core.Session import Session
	from Source.Interfaces.Enums import Interfaces

def RunInterface(interface: "Interfaces", session: "Session"):
	"""
	Запускает интерфейс.

	:param interface: Тип интерфейса.
	:type interface: Interfaces
	:param session: Сессия.
	:type session: Session
	"""

	InterfaceModule = importlib.import_module(f"Source.Interfaces.{interface.name}")
	InterfaceModule.Interface(session).run()