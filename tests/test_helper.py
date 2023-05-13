import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from tests.helper import directory2string


class TestDirectory2string(TestCase):
    def test_emptyfile(self):
        with TemporaryDirectory() as tmpd:
            filename = os.path.join(tmpd, "file.md")
            Path(filename).touch()

            expect = dedent(
                """\
                [FILE] file.md
                """
            )
            self.assertEqual(expect, directory2string(tmpd))

    def test_file(self):
        with TemporaryDirectory() as tmpd:
            filename = os.path.join(tmpd, "file.md")
            with open(filename, "w") as f:
                content = dedent(
                    """\
                    # Title

                    body
                    """
                )
                f.write(content)

            expect = dedent(
                """\
                [FILE] file.md
                # Title

                body
                """
            )
            self.assertEqual(expect, directory2string(tmpd))

    def test_directory(self):
        with TemporaryDirectory() as tmpd:
            dirname = os.path.join(tmpd, "my_dir")
            Path(dirname).mkdir()

            expect = dedent(
                """\
                [DIRECTORY] my_dir
                """
            )
            self.assertEqual(expect, directory2string(tmpd))

    def test_files_and_directories_should_be_ordered(self):
        with TemporaryDirectory() as tmpd:
            root_dir = Path(tmpd)
            (root_dir / "b.txt").touch()
            (root_dir / "c").mkdir()
            (root_dir / "c" / "a.txt").touch()

            expect = dedent(
                """\
                [FILE] b.txt
                [DIRECTORY] c
                [FILE] c/a.txt
                """
            )
            self.assertEqual(expect, directory2string(tmpd))
