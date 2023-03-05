import os
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

from content_path import ContentPath, TitleNotFoundError, UpdateTocError


class TestContentPath(unittest.TestCase):
    def test_is_hidden(self):
        sut = ContentPath("/.my/hidden/file")
        self.assertTrue(sut.is_hidden())

    def test_title(self):
        with NamedTemporaryFile() as tmpf:
            with open(tmpf.name, "w") as f:
                f.writelines("# Title")

            sut = ContentPath(tmpf.name)
            self.assertEqual("Title", sut.title())

    def test_title_lower_level(self):
        with NamedTemporaryFile() as tmpf:
            with open(tmpf.name, "w") as f:
                f.writelines("## Lower level header is OK")

            sut = ContentPath(tmpf.name)
            self.assertEqual("Lower level header is OK", sut.title())

    def test_title_file_not_found(self):
        with NamedTemporaryFile() as tmpf:
            filename = tmpf.name
            # the temporary file is deleted here, that is, no more exists

        sut = ContentPath(filename)
        with self.assertRaises(FileNotFoundError):
            sut.title()

    def test_title_title_nof_found(self):
        with NamedTemporaryFile() as tmpf:
            with open(tmpf.name, "w") as f:
                f.writelines("This is a title that is not a markdown header")

            sut = ContentPath(tmpf.name)
            with self.assertRaises(TitleNotFoundError):
                sut.title()

    def test_title_for_directory(self):
        with TemporaryDirectory() as tmpd:
            index_doc = os.path.join(tmpd, "README.md")
            with open(index_doc, "w") as f:
                f.writelines(
                    "# Title of directory is that of README.md under the directory"
                )

            sut = ContentPath(tmpd)
            self.assertEqual(
                "Title of directory is that of README.md under the directory",
                sut.title(),
            )

    def test_title_for_directory_index_document_not_found(self):
        with TemporaryDirectory() as tmpd:
            sut = ContentPath(tmpd)
            with self.assertRaises(FileNotFoundError):
                sut.title()

    def test_depth_from_directory(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)
            sut = ContentPath(dir_name)
            self.assertEqual(1, sut.depth_from(tmpd))

    def test_depth_from_file(self):
        with TemporaryDirectory() as tmpd:
            doc_name = os.path.join(tmpd, "doc.md")
            open(doc_name, "w+").close()
            sut = ContentPath(doc_name)
            self.assertEqual(1, sut.depth_from(tmpd))

    def test_depth_from_itself(self):
        with TemporaryDirectory() as tmpd:
            sut = ContentPath(tmpd)
            self.assertEqual(0, sut.depth_from(tmpd))

    def test_depth_from_file_under_directory(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)

            doc_name = os.path.join(dir_name, "doc.md")
            open(doc_name, "w+").close()

            sut = ContentPath(doc_name)
            self.assertEqual(2, sut.depth_from(tmpd))

    def test_depth_from_failed(self):
        with TemporaryDirectory() as tmpd1, TemporaryDirectory() as tmpd2:
            sut = ContentPath(tmpd1)
            with self.assertRaises(ValueError):
                sut.depth_from(tmpd2)

    def test_generate_toc(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            index_doc_name = os.path.join(dir_name, "README.md")
            doc_name = os.path.join(dir_name, "doc.md")
            extra_doc_name = os.path.join(tmpd, "extra_doc.md")
            dummy_file_name = os.path.join(tmpd, "dummy.txt")

            os.mkdir(dir_name)

            with open(index_doc_name, "w") as f:
                f.writelines("# Directory 1")

            with open(doc_name, "w") as f:
                f.writelines("# Document")

            with open(extra_doc_name, "w") as f:
                f.writelines("# Extra document")

            with open(dummy_file_name, "w") as f:
                f.writelines("This file should not appear in the table of contents")

            expect = (
                "* [Directory 1](dir1)\n"
                "  * [Document](dir1/doc.md)\n"
                "* [Extra document](extra_doc.md)"
            )

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(expect, actual)

    def test_generate_toc_with_specifying_depth(self):
        with TemporaryDirectory() as tmpd:
            (Path(tmpd) / "dir1").mkdir()
            (Path(tmpd) / "dir1" / "dir11").mkdir()
            (Path(tmpd) / "doc1.md").open("w+").close()

            sut = ContentPath(tmpd)
            actual = sut.generate_toc(max_depth=1)
            expect = (
                "* [dir1](dir1)\n"
                # dir11 would not appear here because its depth is 2
                "* [doc1](doc1.md)"
            )
            self.assertEqual(expect, actual)

    def test_generate_toc_with_ignoring_hidden_file(self):
        with TemporaryDirectory() as tmpd:
            (Path(tmpd) / ".hidden_dir").mkdir()
            (Path(tmpd) / "dir1").mkdir()
            (Path(tmpd) / "dir1" / ".hidden_dir").mkdir()
            (Path(tmpd) / "dir1" / ".hidden_doc.md").open("w+").close()
            sut = ContentPath(tmpd)
            actual = sut.generate_toc()  # ignore_hidden=True by default
            expect = (
                "* [dir1](dir1)"
                # the others would not appear because they are hidden files/directories
            )
            self.assertEqual(expect, actual)

    def test_generate_toc_with_no_index_doc(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)

            # title should be the same as the directory name
            expect = "* [dir1](dir1)"

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(expect, actual)

    def test_generate_toc_index_doc_has_no_title(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            index_doc_name = os.path.join(dir_name, "README.md")

            os.mkdir(dir_name)
            open(index_doc_name, "w+").close()

            # title should be the same as the directory name
            expect = "* [dir1](dir1)"

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(expect, actual)

    def test_generate_toc_failed_to_get_title(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            doc_name = os.path.join(tmpd, "doc.md")

            os.mkdir(dir_name)
            open(doc_name, "w+").close()

            # fmt: off
            expect = (
                "* [dir1](dir1)\n"
                "* [doc](doc.md)"
            )
            # fmt: on

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(expect, actual)

    def test_generate_failed_with_not_directory(self):
        with NamedTemporaryFile() as tmpf:
            sut = ContentPath(tmpf.name)
            with self.assertRaises(ValueError):
                sut.generate_toc()

    def test_create_index_doc(self):
        with TemporaryDirectory() as tmpd:
            sut = ContentPath(tmpd)
            sut.create_index_doc()

            expect_path = os.path.join(tmpd, "README.md")
            self.assertTrue(os.path.exists(expect_path))
            with open(expect_path) as f:
                expect_title = os.path.basename(tmpd)
                expect_text = f"# {expect_title}\n"
                actual_text = f.read()
                self.assertEqual(expect_text, actual_text)

    def test_create_index_doc_failed_when_file_already_exists(self):
        with TemporaryDirectory() as tmpd:
            sut = ContentPath(tmpd)
            index_doc = os.path.join(tmpd, "README.md")
            open(index_doc, "w+").close()

            with self.assertRaises(FileExistsError):
                sut.create_index_doc()

    def test_create_index_doc_failed_with_file(self):
        with NamedTemporaryFile() as tmpf:
            sut = ContentPath(tmpf.name)

            with self.assertRaises(ValueError):
                sut.create_index_doc()

    def test_insert_toc(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)

            index_doc_name = os.path.join(tmpd, "README.md")
            with open(index_doc_name, "w") as f:
                # fmt: off
                index_doc_body = (
                    "# Document\n"
                    "\n"
                    "body\n"
                )
                # fmt: on
                f.write(index_doc_body)

            sut = ContentPath(tmpd)
            sut.insert_toc()

            expect_body = (
                "# Document\n"
                "\n"
                "[//]: # (dirtocgen start)\n"
                "\n"
                "* [dir1](dir1)\n"
                "\n"
                "[//]: # (dirtocgen end)\n"
                "\n"
                "body\n"
            )

            with open(index_doc_name, "r") as f:
                actual_body = f.read()

            self.assertEqual(expect_body, actual_body)

    def test_update_toc(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)

            index_doc_name = os.path.join(tmpd, "README.md")
            with open(index_doc_name, "w") as f:
                index_doc_body = (
                    "# Document\n"
                    "\n"
                    "[//]: # (dirtocgen start)\n"
                    "\n"
                    "This line would be updated (replaced with new toc)\n"
                    "\n"
                    "[//]: # (dirtocgen end)\n"
                    "\n"
                    "body\n"
                )
                f.write(index_doc_body)

            sut = ContentPath(tmpd)
            sut.update_toc()

            expect_body = (
                "# Document\n"
                "\n"
                "[//]: # (dirtocgen start)\n"
                "\n"
                "* [dir1](dir1)\n"
                "\n"
                "[//]: # (dirtocgen end)\n"
                "\n"
                "body\n"
            )

            with open(index_doc_name, "r") as f:
                actual_body = f.read()

            self.assertEqual(expect_body, actual_body)

    def test_update_toc_no_toc_found(self):
        with TemporaryDirectory() as tmpd:
            index_doc_name = os.path.join(tmpd, "README.md")
            open(index_doc_name, "w+").close()

            sut = ContentPath(tmpd)
            with self.assertRaises(UpdateTocError):
                sut.update_toc()
