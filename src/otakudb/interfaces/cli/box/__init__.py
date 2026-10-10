from dublib.cli.terminalyzer import ModelsGroup
from dublib.validators import ValidableTypes

from ..base.processor import BaseCLI
from .handlers import BoxHandlers

class BoxCLI(BaseCLI):
	"""Box CLI processor."""

	@property
	def groups(self) -> tuple[ModelsGroup, ...]:
		"""Commands models groups."""

		return tuple(self._groups.values())

	def __build_box_models_group(self):
		"""Build box models group."""

		box_group: ModelsGroup = self.create_models_group("Box")
		
		model = box_group.create_model("go", "Navigate by virtual path.")
		position = model.create_position("PATH", "Virtual path.", important = True)
		position.set_argument(ValidableTypes.Path)
		model.register_handler(self.__handlers.go)

		model = box_group.create_model("mkdir", "Create box.")
		position = model.create_position("NAME", "Box name.", important = True)
		position.set_argument()
		model.base.add_flag("-o", description = "Open new box after creation.")
		model.register_handler(self.__handlers.mkdir)

		model = box_group.create_model("ls", "List box content.")
		model.register_handler(self.__handlers.ls)

		model = box_group.create_model("rmdir", "Delete box. By default only for empty boxes.")
		position = model.create_position("NAME", "Box name.", important = True)
		position.set_argument()
		model.base.add_flag("-p", description = "Purge all data in box if exists.")
		model.register_handler(self.__handlers.rmdir)

		model = box_group.create_model("types", "Print available tables types.")
		model.register_handler(self.__handlers.types)

	def _build_models(self):
		"""Build models and register handlers."""

		self.__build_box_models_group()

	def _post_init(self):
		"""Execute after instance initialization."""

		self.__handlers: BoxHandlers = BoxHandlers(self._interface)
