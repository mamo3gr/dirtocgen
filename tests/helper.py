import re
from pathlib import Path
from typing import IO


def directory2string(root_dir: str | Path):
    """
    Helper function, which converts directories and files' name and
    their contents into string.
    """
    root_dir = Path(root_dir)

    ret_str = ""
    for path in sorted(root_dir.glob("**/*")):
        header = "[DIRECTORY]" if path.is_dir() else "[FILE]"

        ret_str += f"{header} {path.relative_to(root_dir)}\n"

        if path.is_file():
            with open(path, "r") as f:
                ret_str += f.read()

    return ret_str


class BufferedFileWriter:
    def __init__(self):
        self.file: None | IO = None
        self.string: None | str = None

    def open(self, filename):
        if self.file:
            self.file.close()

        self.file = open(filename, "w")

    def append_line(self, string):
        if self.string is None:
            self.string = string
        else:
            self.string += f"\n{string}"

    def flush_and_close(self):
        if self.file is None:
            return

        self.file.write(self.string)
        self.string = None

        self.file.close()
        self.file = None


def string2directory(root_dir: str | Path, string: str):
    """
    Helper function, which creates files and directories
    with respect to given string.
    """
    root_dir = Path(root_dir)
    writer = BufferedFileWriter()

    for line in string.split("\n"):
        dir_operation = re.match(r"^\[DIRECTORY] (.*)$", line)
        if dir_operation:
            writer.flush_and_close()

            directory = root_dir / dir_operation.group(1)
            directory.mkdir()
            continue

        file_operation = re.match(r"^\[FILE] (.*)$", line)
        if file_operation:
            writer.flush_and_close()

            filename = root_dir / file_operation.group(1)
            writer.open(filename)
            continue

        writer.append_line(line)

    writer.flush_and_close()
