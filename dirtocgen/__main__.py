import argparse

from dirtocgen.usecase import (
    insert_or_update_root_toc_and_create_or_update_children_index_docs,
)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="root directory")
    parser.add_argument(
        "--root_toc_max_depth",
        type=int,
        help="maximum depth of toc (table of contents) in the root directory",
    )
    parser.add_argument(
        "--toc_max_depth",
        type=int,
        help="maximum depth of toc (table of contents) in each directory",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    insert_or_update_root_toc_and_create_or_update_children_index_docs(
        args.path, args.root_toc_max_depth, args.toc_max_depth
    )
