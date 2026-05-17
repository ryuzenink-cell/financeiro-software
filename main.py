import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

from app.database.schema import create_tables
from app.ui.main_window import MainWindow


def aplicar_tema_claro(app):
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#111827"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f9fafb"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#111827"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#111827"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#dbeafe"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#111827"))

    app.setPalette(palette)

    app.setStyleSheet("""
        QMainWindow {
            background-color: #ffffff;
        }

        QWidget {
            background-color: #ffffff;
            color: #111827;
        }

        QStatusBar {
            background-color: #ffffff;
            color: #111827;
            border-top: 1px solid #e5e7eb;
        }

        QMenu {
            background-color: #ffffff;
            color: #111827;
            border: 1px solid #d1d5db;
        }

        QMenu::item:selected {
            background-color: #e5e7eb;
            color: #111827;
        }
    """)


def main():
    create_tables()

    app = QApplication(sys.argv)
    aplicar_tema_claro(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()