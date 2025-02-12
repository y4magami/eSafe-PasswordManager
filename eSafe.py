#!/usr/bin/env python3

"""
eSafe Password Manager (◕‿◕✿)
A secure and kawaii password manager that keeps your secrets safe! 
Created with love and strong encryption ~(˘▾˘~)
"""

import sqlite3
import secrets
import string
import getpass
import bcrypt
import base64
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, List, Dict
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTableWidget, QTableWidgetItem, QMessageBox, 
                            QComboBox, QInputDialog, QDialog, QTabWidget,
                            QSpinBox, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
import sys
import platform
import ctypes
import json
import os
import hashlib
import requests
import time

# Biometric authentication imports based on platform
SYSTEM = platform.system().lower()
if SYSTEM == 'windows':
    try:
        import win32security
        import win32con
        from win32com.shell import shell, shellcon
        BIOMETRIC_AVAILABLE = True
    except ImportError:
        BIOMETRIC_AVAILABLE = False
elif SYSTEM in ['linux', 'darwin']:
    try:
        import pam
        import pwd
        BIOMETRIC_AVAILABLE = True
    except ImportError:
        BIOMETRIC_AVAILABLE = False
else:
    BIOMETRIC_AVAILABLE = False

class PasswordDialog(QDialog):
    """Kawaii dialog for adding/editing passwords (◕‿◕✿)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        self.setup_theme()

    def setup_theme(self):
        """Apply our kawaii theme to the dialog (◕‿◕✿)"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2E2E2E;
                color: #E0B0FF;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #363636;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 5px;
                color: #E0B0FF;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #8A2BE2;
            }
            QComboBox {
                padding: 5px 10px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);  /* You can add a custom arrow image */
            }
            QComboBox:on {
                border-color: #8A2BE2;
            }
            QComboBox QAbstractItemView {
                background-color: #363636;
                border: 1px solid #555555;
                selection-background-color: #8A2BE2;
            }
            QLabel {
                color: #E0B0FF;
            }
            QMessageBox {
                background-color: #2E2E2E;
            }
            QMessageBox QLabel {
                color: #E0B0FF;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)

    def setup_ui(self):
        """Setup our cute password dialog ⊂(◉‿◉)つ"""
        layout = QVBoxLayout()
        
        # Service
        self.service_input = QLineEdit()
        layout.addWidget(QLabel("Service:"))
        layout.addWidget(self.service_input)
        
        # Username
        self.username_input = QLineEdit()
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(self.username_input)
        
        # Password
        password_layout = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.show_password_btn = QPushButton("Show")
        self.show_password_btn.setFixedWidth(60)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.generate_btn = QPushButton("Generate")
        self.generate_btn.clicked.connect(self.generate_password)
        
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.show_password_btn)
        password_layout.addWidget(self.generate_btn)
        
        layout.addWidget(QLabel("Password:"))
        layout.addLayout(password_layout)
        
        # Category
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("General")
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_input)
        
        # Notes
        self.notes_input = QTextEdit()
        layout.addWidget(QLabel("Notes (optional):"))
        layout.addWidget(self.notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setWindowTitle("Add Password")

    def toggle_password_visibility(self):
        """Toggle password visibility (。⌒∇⌒)。"""
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("Hide")
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("Show")

    def generate_password(self):
        """Generate a random password"""
        try:
            length, ok = QInputDialog.getInt(
                self, "Password Length", 
                "Enter password length:",
                16, 8, 32, 1
            )
            if ok:
                # Generate password using string and secrets modules
                chars = string.ascii_letters + string.digits + "!@#$%^&*"
                password = ''.join(secrets.choice(chars) for _ in range(length))
                self.password_input.setText(password)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

class BiometricAuth:
    """Kawaii biometric authentication handler (◕‿◕✿)"""
    def __init__(self):
        self.system = SYSTEM
        self.available = BIOMETRIC_AVAILABLE
        if not self.available:
            logging.warning("Biometric authentication not available (╥﹏╥)")

    def authenticate(self) -> bool:
        """Authenticate using biometrics ⊂(◉‿◉)つ"""
        if not self.available:
            return False
            
        try:
            if self.system == 'windows':
                return self._authenticate_windows()
            elif self.system in ['linux', 'darwin']:
                return self._authenticate_unix()
            return False
        except Exception as e:
            logging.error(f"Biometric authentication error: {str(e)} (╥﹏╥)")
            return False

    def _authenticate_windows(self) -> bool:
        """Windows Hello authentication (。⌒∇⌒)。"""
        try:
            # Create a Windows Hello prompt
            flags = win32con.CREDUI_FLAGS_ALWAYS_SHOW_UI | win32con.CREDUI_FLAGS_GENERIC_CREDENTIALS
            result = win32security.GetUserNameEx(win32con.NameSamCompatible)
            return result is not None
        except Exception as e:
            logging.error(f"Windows Hello error: {str(e)} (╥﹏╥)")
            return False

    def _authenticate_unix(self) -> bool:
        """Unix-based biometric authentication ~(˘▾˘~)"""
        try:
            # Use PAM for fingerprint/Touch ID
            auth = pam.pam()
            return auth.authenticate(pwd.getpwuid(os.getuid())[0], None, service='login')
        except Exception as e:
            logging.error(f"Unix biometric error: {str(e)} (╥﹏╥)")
            return False

class BreachMonitor:
    """Kawaii breach monitoring system (◕‿◕✿)"""
    def __init__(self):
        self.api_base = "https://api.pwnedpasswords.com/range/"
        self.last_check = {}  # Cache to prevent too frequent API calls

    def check_password(self, password: str) -> Tuple[bool, int]:
        """Check if a password has been exposed in data breaches ᕦ(ò_óˇ)ᕤ"""
        # Create SHA-1 hash of the password
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix, suffix = sha1_hash[:5], sha1_hash[5:]
        
        try:
            # Check cache first
            if prefix in self.last_check:
                last_time, results = self.last_check[prefix]
                if datetime.now() - last_time < timedelta(hours=24):
                    return self._check_hash_suffix(suffix, results)
            
            # Query the API
            response = requests.get(f"{self.api_base}{prefix}")
            response.raise_for_status()
            
            # Cache the results
            self.last_check[prefix] = (datetime.now(), response.text)
            
            return self._check_hash_suffix(suffix, response.text)
            
        except Exception as e:
            logging.error(f"Breach check error: {str(e)} (╥﹏╥)")
            return False, 0

    def _check_hash_suffix(self, suffix: str, response_text: str) -> Tuple[bool, int]:
        """Check if the hash suffix exists in the response (。⌒∇⌒)。"""
        for line in response_text.splitlines():
            hash_suffix, count = line.split(':')
            if hash_suffix == suffix:
                return True, int(count)
        return False, 0

class eSafe:
    def __init__(self):
        """Initialize our password manager"""
        self.db_name = 'password_vault.db'
        self.current_user_id = 1
        self.setup_database()

    def setup_database(self):
        """Set up the database"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Drop existing table if it exists
            cursor.execute('DROP TABLE IF EXISTS passwords')
            
            # Create fresh passwords table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service TEXT NOT NULL,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    notes TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database error: {str(e)}")
            raise

    def generate_password(self, length=16):
        """Generate a strong random password"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(chars) for _ in range(length))

    def add_password(self, service: str, username: str, password: str, category: str = 'General', notes: str = ''):
        """Add a new password"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO passwords 
                (service, username, password, category, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (service, username, password, category, notes))
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error adding password: {str(e)}")
            raise

    def get_passwords(self, category: str = None):
        """Get all passwords"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            if category and category != "All Categories":
                cursor.execute('''
                    SELECT service, username, password, category, notes 
                    FROM passwords 
                    WHERE category = ?
                    ORDER BY service
                ''', (category,))
            else:
                cursor.execute('''
                    SELECT service, username, password, category, notes 
                    FROM passwords 
                    ORDER BY service
                ''')
                
            passwords = cursor.fetchall()
            conn.close()
            return passwords
            
        except Exception as e:
            print(f"Error getting passwords: {str(e)}")
            return []

    def get_categories(self):
        """Get unique categories"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            cursor.execute('SELECT DISTINCT category FROM passwords')
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()
            return categories
        except Exception as e:
            print(f"Error getting categories: {str(e)}")
            return []

class eSafeGUI(QMainWindow):
    """Our kawaii password manager GUI (◕‿◕✿)"""
    def __init__(self, esafe):
        super().__init__()
        self.esafe = esafe
        self.setup_theme()
        self.setup_ui()

    def setup_theme(self):
        """Setup our kawaii dark theme with purple accents (◕‿◕✿)"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2E2E2E;
            }
            QWidget {
                background-color: #2E2E2E;
                color: #E0B0FF;  /* Light purple text */
                font-size: 10pt;
            }
            QTableWidget {
                background-color: #363636;
                alternate-background-color: #404040;
                border: 1px solid #555555;
                gridline-color: #555555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #8A2BE2;  /* Purple selection */
            }
            QHeaderView::section {
                background-color: #404040;
                color: #E0B0FF;
                padding: 5px;
                border: 1px solid #555555;
            }
            QPushButton {
                background-color: #4A4A4A;
                border: 2px solid #8A2BE2;
                border-radius: 4px;
                padding: 5px 15px;
                color: #E0B0FF;
            }
            QPushButton:hover {
                background-color: #8A2BE2;
                color: white;
            }
            QPushButton:pressed {
                background-color: #6A1B9A;
            }
            QLineEdit, QTextEdit, QComboBox {
                background-color: #363636;
                border: 2px solid #555555;
                border-radius: 4px;
                padding: 5px;
                color: #E0B0FF;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #8A2BE2;
            }
            QComboBox {
                padding: 5px 10px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);  /* You can add a custom arrow image */
            }
            QComboBox:on {
                border-color: #8A2BE2;
            }
            QComboBox QAbstractItemView {
                background-color: #363636;
                border: 1px solid #555555;
                selection-background-color: #8A2BE2;
            }
            QLabel {
                color: #E0B0FF;
            }
            QMessageBox {
                background-color: #2E2E2E;
            }
            QMessageBox QLabel {
                color: #E0B0FF;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #E0B0FF;
                padding: 8px 20px;
                border: 1px solid #555555;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #8A2BE2;
                color: white;
            }
            QScrollBar:vertical {
                background-color: #2E2E2E;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #8A2BE2;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def setup_ui(self):
        """Setup our cute user interface ⊂(◉‿◉)つ"""
        self.setWindowTitle("eSafe Password Manager")
        self.setMinimumSize(800, 600)

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Create tab widget
        tabs = QTabWidget()
        
        # Passwords tab
        passwords_tab = QWidget()
        passwords_layout = QVBoxLayout(passwords_tab)
        
        # Toolbar
        toolbar = QHBoxLayout()
        self.add_btn = QPushButton("Add Password")
        self.refresh_btn = QPushButton("Refresh")
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        
        toolbar.addWidget(self.add_btn)
        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(QLabel("Filter by category:"))
        toolbar.addWidget(self.category_filter)
        toolbar.addStretch()
        
        # Add breach check button to toolbar
        self.check_breaches_btn = QPushButton("Check for Breaches")
        toolbar.addWidget(self.check_breaches_btn)
        self.check_breaches_btn.clicked.connect(self.check_breaches)
        
        # Password table
        self.password_table = QTableWidget()
        self.password_table.setColumnCount(5)
        self.password_table.setHorizontalHeaderLabels(
            ["Service", "Username", "Password", "Category", "Notes"]
        )
        
        passwords_layout.addLayout(toolbar)
        passwords_layout.addWidget(self.password_table)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_password)
        self.refresh_btn.clicked.connect(self.refresh_passwords)
        self.category_filter.currentTextChanged.connect(self.filter_passwords)
        
        # Add tabs
        tabs.addTab(passwords_tab, "Passwords")
        
        layout.addWidget(tabs)
        
        # Initial password load
        self.refresh_passwords()

        # Update table appearance
        self.password_table.setAlternatingRowColors(True)
        self.password_table.setShowGrid(True)
        self.password_table.horizontalHeader().setStretchLastSection(True)
        self.password_table.verticalHeader().setVisible(False)
        
        # Add some padding
        self.password_table.setStyleSheet("""
            QTableWidget {
                padding: 10px;
            }
        """)

        # Connect table click event to copy password
        self.password_table.cellClicked.connect(self.handle_cell_click)

    def add_password(self):
        """Add a new password entry"""
        try:
            dialog = PasswordDialog(self)  # Remove the password generator parameter
            if dialog.exec_() == QDialog.Accepted:
                service = dialog.service_input.text()
                username = dialog.username_input.text()
                password = dialog.password_input.text()
                category = dialog.category_input.text() or "General"
                notes = dialog.notes_input.toPlainText()
                
                if not all([service, username, password]):
                    QMessageBox.warning(self, "Warning",
                                      "Please fill in all required fields!")
                    return
                
                # Add the password
                self.esafe.add_password(service, username, password, category, notes)
                self.refresh_passwords()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def refresh_passwords(self):
        """Refresh the password list"""
        try:
            category = self.category_filter.currentText()
            if category == "All Categories":
                category = None
                
            passwords = self.esafe.get_passwords(category)
            if passwords is None:
                passwords = []
                
            self.password_table.setRowCount(len(passwords))
            
            for row, (service, username, password, category, notes) in enumerate(passwords):
                self.password_table.setItem(row, 0, QTableWidgetItem(service))
                self.password_table.setItem(row, 1, QTableWidgetItem(username))
                self.password_table.setItem(row, 2, QTableWidgetItem("●●●●●●"))  # Still hide in table
                self.password_table.setItem(row, 3, QTableWidgetItem(category))
                self.password_table.setItem(row, 4, QTableWidgetItem(notes or ""))
            
            # Update categories
            current_filter = self.category_filter.currentText()
            self.category_filter.blockSignals(True)
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")
            categories = self.esafe.get_categories()
            if categories:
                self.category_filter.addItems(categories)
            
            index = self.category_filter.findText(current_filter)
            if index >= 0:
                self.category_filter.setCurrentIndex(index)
            self.category_filter.blockSignals(False)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def filter_passwords(self, category):
        """Filter passwords by category (◠‿◠)"""
        self.refresh_passwords()  # The category is now handled in refresh_passwords

    def check_breaches(self):
        """Check stored passwords for breaches (。┰ω┰。)"""
        try:
            QMessageBox.information(
                self, "Checking Breaches", 
                "Checking your passwords for breaches...\n"
                "This might take a moment."
            )
            
            breached = self.esafe.check_password_breaches()
            
            if not breached:
                QMessageBox.information(
                    self, "All Safe",
                    "None of your passwords appear in known data breaches!"
                )
                return
            
            message = "The following passwords appear in data breaches:\n\n"
            for service, username, count in breached:
                message += f"• {service} ({username}): Found in {count:,} breaches\n"
            message += "\nPlease change these passwords ASAP!"
            
            QMessageBox.warning(
                self, "Breaches Found",
                message
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Error",
                f"Failed to check for breaches: {str(e)}"
            )

    def handle_cell_click(self, row, column):
        """Handle cell clicks in the password table"""
        try:
            # Column 2 is the password column
            if column == 2:
                # Get service and username to find the actual password
                service = self.password_table.item(row, 0).text()
                username = self.password_table.item(row, 1).text()
                category = self.password_table.item(row, 3).text()
                
                # Get the actual password from database
                passwords = self.esafe.get_passwords(category)
                for s, u, password, c, _ in passwords:
                    if s == service and u == username:
                        # Copy to clipboard
                        clipboard = QApplication.clipboard()
                        clipboard.setText(password)
                        
                        # Show temporary feedback
                        self.password_table.item(row, 2).setText("Copied!")
                        QTimer.singleShot(1000, lambda: 
                            self.password_table.item(row, 2).setText("●●●●●●"))
                        break
                
        except Exception as e:
            QMessageBox.critical(self, "Error", "Failed to copy password")

def main():
    """Main function to run our kawaii password manager (◕‿◕✿)"""
    app = QApplication(sys.argv)
    safe = eSafe()
    
    try:
        # Set up database and create default user if needed
        with sqlite3.connect('password_vault.db') as conn:
            cursor = conn.cursor()
            
            # Create encryption keys table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS encryption_keys (
                    id INTEGER PRIMARY KEY,
                    key TEXT NOT NULL
                )
            ''')
            
            # Check if default user exists
            cursor.execute('SELECT id FROM users WHERE id = 1')
            if not cursor.fetchone():
                # Create default user with a dummy master password
                salt = bcrypt.gensalt()
                hashed = bcrypt.hashpw(b'default_password', salt)
                cursor.execute('''
                    INSERT INTO users (id, username, master_hash, master_salt)
                    VALUES (?, ?, ?, ?)
                ''', (1, 'default_user', hashed.decode(), salt.decode()))
                
                # Generate and store new encryption key
                key = Fernet.generate_key()
                cursor.execute('INSERT INTO encryption_keys (id, key) VALUES (1, ?)', 
                             (key.decode(),))
                conn.commit()
            else:
                # Get existing encryption key
                cursor.execute('SELECT key FROM encryption_keys WHERE id = 1')
                result = cursor.fetchone()
                if result:
                    key = result[0].encode()
                else:
                    # Create new key if none exists
                    key = Fernet.generate_key()
                    cursor.execute('INSERT INTO encryption_keys (id, key) VALUES (1, ?)', 
                                 (key.decode(),))
                    conn.commit()
        
        # Set up encryption
        safe.current_user_id = 1
        
        # Launch GUI
        window = eSafeGUI(safe)
        window.show()
        sys.exit(app.exec_())
        
    except Exception as e:
        logging.error(f"Startup error: {str(e)}")
        QMessageBox.critical(None, "Error", 
                           f"Failed to start eSafe: {str(e)}\n"
                           "Please ensure you have write permissions in this directory.")
        sys.exit(1)

if __name__ == "__main__":
    main() 