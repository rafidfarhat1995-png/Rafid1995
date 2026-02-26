"""
Tests for scraper.py — uses mocking so no real network calls are needed.
Run with: python -m pytest test_scraper.py -v
"""

import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from scraper import fetch_page, parse_quotes, get_next_page, scrape


SAMPLE_HTML = """
<html><body>
  <div class="quote">
    <span class="text">\u201cLife is short.\u201d</span>
    <small class="author">Jane Doe</small>
    <a class="tag">life</a>
    <a class="tag">short</a>
  </div>
  <div class="quote">
    <span class="text">\u201cCode every day.\u201d</span>
    <small class="author">John Smith</small>
    <a class="tag">coding</a>
  </div>
  <ul class="pager">
    <li class="next"><a href="/page/2/">Next</a></li>
  </ul>
</body></html>
"""

SAMPLE_HTML_LAST_PAGE = """
<html><body>
  <div class="quote">
    <span class="text">\u201cThe end.\u201d</span>
    <small class="author">Someone</small>
  </div>
</body></html>
"""


class TestParseQuotes(unittest.TestCase):
    def setUp(self):
        self.soup = BeautifulSoup(SAMPLE_HTML, "html.parser")

    def test_returns_correct_count(self):
        quotes = parse_quotes(self.soup)
        self.assertEqual(len(quotes), 2)

    def test_quote_fields_present(self):
        quotes = parse_quotes(self.soup)
        for q in quotes:
            self.assertIn("text", q)
            self.assertIn("author", q)
            self.assertIn("tags", q)

    def test_first_quote_content(self):
        quotes = parse_quotes(self.soup)
        self.assertIn("Life is short", quotes[0]["text"])
        self.assertEqual(quotes[0]["author"], "Jane Doe")
        self.assertEqual(quotes[0]["tags"], ["life", "short"])

    def test_tags_as_list(self):
        quotes = parse_quotes(self.soup)
        self.assertIsInstance(quotes[1]["tags"], list)
        self.assertEqual(quotes[1]["tags"], ["coding"])


class TestGetNextPage(unittest.TestCase):
    def test_finds_next_page(self):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        url = get_next_page(soup)
        self.assertEqual(url, "http://quotes.toscrape.com/page/2/")

    def test_no_next_page(self):
        soup = BeautifulSoup(SAMPLE_HTML_LAST_PAGE, "html.parser")
        url = get_next_page(soup)
        self.assertIsNone(url)


class TestFetchPage(unittest.TestCase):
    @patch("scraper.requests.get")
    def test_successful_fetch(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = SAMPLE_HTML
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        soup = fetch_page("http://quotes.toscrape.com")
        self.assertIsNotNone(soup)
        self.assertEqual(len(parse_quotes(soup)), 2)

    @patch("scraper.requests.get")
    def test_network_error_returns_none(self, mock_get):
        import requests
        mock_get.side_effect = requests.RequestException("connection error")
        result = fetch_page("http://quotes.toscrape.com")
        self.assertIsNone(result)


class TestScrape(unittest.TestCase):
    @patch("scraper.fetch_page")
    def test_respects_max_pages(self, mock_fetch):
        soup = BeautifulSoup(SAMPLE_HTML, "html.parser")
        mock_fetch.return_value = soup

        results = scrape(max_pages=2)
        self.assertEqual(mock_fetch.call_count, 2)
        self.assertEqual(len(results), 4)  # 2 quotes x 2 pages

    @patch("scraper.fetch_page")
    def test_stops_when_no_next_page(self, mock_fetch):
        soup_last = BeautifulSoup(SAMPLE_HTML_LAST_PAGE, "html.parser")
        mock_fetch.return_value = soup_last

        results = scrape(max_pages=10)
        self.assertEqual(mock_fetch.call_count, 1)
        self.assertEqual(len(results), 1)

    @patch("scraper.fetch_page")
    def test_handles_fetch_failure(self, mock_fetch):
        mock_fetch.return_value = None
        results = scrape(max_pages=3)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
