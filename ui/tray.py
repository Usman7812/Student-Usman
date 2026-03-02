import pystray
from PIL import Image
from PyQt6.QtWidgets import QSystemTrayIcon
from PyQt6.QtGui import QIcon

class TrayManager:
    """
    Simplified tray manager for StudySense.
    """
    def __init__(self, main_window):
        self.main_window = main_window
        # Note: A real implementation would need a 16x16 icon file in assets/icons
        self.tray_icon = QSystemTrayIcon(main_window)
        # self.tray_icon.setIcon(QIcon("assets/icons/app_icon.png"))
        self.tray_icon.setToolTip("StudySense — AI Smart Study Companion")
        self.tray_icon.activated.connect(self.on_tray_click)
        self.tray_icon.show()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.main_window.isVisible():
                self.main_window.hide()
            else:
                self.main_window.show()
                self.main_window.activateWindow()
