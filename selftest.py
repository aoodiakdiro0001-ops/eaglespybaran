"""Offline tests: adbkit parsing + report writing (no device needed)."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import adbkit
import report


class FakeP:
    def __init__(self, out, err=b"", rc=0):
        self.stdout = out.encode()
        self.stderr = err.encode()
        self.returncode = rc


def test_parsers():
    # devices parsing
    orig = adbkit.run
    adbkit.run = lambda *a, **k: "List of devices attached\nR58T\tdevice\nxyz\toffline\n"
    devs = adbkit.devices()
    assert devs == [{"serial": "R58T", "state": "device"},
                    {"serial": "xyz", "state": "offline"}], devs

    # getprop parsing
    adbkit.run = lambda *a, **k: (
        "[ro.build.version.release]: [15]\n[ro.product.model]: [S25 Ultra]\n"
        "[ro.product.brand]: [samsung]\n[ro.build.version.security_patch]: [2026-09-01]\n"
        "[ro.product.cpu.abi]: [arm64-v8a]\n[persist.other]: [x]\n")
    info = adbkit.props("R58T")
    assert info == {"release": "15", "model": "S25 Ultra", "brand": "samsung",
                    "security_patch": "2026-09-01", "abi": "arm64-v8a"}, info

    # packages parsing
    adbkit.run = lambda *a, **k: "package:com.whatsapp\npackage:com.bank.app\n"
    pkgs = adbkit.packages("R58T", third_party_only=True)
    assert pkgs == ["com.bank.app", "com.whatsapp"], pkgs
    adbkit.run = lambda *a, **k: "package:com.whatsapp\npackage:com.bank.app\n"
    hits = adbkit.find_name("R58T", "BANK")
    assert hits == ["com.bank.app"], hits

    # battery + storage parsing
    adbkit.run = lambda *a, **k: (
        "level: 77\ntemperature: 295\nAC powered: false\nUSB powered: true\n")
    b = adbkit.battery("R58T")
    assert b["level_%"] == "77" and b["temp_C"] == 29.5, b
    adbkit.run = lambda *a, **k: (
        "Filesystem  Size  Used  Avail  Use%  Mounted on\n"
        "/dev/block  500G  210G  290G   42%   /data\n")
    s = adbkit.storage("R58T")
    assert s["total"] == "500G" and s["use_%"] == "42%", s

    # permission detection: any dangerous perm requested by the package
    adbkit.run = lambda *a, **k: (
        "requested permissions:\n"
        "  android.permission.CAMERA: granted=true\n"
        "  android.permission.RECORD_AUDIO: granted=false\n"
        "  android.permission.READ_SMS: granted=true\n"
        "  install permissions:\n")
    g = adbkit.pkg_permissions("R58T", "com.x")
    assert g == ["RECORD_AUDIO", "CAMERA", "READ_SMS"], g

    adbkit.run = orig
    print("PARSER TESTS PASS")


def test_report():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "r.html")
    report.write({"model": "S25 Ultra", "brand": "samsung", "release": "15",
                  "security_patch": "2026-09-01"},
                 ["com.bank.app", "com.x"], {"level_%": "77", "temp_C": 29.5},
                 {"used": "210G", "total": "500G"},
                 {"com.bank.app": ["CAMERA", "READ_SMS"]}, p)
    html = open(p, encoding="utf-8").read()
    for s in ("Baran Avisat", "S25 Ultra", "com.bank.app",
              "TR10 0001 0090 1008 4013 0050 01"):
        assert s in html, s
    print("REPORT TEST PASS")


if __name__ == "__main__":
    test_parsers()
    test_report()
    print("SELFTEST DONE")
