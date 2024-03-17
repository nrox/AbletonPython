import inspect
import time

from utils import browser
from utils.browser import parse_items
from . import client  # type: ignore


def test_parse_items():
    items_str = "[[(0, 'Analog', [(8, 'Strings', [(0, 'M Tron Strings.adg'), (1, 'Off World Strings.adg'), (2, 'Synthetic Choir Strings.adg')])])]]"
    assert parse_items(items_str) == [
        ['Analog', 'Strings', 'M Tron Strings.adg'],
        ['Analog', 'Strings', 'Off World Strings.adg'],
        ['Analog', 'Strings', 'Synthetic Choir Strings.adg']
    ]


def test_get_folder(client):
    code = inspect.getsource(browser.get_folder)
    folders = ["'Analog'", "'Strings'"]
    code = code + "\n" + f"get_folder(Live, result, 'instruments', {','.join(folders)})"
    rv = client.query("/live/exec", (code,), timeout=2)
    assert 'Strings' in str(rv)
    print(rv)


def test_get_preview(client):
    code = inspect.getsource(browser.get_preview)
    folders = ["'Analog'", "'Strings'", "'Off World Strings.adg'"]
    code = code + "\n" + f"get_preview(Live, result, 'instruments', {','.join(folders)})"
    rv = client.query("/live/exec", (code,), timeout=2)
    assert 'Off World Strings.adg' in str(rv)


def test_list_and_preview(client):
    code = inspect.getsource(browser.get_folder)
    folders = ["'Analog'", "'Strings'"]
    code = code + "\n" + f"get_folder(Live, result, 'instruments', {','.join(folders)})"
    items_str, _ = client.query("/live/exec", (code,), timeout=3)
    items = parse_items(items_str)
    for i in items:
        browser.preview(client, i)
        time.sleep(3)
