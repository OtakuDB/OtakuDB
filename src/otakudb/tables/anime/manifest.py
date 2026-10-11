from typing import override

from pydantic import BaseModel

from otakudb.core.base.manifest import BaseManifest

class CustomSettingsModel(BaseModel):
	"""Custom settings model."""

	max_estimation: int = 10

class Manifest(BaseManifest[CustomSettingsModel]):
	"""Manifest."""

	@override
	def _edit(self):
		"""Edit base manifest to generate table manifest."""

		self.metainfo_rules.create_field_parameters(
			field = "base",
			types = str,
			values = ("game", "manga", "novel", "original", "ranobe"),
			description = "Base for anime.",
		)

	@override
	def _export_custom_settings_model(self) -> type[CustomSettingsModel]:
		"""
		Export custom settings typing [pydantic](https://github.com/pydantic/PYDANTIC) model.

		:return: Custom settings typing model.
		:rtype: type[CustomSettingsModel]
		"""

		return CustomSettingsModel
