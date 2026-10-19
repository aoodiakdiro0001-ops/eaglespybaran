#!/usr/bin/env python3
"""EagleSpyBaran CLI — audit YOUR connected Android device via ADB.

Commands:
  python3 main.py devices              # قائمة الأجهزة المتصلة
  python3 main.py find <اسم أو حزمة>   # Find Name
  python3 main.py shot                 # لقطة شاشة للجهاز
  python3 main.py record [ثواني]       # تسجيل شاشة (إشعار ظاهر على الهاتف)
  python3 main.py audit [-d SERIAL]    # تقرير كامل HTML
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import adbkit
import report

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")


def cmd_devices(_a):
    devs = adbkit.devices()
    if not devs:
        print("لا يوجد جهاز. فعّل USB debugging + اقبل النافذة على الهاتف.")
        return
    for d in devs:
        print("%-20s %s" % (d["serial"], d["state"]))


def cmd_find(a):
    dev = adbkit.pick_device(a.serial)
    hits = adbkit.find_name(dev, a.needle)
    print("الجهاز: %s — نتائج البحث عن '%s' (%d):" % (dev, a.needle, len(hits)))
    for p in hits:
        print("  " + p)


def cmd_shot(a):
    dev = adbkit.pick_device(a.serial)
    p = adbkit.screenshot(dev, OUT)
    print("[+] لقطة الشاشة: %s" % p if p else "[!] فشلت اللقطة")


def cmd_record(a):
    dev = adbkit.pick_device(a.serial)
    sec = max(3, min(int(a.seconds or 10), 180))
    print("[*] تسجيل %d ثانية — إشعار التسجيل سيظهر على شاشة الهاتف..." % sec)
    p = adbkit.screenrecord(dev, OUT, sec)
    print("[+] التسجيل: %s" % p if p else "[!] فشل التسجيل")


def cmd_audit(a):
    dev = adbkit.pick_device(a.serial)
    print("[*] تدقيق الجهاز:", dev)
    info = adbkit.props(dev)
    pkgs = adbkit.packages(dev, third_party_only=not a.all)
    bat = adbkit.battery(dev)
    sto = adbkit.storage(dev)
    print("[*] فحص الصلاحيات الحساسة لـ %d تطبيق (قد يستغرق دقائق)..." % len(pkgs))
    perms = {}
    for i, p in enumerate(pkgs, 1):
        try:
            g = adbkit.pkg_permissions(dev, p)
            if g:
                perms[p] = g
        except Exception:
            pass
        if i % 25 == 0:
            print("    %d/%d..." % (i, len(pkgs)))
    os.makedirs(OUT, exist_ok=True)
    data = {"device": dev, "info": info, "battery": bat, "storage": sto,
            "packages": pkgs, "sensitive_perms": perms,
            "time": __import__("datetime").datetime.now().isoformat()}
    with open(os.path.join(OUT, "audit.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    html_path = os.path.join(OUT, "audit_report.html")
    report.write(info, pkgs, bat, sto, perms, html_path)
    risky = sorted(perms.items(), key=lambda kv: -len(kv[1]))[:10]
    print("[+] التقرير: %s" % html_path)
    print("[+] أعلى التطبيقات صلاحية حساسة:")
    for p, g in risky:
        print("    %s  [%s]" % (p, ", ".join(g[:6]) + ("…" if len(g) > 6 else "")))


def main():
    ap = argparse.ArgumentParser(prog="eaglespybaran",
                                 description="جرد وفحص أجهزتك عبر ADB")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("devices")
    f = sub.add_parser("find"); f.add_argument("needle"); f.add_argument("-d", "--serial")
    s = sub.add_parser("shot"); s.add_argument("-d", "--serial")
    r = sub.add_parser("record"); r.add_argument("seconds", nargs="?", default="10")
    r.add_argument("-d", "--serial")
    au = sub.add_parser("audit"); au.add_argument("-d", "--serial")
    au.add_argument("--all", action="store_true", help="أدرج تطبيقات النظام أيضاً")
    a = ap.parse_args()
    fn = {"devices": cmd_devices, "find": cmd_find, "shot": cmd_shot,
          "record": cmd_record, "audit": cmd_audit}[a.cmd]
    try:
        fn(a)
    except FileNotFoundError:
        print("[!] adb غير مثبت — ثبته: brew install android-platform-tools")
    except RuntimeError as ex:
        print("[!] %s" % ex)


if __name__ == "__main__":
    main()
