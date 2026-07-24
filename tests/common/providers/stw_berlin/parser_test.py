from pathlib import Path
from common.providers.stw_berlin.parser import parse_menu
import pytest

directory = Path("./tests/common/providers/stw_berlin/fixtures")

html = sorted([str(path) for path in directory.iterdir() if path.suffix == ".html"])
expected = sorted([str(path) for path in directory.iterdir() if path.suffix == ".py"])

fixture_table = list(zip(html, expected))

@pytest.mark.filterwarnings("ignore")
@pytest.mark.parametrize(
    ("html_path", "expected_path"),
    fixture_table
)
def test_parse_menu(html_path, expected_path):
    with open(html_path.__str__()) as file:
        html = file.read()
        menu = parse_menu(html)
        print(f"Menu: {menu}")

    with open(expected_path.__str__()) as file:
        expected = file.read()
        print(f"Expected: {expected}")

    assert str(menu) == str(expected)
