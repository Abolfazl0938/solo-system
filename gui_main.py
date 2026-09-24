"""Entrypoint for SoloSystem Modern Desktop GUI."""

from pathlib import Path
import sys

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import flet as ft
from ui.app_view import SoloLevelingView


def main(page: ft.Page) -> None:
    page.window_width = 1080
    page.window_height = 680
    page.window_min_width = 900
    page.window_min_height = 600
    page.window_center()

    SoloLevelingView(page)


if __name__ == "__main__":
    ft.app(target=main)
