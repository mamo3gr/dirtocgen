import os.path
from pathlib import Path
from tempfile import TemporaryDirectory
from textwrap import dedent
from unittest import TestCase

from tests.helper import directory2string, string2directory


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


class TestString2directory(TestCase):
    def test_directory(self):
        with TemporaryDirectory() as tmpd:
            string = dedent(
                """\
                [DIRECTORY] my_dir
                """
            ).strip("\n")
            string2directory(tmpd, string)

            _tmpd = Path(tmpd)
            self.assertTrue((_tmpd / "my_dir").is_dir())

    def test_emptyfile(self):
        with TemporaryDirectory() as tmpd:
            string = dedent(
                """\
                [FILE] doc.md
                """
            )
            string2directory(tmpd, string)

            with open(os.path.join(tmpd, "doc.md")) as f:
                content_actual = f.read()
                content_expect = ""
                self.assertEqual(content_expect, content_actual)

    def test_file(self):
        with TemporaryDirectory() as tmpd:
            string = dedent(
                """\
                [FILE] doc.md
                # Title

                body"""
            )
            string2directory(tmpd, string)

            with open(os.path.join(tmpd, "doc.md")) as f:
                content_actual = f.read()
                content_expect = dedent(
                    """\
                    # Title

                    body"""
                )
                self.assertEqual(content_expect, content_actual)

    def test_multiple_files(self):
        with TemporaryDirectory() as tmpd:
            string = dedent(
                """\
                [FILE] doc1.md
                # Title1

                body1
                [FILE] doc2.md
                # Title2

                body2"""
            )
            string2directory(tmpd, string)

            with open(os.path.join(tmpd, "doc1.md")) as f:
                content_actual = f.read()
                content_expect = dedent(
                    """\
                    # Title1

                    body1"""
                )
                self.assertEqual(content_expect, content_actual)

            with open(os.path.join(tmpd, "doc2.md")) as f:
                content_actual = f.read()
                content_expect = dedent(
                    """\
                    # Title2

                    body2"""
                )
                self.assertEqual(content_expect, content_actual)

    def test_nested_file(self):
        with TemporaryDirectory() as tmpd:
            string = dedent(
                """\
                [DIRECTORY] foo
                [DIRECTORY] foo/bar
                [FILE] foo/bar/baz.md
                """
            )
            string2directory(tmpd, string)

            _tmpd = Path(tmpd)
            self.assertTrue((_tmpd / "foo").is_dir())
            self.assertTrue((_tmpd / "foo" / "bar").is_dir())
            self.assertTrue((_tmpd / "foo" / "bar" / "baz.md").exists())
