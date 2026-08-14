import flet as ft
from src.printer_app import PrinterApp

def main(page: ft.Page):
    PrinterApp(page)

if __name__ == "__main__":
    ft.app(target=main)
        