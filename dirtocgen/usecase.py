from logging import INFO, basicConfig, getLogger
from pathlib import Path

from dirtocgen.content_path import ContentPath

logger = getLogger(__name__)
basicConfig(level=INFO)


def insert_or_update_root_toc_and_create_or_update_children_index_docs(
    root_dir: str | Path, root_toc_max_depth=1, toc_max_depth=1
):
    root_dir = Path(root_dir)
    root = ContentPath(root_dir)
    _insert_or_update_toc(root, max_depth=root_toc_max_depth)

    for path in root_dir.glob("**/*"):
        if not path.is_dir():
            continue

        c = ContentPath(path)
        if c.is_hidden():
            continue

        if not c.doc_path().exists():
            c.create_index_doc()
            logger.info(f"create index doc: {c.doc_path()}")

        _insert_or_update_toc(c, max_depth=toc_max_depth)


def _insert_or_update_toc(c: ContentPath, *args, **kwargs):
    if c.has_toc():
        c.update_toc(*args, **kwargs)
        logger.info(f"update toc: {c.path}")
    else:
        c.insert_toc(*args, **kwargs)
        logger.info(f"insert toc: {c.path}")
