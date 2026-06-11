from Source.Core.Base.Manifest.Generator import Manifest, ManifestGenerator

class Generator(ManifestGenerator):
	"""Генератор манифеста."""

	def _EditManifest(self, manifest: Manifest) -> Manifest:
		"""
		Переопределите данный метод для редактирования стандартного манифеста.

		После завершения редактирования будет выполнено обязательное сохранение манифеста, поэтому для методов редактирования рекомендуется отключать сохранение.

		:param manifest: Редактируемый манифест.
		:type manifest: Manifest
		:return: Отредактированный манифест.
		:rtype: Manifest
		"""

		manifest.custom["max_estimation"] = 10

		manifest.metainfo_rules.create_field_parameters(
			field = "base",
			types = str,
			values = ("game", "manga", "novel", "original", "ranobe"),
			description = "Base for anime.",
			save = False
		)

		return manifest