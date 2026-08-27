# -*- coding: utf-8 -*-

"""
Client for the Klimadatastyrelsen "Adressevask" and "Adressevælger" services,
replacing the old DAWA-based lookups.

Adressevask: https://confluence.kds.dk/display/ADV/Adressevask
Adressevælger (opslag med ID): https://confluence.kds.dk/pages/viewpage.action?pageId=246743156
"""

import json
from urllib.parse import quote
from qgis.PyQt.QtCore import QUrl
from qgis.PyQt.QtNetwork import QNetworkRequest, QNetworkReply
from qgis.core import Qgis, QgsMessageLog, QgsNetworkAccessManager, QgsPoint, QgsSettings

# Tag used for messages in QGIS' "Log Messages" panel (Panels > Log Messages) - select it in the tab dropdown.
LOG_TAG = "AddressToolsDK"

# QgsSettings location of the user-configurable token, set via Indstillinger > Muligheder > AddressToolsDK.
SETTINGS_GROUP = "AddressToolsDK"
TOKEN_SETTINGS_KEY = "adressevaelger_token"
# Per advise of the service owner, this shared token is currently used for all purposes and works out of
# the box - the settings page only needs to be used if/when Adressevælger starts requiring individual tokens.
DEFAULT_TOKEN = "adressevaelger123"

# Coordinate reference system used by the adgangspunkt coordinates returned by the API.
ADGANGSPUNKT_CRS = "EPSG:25832"


def flatten_adresse(opslag):
    """Flattens an /adresser/{id} response into the attributes we expose, plus an accesspoint QgsPoint."""
    adresse = (opslag or {}).get("adresse") or {}
    husnummer = adresse.get("husnummer") or {}
    adgangspunkt = husnummer.get("adgangspunkt") or {}
    postnummer = husnummer.get("postnummer") or {}
    kommunedel = husnummer.get("navngivenvejkommunedel") or {}
    supplerende = husnummer.get("supplerendebynavn") or {}
    coords = (adgangspunkt.get("geometri") or {}).get("coordinates")
    point = QgsPoint(float(coords[0]), float(coords[1])) if coords else None
    return {
        "adresse_id": adresse.get("id_lokalid"),
        "adresse_betegnelse": adresse.get("adressebetegnelse"),
        "etage": adresse.get("etagebetegnelse"),
        "dor": adresse.get("doerbetegnelse"),
        "adresse_status": adresse.get("status"),
        "husnummer_id": husnummer.get("id_lokalid"),
        "husnummertekst": husnummer.get("husnummertekst"),
        "adgangsadressebetegnelse": husnummer.get("adgangsadressebetegnelse"),
        "vejnavn": husnummer.get("vejnavn"),
        "husnummer_status": husnummer.get("status"),
        "postnr": postnummer.get("postnr"),
        "postnummer_navn": postnummer.get("navn"),
        "kommunekode": kommunedel.get("kommune"),
        "vejkode": kommunedel.get("vejkode"),
        "supplerende_bynavn": supplerende.get("navn"),
        "accesspoint": point
    }


class AdresseVaelgerClient():
    BASE_URL = "https://adressevaelger.dk"

    def _token(self):
        """Returns the user-configured token from the options page, or the shared default token."""
        settings = QgsSettings()
        settings.beginGroup(SETTINGS_GROUP)
        token = settings.value(TOKEN_SETTINGS_KEY, "") or ""
        settings.endGroup()
        return token.strip() or DEFAULT_TOKEN

    def _get_json(self, url):
        """GETs url and returns the parsed JSON, or None on a network error or invalid response body."""
        QgsMessageLog.logMessage(f"Kalder: {url}", LOG_TAG, Qgis.Info)
        request = QNetworkRequest(QUrl(url))
        reply = QgsNetworkAccessManager.blockingGet(request)
        status = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        raw = bytes(reply.content())
        if reply.error() != QNetworkReply.NetworkError.NoError:
            QgsMessageLog.logMessage(
                f"Netværksfejl ved kald til {url}: {reply.errorString()} (HTTP {status})",
                LOG_TAG, Qgis.Warning
            )
            return None
        QgsMessageLog.logMessage(
            f"Svar fra {url} (HTTP {status}, {len(raw)} bytes): {raw[:500]!r}",
            LOG_TAG, Qgis.Info
        )
        try:
            return json.loads(str(raw, encoding="utf-8"))
        except json.JSONDecodeError:
            QgsMessageLog.logMessage(
                f"Kunne ikke parse JSON-svar fra {url} (HTTP {status})",
                LOG_TAG, Qgis.Critical
            )
            return None

    def wash_uri(self, address):
        trimmed = address.strip() if address else None
        if not trimmed:
            return None
        return f"{self.BASE_URL}/vask/?token={self._token()}&adresse={quote(trimmed)}"

    def adresse_uri(self, id):
        return f"{self.BASE_URL}/adresser/{quote(id)}?token={self._token()}"

    def wash(self, address):
        """Calls Adressevask with a free-text address. Returns the parsed JSON, or None if address is empty."""
        url = self.wash_uri(address)
        if not url:
            return None
        return self._get_json(url)

    def address_from_id(self, id):
        """Calls Adressevælger's opslag-med-id for an adresse id_lokalid. Returns the parsed JSON."""
        if not id:
            return None
        return self._get_json(self.adresse_uri(id))

    def geocode(self, address):
        """Washes a free-text address and looks up its coordinates. Returns a flat dict, or None if address is empty.

        vaskestatus_kode/vaskestatus_tekst are always present in the result, replacing the old DAWA A/B/C
        kategori - they're returned even when the wash finds no match (negative kode), so callers can see why.
        The other attributes (adresse_id, adresse_betegnelse, accesspoint, ...) are only populated on a match.

        Adressevask matches both current and historic adressebetegnelser - if the input matched a historic
        betegnelse, "vaskeresultat_historisk" in the API response holds that old betegnelse and its validity
        period, which is surfaced here as historisk_adressebetegnelse/historisk_virkningfra/historisk_virkningtil.
        """
        washed = self.wash(address)
        if not washed:
            return None
        vaskestatus = washed.get("vaskestatus") or {}
        kode = vaskestatus.get("kode")
        result = {
            "vaskestatus_kode": kode,
            "vaskestatus_tekst": vaskestatus.get("tekst"),
            "adresse_id": None,
            "adresse_betegnelse": None,
            "historisk_adressebetegnelse": None,
            "historisk_virkningfra": None,
            "historisk_virkningtil": None,
            "accesspoint": None,
        }
        if kode is None or kode < 0:
            return result
        vaskeresultat = washed.get("vaskeresultat") or {}
        id = vaskeresultat.get("adresse_id_lokalid")
        if not id:
            return result
        # Vaskeresultatet giver i sig selv id og betegnelse - bevar dem selvom opslaget herunder fejler.
        result["adresse_id"] = id
        result["adresse_betegnelse"] = vaskeresultat.get("adressebetegnelse")
        opslag = self.address_from_id(id)
        if not opslag:
            return result
        result.update(flatten_adresse(opslag))
        historisk = washed.get("vaskeresultat_historisk") or {}
        result["historisk_adressebetegnelse"] = historisk.get("adressebetegnelse")
        result["historisk_virkningfra"] = historisk.get("virkningfra")
        result["historisk_virkningtil"] = historisk.get("virkningtil")
        return result

