import re
from pathlib import Path


class TitleNotFoundError(Exception):
    """Failed to find title of the file"""


class UpdateTocError(Exception):
    """Failed to update toc"""


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

    def generate_toc(self, max_depth: int | None = None, ignore_hidden=True) -> str:
        if not self.path.is_dir():
            raise ValueError(f"{self.path} is not a directory")

        root_dir = self.path
        toc_lines: list[str] = []

        for path in sorted(root_dir.glob("**/*")):
            if path.is_file():
                if path.suffix != ".md" or path.name == "README.md":
                    continue

            c = ContentPath(path)
            if ignore_hidden and c.is_hidden():
                continue

            depth = c.depth_from(root_dir)
            if max_depth and depth > max_depth:
                continue

            try:
                title = c.title()
            except (FileNotFoundError, TitleNotFoundError):
                title = path.stem

            indent = "".join([" " * (depth - 1) * 2])
            toc_line = f"{indent}* [{title}]({path.relative_to(root_dir)})"
            toc_lines.append(toc_line)

        return "\n".join(toc_lines)

    def create_index_doc(self):
        if not self.path.is_dir():
            raise ValueError(f"{self.path} is not a directory")

        index_doc = self.path / "README.md"
        index_doc.touch(exist_ok=False)
        with open(index_doc, "w") as f:
            title = self.path.name
            f.write(f"# {title}\n")

    def insert_toc(self, *args, **kwargs):
        path = self.doc_path()
        self._insert_toc(path, *args, **kwargs)

    def _insert_toc(self, path, *args, **kwargs):
        with open(path, "r") as f:
            lines = f.readlines()

        toc_text = self._generate_toc_text(*args, **kwargs)
        lines.insert(1, "\n" + toc_text + "\n")

        with open(path, "w") as f:
            f.writelines(lines)

    def _generate_toc_text(self, *args, **kwargs):
        return (
            f"[//]: # (dirtocgen start)\n"
            f"\n"
            f"{self.generate_toc(*args, **kwargs)}\n"
            f"\n"
            f"[//]: # (dirtocgen end)"
        )

    def update_toc(self, *args, **kwargs):
        path = self.doc_path()
        self._update_toc(path, *args, **kwargs)

    def _update_toc(self, path, *args, **kwargs):
        with open(path, "r") as f:
            text = f.read()

        toc_text = self._generate_toc_text(*args, **kwargs)
        pattern = r"\[//\]: # \(dirtocgen start\)[\s\S]+\[//\]: # \(dirtocgen end\)"
        text_updated, number_of_subs_made = re.subn(pattern, toc_text, text)
        if number_of_subs_made == 0:
            raise UpdateTocError

        with open(path, "w") as f:
            f.write(text_updated)

    def has_toc(self):
        path = self.doc_path()
        return self._has_toc(path)

    @staticmethod
    def _has_toc(path):
        with open(path, "r") as f:
            text = f.read()

        pattern = r"\[//\]: # \(dirtocgen start\)[\s\S]+\[//\]: # \(dirtocgen end\)"
        result = re.search(pattern, text)

        return result is not None
