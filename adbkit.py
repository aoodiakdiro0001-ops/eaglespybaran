"""EagleSpyBaran — personal device audit via ADB (YOUR devices only).

Every function requires the device to be yours and physically connected
with USB debugging enabled (a visible auth prompt on the phone screen).
No stealth, no binding, no spying — a device-owner toolkit.
"""
import json
import os
import subprocess
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ADB = os.environ.get("ADB_PATH", "adb")

DANGEROUS = ("RECORD_AUDIO", "CAMERA", "ACCESS_FINE_LOCATION",
             "ACCESS_COARSE_LOCATION", "READ_SMS", "SEND_SMS",
             "READ_CONTACTS", "WRITE_CONTACTS", "READ_CALL_LOG",
             "READ_EXTERNAL_STORAGE", "WRITE_EXTERNAL_STORAGE",
             "READ_PHONE_STATE", "RECEIVE_SMS", "CALL_PHONE",
             "ACCESS_BACKGROUND_LOCATION", "READ_MEDIA_IMAGES",
             "READ_MEDIA_VIDEO", "READ_MEDIA_AUDIO")


def run(args, device=None, timeout=30):
    cmd = [ADB]
    if device:
        cmd += ["-s", device]
    cmd += args
    p = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.decode("utf-8", "replace").strip())
    return p.stdout.decode("utf-8", "replace")


def devices():
    out = run(["devices"])
    devs = []
    for line in out.splitlines()[1:]:
        if "\t" in line:
            serial, st = line.split("\t", 1)
            devs.append({"serial": serial.strip(), "state": st.strip()})
    return devs


def pick_device(serial=None):
    devs = devices()
    if not devs:
        raise RuntimeError("لا يوجد جهاز متصل — فعّل USB debugging واقبل النافذة على الهاتف")
    if serial:
        for d in devs:
            if d["serial"] == serial and d["state"] == "device":
                return serial
        raise RuntimeError("الجهاز المطلوب غير متصل: %s" % serial)
    ok = [d for d in devs if d["state"] == "device"]
    if not ok:
        raise RuntimeError("الجهاز متصل لكن غير مصرح — اقبل نافذة تصحيح USB على الشاشة")
    return ok[0]["serial"]


def props(device):
    out = run(["shell", "getprop"], device=device, timeout=20)
    wanted = ("ro.build.version.release", "ro.product.model",
              "ro.product.brand", "ro.build.version.security_patch",
              "ro.product.cpu.abi")
    info = {}
    for line in out.splitlines():
        if ": [" in line:
            k, v = line.split(": [", 1)
            k = k.strip()
            if k in wanted:
                info[k.split(".")[-1]] = v.rstrip("]").strip()
    return info


def packages(device, third_party_only=True):
    flag = "-3" if third_party_only else ""
    out = run(["shell", "pm", "list", "packages", flag], device=device,
              timeout=30)
    return sorted(l.split(":", 1)[1] for l in out.splitlines()
                  if l.startswith("package:"))


def find_name(device, needle):
    needle = needle.lower().strip()
    return [p for p in packages(device, third_party_only=False)
            if needle in p.lower()]


def battery(device):
    out = run(["shell", "dumpsys", "battery"], device=device, timeout=20)
    info = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            info[k.strip()] = v.strip()
    return {"level_%": info.get("level"),
            "temp_C": round(int(info.get("temperature", 0)) / 10, 1)
            if info.get("temperature", "").isdigit() else "?",
            "powered": info.get("AC powered", "?") + "/" + info.get("USB powered", "?")}


def storage(device):
    out = run(["shell", "df", "-h", "/data"], device=device, timeout=20)
    parts = out.splitlines()[-1].split()
    return {"total": parts[1], "used": parts[2], "free": parts[3],
            "use_%": parts[4]} if len(parts) >= 5 else {}


def pkg_permissions(device, pkg):
    out = run(["shell", "dumpsys", "package", pkg], device=device,
              timeout=25)
    granted = []
    for line in out.splitlines():
        line = line.strip()
        for dgr in DANGEROUS:
            if line.endswith("permission." + dgr) and (
                    "granted=true" in line or "GRANTED" in line
                    or ": granted=true" in line):
                if dgr not in granted:
                    granted.append(dgr)
    return granted


def screenshot(device, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    name = "screen_%s.png" % datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, name)
    with open(path, "wb") as f:
        p = subprocess.run([ADB, "-s", device, "exec-out", "screencap", "-p"],
                           capture_output=True, timeout=30)
        f.write(p.stdout)
    return path if os.path.getsize(path) > 100 else None


def screenrecord(device, out_dir, seconds=10):
    os.makedirs(out_dir, exist_ok=True)
    name = "record_%s.mp4" % datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(out_dir, name)
    subprocess.run([ADB, "-s", device, "shell",
                    "screenrecord", "--time-limit", str(seconds),
                    "/sdcard/_baran_rec.mp4"], timeout=seconds + 25)
    run(["pull", "/sdcard/_baran_rec.mp4", path], device=device)
    run(["shell", "rm", "/sdcard/_baran_rec.mp4"], device=device)
    return path if os.path.exists(path) else None
