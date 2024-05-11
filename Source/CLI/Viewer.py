from dublib.StyledPrinter import StyledPrinter, Styles
from Source.Tables.MediaViews import MediaViewsTable, MediaViewsNote

def View(table: MediaViewsTable, note: MediaViewsNote):
	"""
	Выводит форматированные данные записи.
		table – объектное представление таблицы;
		note – объектное представление записи.
	"""

	# Если передана запись о просмотрах.
	if type(note) == MediaViewsNote:
		# Получение основных значений.
		TotalProgress = f" ({note.progress}% viewed)" if note.progress else ""
		# Вывод названия и прогресса.
		if note.name: StyledPrinter(note.name, decorations = [Styles.Decorations.Bold], end = False)
		print(f"{TotalProgress} {note.emoji_status}")

		# Если указаны альтернативные названия.
		if note.another_names:
			# Вывести каждое название.
			for name in note.another_names: StyledPrinter(f"    {name}", decorations = [Styles.Decorations.Italic])

		# Вывод оценки.
		if note.estimation: print(f"⭐ {note.estimation} / {table.max_estimation}")
		# Получение частей.
		Parts = note.parts

		# Если задана группа.
		if note.group_id:
			# Вывод в консоль: заголовок тегов.
			StyledPrinter(f"GROUP: ", decorations = [Styles.Decorations.Bold], end = False)
			# Название группы.
			GroupName = f"@{note.group_id}" if not table.get_group(note.group_id) else table.get_group(note.group_id)["name"]
			if GroupName == "@None": GroupName = ""
			# Вывод в консоль: название группы.
			StyledPrinter(GroupName, decorations = [Styles.Decorations.Italic])

		# Если заданы теги.
		if note.tags:
			# Вывод в консоль: заголовок тегов.
			StyledPrinter(f"TAGS: ", decorations = [Styles.Decorations.Bold], end = False)
			# Вывод в консоль: теги.
			print(", ".join(note.tags))

		# Если имеются части.
		if Parts:
			# Вывод в консоль: заголовок частей.
			StyledPrinter(f"PARTS:", decorations = [Styles.Decorations.Bold])

			# Для каждой части.
			for PartIndex in range(0, len(Parts)):
				# Статус просмотра.
				Watched = " ✅" if Parts[PartIndex]["watched"] else ""

				# Если часть многосерийная.
				if "series" in Parts[PartIndex].keys():
					# Закладка.
					Mark = str(Parts[PartIndex]["mark"]) + " / " if "mark" in Parts[PartIndex] else ""
					# Индикатор закладки.
					MarkIndicator = " ⏳" if Mark else ""
					# Прогресс просмотра части.
					Progress = " (" + str(int(Parts[PartIndex]["mark"] / Parts[PartIndex]["series"] * 100)) + "% viewed)" if Mark else ""
					# Номер сезона.
					Number = str(Parts[PartIndex]["number"]) if "number" in Parts[PartIndex].keys() else ""

					# Вывод в консоль: тип части.
					print(f"    {PartIndex} ▸ " + Parts[PartIndex]["type"] + f": {Number}{Watched}{MarkIndicator}")
					# Вывод в консоль: прогресс просмотра.
					print("    " + " " * len(str(PartIndex)) + f"       {Mark}" + str(Parts[PartIndex]["series"]) + f" series{Progress}")

				else:
					# Название фильма.
					Name = ": " + Parts[PartIndex]["name"] if Parts[PartIndex]["name"] else ""
					# Вывод в консоль: название.
					print(f"    {PartIndex} ▸ " + Parts[PartIndex]["type"] + f"{Name}{Watched}")

				# Вывод в консоль: метаданные.
				if "link" in Parts[PartIndex].keys(): print("    " + " " * len(str(PartIndex)) + f"       🔗 " + Parts[PartIndex]["link"])
				if "comment" in Parts[PartIndex].keys(): print("    " + " " * len(str(PartIndex)) + f"       💭 " + Parts[PartIndex]["comment"])