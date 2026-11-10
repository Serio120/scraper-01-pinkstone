from unittest.mock import Mock

import pandas as pd
import pytest
import requests

import main as scraper


HTML = """
<div class="quote">
  <span class="text">“A quote.”</span>
  <span><small class="author">An Author</small></span>
  <div class="tags">
    <a class="tag">life</a>
    <a class="tag">inspiration</a>
  </div>
</div>
"""


def response_with(content):
    response = Mock()
    response.content = content.encode("utf-8")
    response.raise_for_status.return_value = None
    return response


def test_scrape_page_extracts_quote_author_and_tags(monkeypatch):
    get = Mock(return_value=response_with(HTML))
    monkeypatch.setattr(scraper.requests, "get", get)

    result = scraper.scrape_page("https://example.test/page/1/", timeout=4)

    assert result == [
        {"Cita": "“A quote.”", "Autor": "An Author", "Etiquetas": "life, inspiration"}
    ]
    get.assert_called_once_with("https://example.test/page/1/", timeout=4)


def test_scrape_page_allows_missing_tags(monkeypatch):
    html = """
    <div class="quote">
      <span class="text">A quote without tags.</span>
      <small class="author">An Author</small>
    </div>
    """
    monkeypatch.setattr(scraper.requests, "get", Mock(return_value=response_with(html)))

    assert scraper.scrape_page("https://example.test/") == [
        {"Cita": "A quote without tags.", "Autor": "An Author", "Etiquetas": ""}
    ]


def test_scrape_page_skips_incomplete_quote(monkeypatch):
    html = '<div class="quote"><span class="text">Missing author</span></div>'
    monkeypatch.setattr(scraper.requests, "get", Mock(return_value=response_with(html)))

    assert scraper.scrape_page("https://example.test/") == []


def test_scrape_page_returns_empty_list_on_request_error(monkeypatch):
    get = Mock(side_effect=requests.exceptions.Timeout("request timed out"))
    monkeypatch.setattr(scraper.requests, "get", get)

    assert scraper.scrape_page("https://example.test/") == []


def test_save_to_excel_writes_expected_columns(tmp_path):
    output = tmp_path / "nested" / "quotes.xlsx"
    data = [{"Cita": "A quote", "Autor": "An Author", "Etiquetas": "life"}]

    assert scraper.save_to_excel(data, output) is True
    saved = pd.read_excel(output)
    assert list(saved.columns) == ["Cita", "Autor", "Etiquetas"]
    assert saved.iloc[0]["Autor"] == "An Author"


def test_save_to_excel_does_not_create_file_for_empty_data(tmp_path):
    output = tmp_path / "empty.xlsx"

    assert scraper.save_to_excel([], output) is False
    assert not output.exists()


def test_main_scrapes_all_requested_pages(monkeypatch, tmp_path):
    monkeypatch.setattr(scraper, "configure_logging", lambda: None)
    seen_urls = []

    def fake_scrape(url, timeout):
        seen_urls.append(url)
        return [{"Cita": url, "Autor": "Author", "Etiquetas": ""}]

    saved = {}
    monkeypatch.setattr(scraper, "scrape_page", fake_scrape)
    monkeypatch.setattr(
        scraper, "save_to_excel", lambda data, filename: saved.update(data=data, filename=filename)
    )

    count = scraper.main(
        base_url="https://example.test/",
        pages=3,
        output_file=tmp_path / "quotes.xlsx",
        max_workers=2,
        timeout=3,
    )

    assert count == 3
    assert set(seen_urls) == {
        "https://example.test/page/1/",
        "https://example.test/page/2/",
        "https://example.test/page/3/",
    }
    assert len(saved["data"]) == 3


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"pages": 0}, "pages"),
        ({"max_workers": 0}, "max_workers"),
        ({"timeout": 0}, "timeout"),
    ],
)
def test_main_rejects_invalid_configuration(kwargs, message):
    with pytest.raises(ValueError, match=message):
        scraper.main(**kwargs)
