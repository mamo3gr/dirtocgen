"""
update_root_toc_and_ignore_hidden_doc
input:
[FILE] .doc2.md
# Hidden document

This document would not appear in the table of contents
[FILE] README.md
# Root document

[//]: # (dirtocgen start)

This section would be replaced

[//]: # (dirtocgen end)

body
[FILE] doc1.md
# Document 1
expect:
[FILE] .doc2.md
# Hidden document

This document would not appear in the table of contents
[FILE] README.md
# Root document

[//]: # (dirtocgen start)

* [Document 1](doc1.md)

[//]: # (dirtocgen end)

body
[FILE] doc1.md
# Document 1
"""
from __future__ import annotations

import os
import unittest
from dataclasses import dataclass
from distutils.dir_util import copy_tree
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from typing import Callable

from usecase import insert_or_update_root_toc_and_create_or_update_children_index_docs

from tests.helper import directory2string, string2directory


@dataclass
class TestCase:
    name: str
    dir: str | Path
    sut: Callable


def _read_case(
    case_dir: str | Path, setup_file="setup.txt", expect_file="expect.txt"
) -> tuple[str, str]:
    case_dir = Path(case_dir)
    setup = _read_file(case_dir / setup_file)
    expect = _read_file(case_dir / expect_file)
    return setup, expect


def _read_file(file: str | Path):
    with open(file) as f:
        return f.read()


# class TestUsecase(unittest.TestCase):
#     maxDiff = None
#     case_dir_and_sut = [
#         TestCase(
#             "insert_root_toc_and_create_child_index_doc",
#             "./tests/cases/insert_root_toc_and_create_child_index_doc",
#             insert_or_update_root_toc_and_create_or_update_children_index_docs,
#         ),
#         TestCase(
#             "update_root_toc_and_ignore_hidden_doc",
#             "./tests/cases/update_root_toc",
#             insert_or_update_root_toc_and_create_or_update_children_index_docs,
#         ),
#     ]
#
#     def test_nominal(self):
#         for case in self.case_dir_and_sut:
#             input_dir = os.path.join(case.dir, "input")
#             expect_dir = os.path.join(case.dir, "expect")
#             sut = case.sut
#
#             with self.subTest(
#                 case.name, input_dir=input_dir, expect_dir=expect_dir, sut=sut
#             ):
#                 with TemporaryDirectory() as tmpd:
#                     copy_tree(input_dir, tmpd)
#                     sut(tmpd)
#                     self.assertEqual(
#                         directory2string(expect_dir),
#                         directory2string(tmpd),
#                     )
#
#     def test_insert_root_toc(self):
#         setup, expect = _read_case("tests/cases/insert_root_toc")
#         with TemporaryDirectory() as tmpd:
#             string2directory(tmpd, setup)
#             insert_or_update_root_toc_and_create_or_update_children_index_docs(tmpd)
#             actual = directory2string(tmpd)
#             self.assertEqual(expect, actual)
