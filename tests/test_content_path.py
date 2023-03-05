import os
import unittest
from tempfile import NamedTemporaryFile, TemporaryDirectory

from content_path import ContentPath, TitleNotFoundError


class TestContentPath(unittest.TestCase):
    def test_is_hidden(self):
        sut = ContentPath("/.my/hidden/file")
        self.assertTrue(sut.is_hidden())

    def test_title(self):
        with NamedTemporaryFile() as tmpf:
            with open(tmpf.name, "w") as f:
                f.writelines("# Title")

            sut = ContentPath(tmpf.name)
            self.assertEqual(sut.title(), "Title")

    def test_title_lower_level(self):
        with NamedTemporaryFile() as tmpf:
            with open(tmpf.name, "w") as f:
                f.writelines("## Lower level header is OK")

            sut = ContentPath(tmpf.name)
            self.assertEqual(sut.title(), "Lower level header is OK")

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
                sut.title(),
                "Title of directory is that of README.md under the directory",
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
            self.assertEqual(sut.depth_from(tmpd), 1)

    def test_depth_from_file(self):
        with TemporaryDirectory() as tmpd:
            doc_name = os.path.join(tmpd, "doc.md")
            open(doc_name, "w+").close()
            sut = ContentPath(doc_name)
            self.assertEqual(sut.depth_from(tmpd), 1)

    def test_depth_from_itself(self):
        with TemporaryDirectory() as tmpd:
            sut = ContentPath(tmpd)
            self.assertEqual(sut.depth_from(tmpd), 0)

    def test_depth_from_file_under_directory(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)

            doc_name = os.path.join(dir_name, "doc.md")
            open(doc_name, "w+").close()

            sut = ContentPath(doc_name)
            self.assertEqual(sut.depth_from(tmpd), 2)

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

            # fmt: off
            expect = "* [Directory 1](dir1)\n" \
                     "  * [Document](dir1/doc.md)\n" \
                     "* [Extra document](extra_doc.md)\n"
            # fmt: on

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(actual, expect)

    def test_generate_toc_with_no_index_doc(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            os.mkdir(dir_name)

            # title should be the same as the directory name
            expect = "* [dir1](dir1)\n"

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(actual, expect)

    def test_generate_toc_index_doc_has_no_title(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            index_doc_name = os.path.join(dir_name, "README.md")

            os.mkdir(dir_name)
            open(index_doc_name, "w+").close()

            # title should be the same as the directory name
            expect = "* [dir1](dir1)\n"

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(actual, expect)

    def test_generate_toc_failed_to_get_title(self):
        with TemporaryDirectory() as tmpd:
            dir_name = os.path.join(tmpd, "dir1")
            doc_name = os.path.join(tmpd, "doc.md")

            os.mkdir(dir_name)
            open(doc_name, "w+").close()

            # fmt: off
            expect = "* [dir1](dir1)\n" \
                     "* [doc](doc.md)\n"
            # fmt: on

            sut = ContentPath(tmpd)
            actual = sut.generate_toc()
            self.assertEqual(actual, expect)

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
                index_doc_body = "# Document\n" \
                                 "\n" \
                                 "body\n"
                # fmt: on
                f.write(index_doc_body)

            sut = ContentPath(tmpd)
            sut.insert_toc()

            # fmt: off
            expect_body = "# Document\n" \
                          "\n" \
                          "[//]: # (dirtocgen start)\n" \
                          "\n" \
                          "* [dir1](dir1)\n" \
                          "\n" \
                          "[//]: # (dirtocgen end)\n" \
                          "\n" \
                          "body\n"
            # fmt: on

            with open(index_doc_name, "r") as f:
                actual_body = f.read()

            self.assertEqual(expect_body, actual_body)
