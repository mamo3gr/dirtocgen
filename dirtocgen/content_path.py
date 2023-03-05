import re
from pathlib import Path


class TitleNotFoundError(Exception):
    """Failed to find title of the file"""


class ContentPath:
    def __init__(self, path: str | Path):
        if isinstance(path, str):
            path = Path(path)
        self.path = path

    def is_hidden(self) -> bool:
        return any(p.startswith(".") for p in self.path.parts)

    def doc_path(self) -> Path:
        if self.path.is_dir():
            path = self.path / "README.md"
        else:
            path = self.path

        return path

    def title(self) -> str:
        path = self.doc_path()
        return self._get_header(path)

    @staticmethod
    def _get_header(file: Path):
        with open(file, "r") as f:
            header = f.readline()
            pattern = r"#+\s+(.*)"
            result = re.match(pattern, header)
            if result is None:
                raise TitleNotFoundError
            return result.group(1)

    def depth_from(self, directory: str | Path):
        try:
            relative_path = self.path.relative_to(directory)
            return len(relative_path.parents)
        except ValueError as e:
            raise e

    def generate_toc(self) -> str:
        if not self.path.is_dir():
            raise ValueError(f"{self.path} is not a directory")

        root_dir = self.path
        toc = ""

        for path in sorted(root_dir.glob("**/*")):
            if path.is_file():
                if path.suffix != ".md" or path.name == "README.md":
                    continue

            c = ContentPath(path)
            try:
                title = c.title()
            except (FileNotFoundError, TitleNotFoundError):
                title = path.stem
            depth = c.depth_from(root_dir)

            indent = "".join([" " * (depth - 1) * 2])
            toc_line = f"{indent}* [{title}]({path.relative_to(root_dir)})\n"
            toc += toc_line

        return toc

    def create_index_doc(self):
        if not self.path.is_dir():
            raise ValueError(f"{self.path} is not a directory")

        index_doc = self.path / "README.md"
        index_doc.touch()

    def insert_toc(self):
        path = self.doc_path()
        self._insert_toc(path)

    def _insert_toc(self, path):
        with open(path, "r") as f:
            lines = f.readlines()

        lines.insert(1, "\n")
        lines.insert(2, "[//]: # (dirtocgen start)\n")
        lines.insert(3, "\n")
        lines.insert(4, self.generate_toc())
        lines.insert(5, "\n")
        lines.insert(6, "[//]: # (dirtocgen end)\n")

        with open(path, "w") as f:
            f.writelines(lines)
