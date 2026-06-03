from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:
	from Source.Core.Enums import Interfaces
	from Source.Core.Session import Session

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