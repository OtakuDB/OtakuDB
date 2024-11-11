# from dublib.Methods.JSON import ReadJSON, WriteJSON

# import os

# Path = "Data/bt/books"
# Files = os.listdir(Path)
# if "manifest.json" in Files: Files.remove("manifest.json")

# for File in Files:
# 	Data = ReadJSON(f"{Path}/{File}")

# 	Data["attachments"] = {"slots": {"ebook": None}}

# 	WriteJSON(f"{Path}/{File}", Data)

# exit(0)

from Source.CLI.Interpreter import Interpreter

Interpreter().run()