import os
import subprocess

ui_dir = r"./src/datakwaliteit_tool/ui/designer"
ui_files = []


def add_type_ignore_comments(filename: str) -> None:
    triggers = {
        "setupUi(": " # type: ignore",
        "retranslateUi(": " # type: ignore",
    }

    with open(filename, "r") as src:
        lines = src.readlines()

    modified = []
    for line in lines:
        stripped = line.rstrip("\n\r")
        appended = False

        for trigger, suffix in triggers.items():
            if trigger in line:
                newline = line[len(stripped) :]
                stripped += suffix + newline
                appended = True
                break

        modified.append(stripped if appended else line)

    with open(filename, "w") as dst:
        dst.writelines(modified)


for path, _, files in os.walk(ui_dir):
    for file in files:
        if file.endswith(".ui"):
            ui_files.append(os.path.join(ui_dir, file))


for ui_file in ui_files:
    py_file = f"{ui_file[:-3]}.py"
    subprocess.run(["uv", "run", "pyside6-uic", ui_file, "-o", py_file])
    add_type_ignore_comments(py_file)
