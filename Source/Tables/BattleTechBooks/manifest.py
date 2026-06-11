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

		manifest.connections.bonds.create_bond_parameters("stories", "Stories that make up the book.", save = False)

		manifest.metainfo_rules.create_field_parameters(
			field = "author",
			types = str,
			allow_list = True,
			description = "One or more authors.",
			save = False
		)
		manifest.metainfo_rules.create_field_parameters(
			field = "publisher",
			types = str,
			description = "Publisher of paper book.",
			save = False
		)
		manifest.metainfo_rules.create_field_parameters(
			field = "series",
			types = str,
			allow_list = True,
			values = ("Blitzkrieg", "MechWarrior"),
			description = "Series to which the book belongs.",
			save = False
		)
		manifest.metainfo_rules.create_field_parameters(
			field = "publication_date",
			types = str,
			description = "Date of book publication in original.",
			save = False
		)
		manifest.metainfo_rules.create_field_parameters(
			field = "story_source",
			types = str,
			allow_list = True,
			description = "Source of story.",
			save = False
		)

		ColumnsNames = ("ID", "Status", "Name", "Author", "Publication", "Type", "Series", "Era", "Estimation")
		OptionsCLI = {
			"columns": dict().fromkeys(ColumnsNames, {"enabled": True, "max_width": None})
		}
		manifest.interfaces_options.set_options(Interfaces.CLI, OptionsCLI, save = False)

		return manifest