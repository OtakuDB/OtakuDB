from pydantic import BaseModel

class GlobalInterfaceOptionsModel(BaseModel):
	"""Global interface options model."""

	autoclear: bool = True
	autoview: bool = True
