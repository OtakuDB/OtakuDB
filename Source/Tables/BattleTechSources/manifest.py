from Source.Core.Base.Manifest.Generator import Manifest, ManifestGenerator
from Source.Interfaces.Enums import Interfaces

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

		manifest.attachments.create_slot_parameters("ebook", "The e-book file.", save = False)

		manifest.metainfo_rules.create_field_parameters(
			field = "product_code",
			types = str,
			description = "Individual production code.",
			save = False
		)

		ColumnsNames = ("ID", "Status", "Code", "Name", "Ebook", "Type")
		OptionsCLI = {
			"columns": dict().fromkeys(ColumnsNames, {"enabled": True, "max_width": None})
		}
		manifest.interfaces_options.set_options(Interfaces.CLI, OptionsCLI, save = False)

		return manifest