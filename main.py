#!/usr/bin/env python3
# text_editor.py
# Simple Text Editor using PyQt6
# Features: New, Open, Save, Save As, Undo/Redo, Cut/Copy/Paste, About, Confirm on close

import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QFileDialog,
    QMessageBox, QStatusBar
)
from PyQt6.QtGui import QAction, QIcon, QKeySequence

from PyQt6.QtGui import QIcon, QKeySequence
from PyQt6.QtCore import Qt

APP_NAME = "SabrinaEdit"
APP_VERSION = "1.0"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_path: Path | None = None
        self.is_modified = False

        self.setWindowTitle(f"{APP_NAME} - Untitled")
        self.resize(800, 600)

        # Central widget: text editor
        self.editor = QTextEdit()
        self.setCentralWidget(self.editor)
        self.editor.textChanged.connect(self.on_text_changed)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.update_status("Ready")

        # Create actions and menu
        self.create_actions()
        self.create_menus()
        self.create_shortcuts()

        # Window icon (if bundled with icon file, PyInstaller will include it)
        try:
            self.setWindowIcon(QIcon("app.ico"))
        except Exception:
            pass

    def create_actions(self):
        # File actions
        self.new_action = QAction("&New", self)
        self.new_action.triggered.connect(self.file_new)

        self.open_action = QAction("&Open...", self)
        self.open_action.triggered.connect(self.file_open)

        self.save_action = QAction("&Save", self)
        self.save_action.triggered.connect(self.file_save)

        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.triggered.connect(self.file_save_as)

        self.exit_action = QAction("E&xit", self)
        self.exit_action.triggered.connect(self.close)

        # Edit actions
        self.undo_action = QAction("&Undo", self)
        self.undo_action.triggered.connect(self.editor.undo)

        self.redo_action = QAction("&Redo", self)
        self.redo_action.triggered.connect(self.editor.redo)

        self.cut_action = QAction("Cu&t", self)
        self.cut_action.triggered.connect(self.editor.cut)

        self.copy_action = QAction("&Copy", self)
        self.copy_action.triggered.connect(self.editor.copy)

        self.paste_action = QAction("&Paste", self)
        self.paste_action.triggered.connect(self.editor.paste)

        # Help
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.show_about)

    def create_menus(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")
        help_menu.addAction(self.about_action)

    def create_shortcuts(self):
        self.new_action.setShortcut(QKeySequence.StandardKey.New)
        self.open_action.setShortcut(QKeySequence.StandardKey.Open)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)

        self.undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        self.redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        self.cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        self.copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        self.paste_action.setShortcut(QKeySequence.StandardKey.Paste)

        self.about_action.setShortcut(QKeySequence("F1"))

    # File operations
    def file_new(self):
        if self.maybe_save():
            self.editor.clear()
            self.current_path = None
            self.is_modified = False
            self.setWindowTitle(f"{APP_NAME} - Untitled")
            self.update_status("New file")

    def file_open(self):
        if not self.maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                self.editor.setPlainText(text)
                self.current_path = Path(path)
                self.is_modified = False
                self.setWindowTitle(f"{APP_NAME} - {self.current_path.name}")
                self.update_status(f"Opened {self.current_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not open file:\n{e}")

    def file_save(self):
        if self.current_path:
            return self._save_to_path(self.current_path)
        else:
            return self.file_save_as()

    def file_save_as(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt);;All Files (*)")
        if path:
            return self._save_to_path(Path(path))
        return False

    def _save_to_path(self, path: Path):
        try:
            text = self.editor.toPlainText()
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.current_path = path
            self.is_modified = False
            self.setWindowTitle(f"{APP_NAME} - {self.current_path.name}")
            self.update_status(f"Saved {self.current_path}")
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file:\n{e}")
            return False

    # Helpers
    def maybe_save(self) -> bool:
        if not self.is_modified:
            return True
        ret = QMessageBox.question(
            self,
            "Unsaved Changes",
            "This document has unsaved changes. Save now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
        )
        if ret == QMessageBox.StandardButton.Yes:
            return self.file_save()
        elif ret == QMessageBox.StandardButton.No:
            return True
        else:
            return False

    def on_text_changed(self):
        if not self.is_modified:
            self.is_modified = True
            title = self.windowTitle()
            if not title.startswith("*"):
                self.setWindowTitle("*" + title)

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    def show_about(self):
        QMessageBox.information(self, f"About {APP_NAME}",
                                f"{APP_NAME} Version {APP_VERSION}\n\nSimple text editor built with PyQt6.")

    def update_status(self, message: str):
        self.status.showMessage(message, 5000)  # show for 5s


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
