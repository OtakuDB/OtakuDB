from pydantic import BaseModel

class CommonInterfaceOptionsModel(BaseModel):
	"""Common interface options model."""

	autoclear: bool = True
	autoview: bool = True
