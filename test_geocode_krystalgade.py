"""
Standalone smoke test for AdresseVaelgerClient, using the plugin's own code.

Run with QGIS' bundled Python (adjust OSGEO4W_ROOT below if your install differs):
    C:\\OSGeo4W\\bin\\python3.exe test_geocode_krystalgade.py
"""
import os
import sys

OSGEO4W_ROOT = os.environ.get("OSGEO4W_ROOT", r"C:\OSGeo4W")
QGIS_PREFIX = os.environ.get("QGIS_PREFIX_PATH", os.path.join(OSGEO4W_ROOT, "apps", "qgis"))

for bin_dir in (os.path.join(OSGEO4W_ROOT, "bin"), os.path.join(QGIS_PREFIX, "bin")):
    if os.path.isdir(bin_dir):
        os.add_dll_directory(bin_dir)
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]

sys.path.append(os.path.join(QGIS_PREFIX, "python"))
sys.path.append(os.path.join(QGIS_PREFIX, "python", "plugins"))

from qgis.core import QgsApplication

QgsApplication.setPrefixPath(QGIS_PREFIX, True)
app = QgsApplication([], False)
app.initQgis()

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(REPO_ROOT, "AddressToolsDK"))

from addresstoolsdk_api import AdresseVaelgerClient

ADDRESS = "Krystalgade 15, 1172 København K"

try:
    client = AdresseVaelgerClient()

    print("== wash() ==")
    washed = client.wash(ADDRESS)
    print(washed)

    print("\n== geocode() ==")
    result = client.geocode(ADDRESS)
    print(result)

    if result and result.get("accesspoint"):
        point = result["accesspoint"]
        print(f"\naccesspoint ({client.__class__.__module__}, EPSG:25832): x={point.x()}, y={point.y()}")
finally:
    app.exitQgis()
