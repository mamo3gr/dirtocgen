import os
import unittest
from dataclasses import dataclass
from distutils.dir_util import copy_tree
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Callable

from usecase import insert_or_update_root_toc_and_create_or_update_children_index_docs


@dataclass
class TestCase:
    name: str
    dir: str | Path
    sut: Callable


class TestUsecase(unittest.TestCase):
    maxDiff = None
    case_dir_and_sut = [
        TestCase(
            "insert_root_toc_and_create_child_index_doc",
            "./tests/cases/insert_root_toc_and_create_child_index_doc",
            insert_or_update_root_toc_and_create_or_update_children_index_docs,
        ),
        TestCase(
            "update_root_toc_and_ignore_hidden_doc",
            "./tests/cases/update_root_toc",
            insert_or_update_root_toc_and_create_or_update_children_index_docs,
        ),
    ]

    def test_nominal(self):
        for case in self.case_dir_and_sut:
            input_dir = os.path.join(case.dir, "input")
            expect_dir = os.path.join(case.dir, "expect")
            sut = case.sut

            with self.subTest(
                case.name, input_dir=input_dir, expect_dir=expect_dir, sut=sut
            ):
                with TemporaryDirectory() as tmpd:
                    copy_tree(input_dir, tmpd)
                    sut(tmpd)
                    self.assertEqual(
                        directory2string(expect_dir),
                        directory2string(tmpd),
                    )


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

        ret_str += "\n"

    return ret_str
