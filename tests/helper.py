from pathlib import Path


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
