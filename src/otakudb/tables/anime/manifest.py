from pydantic import BaseModel

from otakudb.core.base.manifest.generator import Manifest, ManifestGenerator

class CustomSettingsModel(BaseModel):
	"""Custom settings model."""

	max_estimation: int = 10

class Generator(ManifestGenerator[CustomSettingsModel]):
	"""Генератор манифеста."""

	def _edit_manifest(self, manifest: Manifest) -> Manifest:
		"""
		Переопределите данный метод для редактирования стандартного манифеста.

		После завершения редактирования сохранение происходит автоматически.

		:param manifest: Редактируемый манифест.
		:type manifest: Manifest
		:return: Отредактированный манифест.
		:rtype: Manifest
		"""

		manifest.metainfo_rules.create_field_parameters(
			field = "base",
			types = str,
			values = ("game", "manga", "novel", "original", "ranobe"),
			description = "Base for anime.",
		)

		return manifest

	def _export_custom_settings_model(self) -> type[CustomSettingsModel]:
		"""
		Export custom settings typing [pydantic](https://github.com/pydantic/PYDANTIC) model.

		:return: Custom settings typing model.
		:rtype: type[CustomSettingsModel]
		"""

		return CustomSettingsModel
