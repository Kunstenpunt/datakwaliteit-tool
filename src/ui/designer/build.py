import os
import subprocess

ui_dir = r"./src/ui/designer"
ui_files = []

for path, _, files in os.walk(ui_dir):
    for file in files:
        if file.endswith(".ui"):
            ui_files.append(os.path.join(ui_dir, file))

for ui_file in ui_files:
    subprocess.run(["pyside6-uic", ui_file, "-o", f"{ui_file[:-3]}.py"])
