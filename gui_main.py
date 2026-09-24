"""Entrypoint for SoloSystem Modern Desktop GUI."""

import sys
from pathlib import Path

# Ensure root directory is on sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import flet as ft
from ui.app_view import SoloSystemApp


def main(page: ft.Page) -> None:
    SoloSystemApp(page)


if __name__ == "__main__":
    ft.app(target=main)
