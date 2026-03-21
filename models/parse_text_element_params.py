from dataclasses import dataclass
from bs4 import BeautifulSoup

@dataclass
class ParseTextElementParams:
    soup: BeautifulSoup
    class_name: str
    html_tag: str = "div"
    default_value: str = "Unknown"