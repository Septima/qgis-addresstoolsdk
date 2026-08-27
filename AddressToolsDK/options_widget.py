# -*- coding: utf-8 -*-
# /***************************************************************************
#  AddressToolsDK - QGIS Plugin
#  Options page: lets users configure their own Adressevælger token.
#  Copyright: (C) 2019 by Septima
# ***************************************************************************/

import os
from qgis.PyQt import uic
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QLineEdit, QToolButton
from qgis.core import QgsSettings
from qgis.gui import QgsOptionsPageWidget, QgsOptionsWidgetFactory
from .addresstoolsdk_api import DEFAULT_TOKEN, SETTINGS_GROUP, TOKEN_SETTINGS_KEY

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "ui", "options_widget.ui")
)


class AddressToolsDKOptionsWidget(QgsOptionsPageWidget, FORM_CLASS):
    """Options page for the AddressToolsDK plugin."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._setup_token_field()
        self.load_settings()

    def _setup_token_field(self):
        """Mask the token like a password field, with an eye-toggle to reveal it."""
        self.tokenInput.setEchoMode(QLineEdit.EchoMode.Password)

        btn = QToolButton(self)
        btn.setText("👁")
        btn.setCheckable(True)
        btn.setToolTip("Vis/skjul token")
        btn.setFixedWidth(28)
        btn.toggled.connect(
            lambda checked: self.tokenInput.setEchoMode(
                QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
            )
        )
        self.gridLayout.addWidget(btn, 0, 3)

    def load_settings(self):
        """Load the token from QgsSettings, pre-filled with the shared default token if not yet set."""
        settings = QgsSettings()
        settings.beginGroup(SETTINGS_GROUP)
        self.tokenInput.setText(settings.value(TOKEN_SETTINGS_KEY, DEFAULT_TOKEN))
        settings.endGroup()

    def apply(self):
        """Called by QGIS when OK or Apply is clicked in the options dialog."""
        self.save_settings()

    def save_settings(self):
        """Persist the token to QgsSettings, so AdresseVaelgerClient picks it up."""
        settings = QgsSettings()
        settings.beginGroup(SETTINGS_GROUP)
        settings.setValue(TOKEN_SETTINGS_KEY, self.tokenInput.text().strip())
        settings.endGroup()
        settings.sync()


class AddressToolsDKOptionsFactory(QgsOptionsWidgetFactory):
    """Registers the AddressToolsDK page under QGIS' Settings > Options dialog."""

    def icon(self):
        return QIcon()

    def createWidget(self, parent):
        return AddressToolsDKOptionsWidget(parent)

    def title(self):
        return "AddressToolsDK"

