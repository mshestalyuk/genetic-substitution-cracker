import tempfile
import unittest
from pathlib import Path

from corpus import load_corpus, normalize, resolve_source, strip_boilerplate


class NormalizeTests(unittest.TestCase):
    def test_polish_diacritics_are_folded(self):
        self.assertEqual(normalize("Zażółć gęślą jaźń! ŁÓDŹ"), "zazolcgeslajaznlodz")

    def test_letters_only_by_default(self):
        self.assertEqual(normalize("Attack at dawn, 12:30!"), "attackatdawn")

    def test_keep_spaces_collapses_separators(self):
        self.assertEqual(normalize("  Hello,   world -- 42 ", keep_spaces=True), "hello world")


class BoilerplateTests(unittest.TestCase):
    def test_gutenberg_header_and_footer_removed(self):
        raw = (
            "License blah\n*** START OF THE PROJECT GUTENBERG EBOOK X ***\n"
            "Real text.\n*** END OF THE PROJECT GUTENBERG EBOOK X ***\nMore license"
        )
        self.assertEqual(strip_boilerplate(raw).strip(), "Real text.")

    def test_wolne_lektury_footer_removed(self):
        raw = "Adam Mickiewicz\n\nTekst utworu.\n\n-----\nTa lektura ... wolnelektury.pl ...\n"
        self.assertEqual(strip_boilerplate(raw).strip(), "Adam Mickiewicz\n\nTekst utworu.")

    def test_plain_text_unchanged(self):
        self.assertEqual(strip_boilerplate("no markers here"), "no markers here")


class LoadCorpusTests(unittest.TestCase):
    def test_loads_directory_of_txt_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            Path(tmp, "a.txt").write_text("Ala ma kota.", encoding="utf-8")
            Path(tmp, "b.txt").write_text("Kot ma Alę.", encoding="utf-8")
            Path(tmp, "ignored.md").write_text("skip me", encoding="utf-8")
            self.assertEqual(load_corpus([tmp]), "alamakotakotmaale")

    def test_missing_path_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_corpus(["/definitely/not/here"])

    def test_slug_resolves_to_wolne_lektury(self):
        self.assertEqual(
            resolve_source("pan-tadeusz"),
            "https://wolnelektury.pl/media/book/txt/pan-tadeusz.txt",
        )
        url = "https://www.gutenberg.org/ebooks/1342.txt.utf-8"
        self.assertEqual(resolve_source(url), url)


if __name__ == "__main__":
    unittest.main()
