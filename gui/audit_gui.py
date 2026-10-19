"""Audit GUI — full device audit + HTML report."""
import os
import subprocess
import sys
import tkinter as tk
from datetime import datetime

import adbkit
import report
from gui import common as C

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    root = tk.Tk()
    C.setup_window(root, "التدقيق الشامل", 680, 520)
    C.header(root, "التدقيق الشامل",
             "جرد + صلاحيات حساسة + تقرير HTML (قد يستغرق دقائق)")
    bar, get_sel, _ = C.device_bar(root)
    txt = C.output_box(root)

    def audit():
        dev = get_sel()
        if not dev:
            C.log(txt, "⛔ اختر جهازاً."); return
        C.log(txt, "[*] قراءة معلومات الجهاز…")

        def work():
            info = adbkit.props(dev)
            pkgs = adbkit.packages(dev)
            bat = adbkit.battery(dev)
            sto = adbkit.storage(dev)
            perms = {}
            for i, p in enumerate(pkgs, 1):
                try:
                    g = adbkit.pkg_permissions(dev, p)
                    if g:
                        perms[p] = g
                except Exception:
                    pass
                if i % 25 == 0:
                    C.log(txt, "    %d/%d تطبيق…" % (i, len(pkgs)))
            os.makedirs(C.OUT, exist_ok=True)
            html_path = os.path.join(C.OUT, "audit_report.html")
            report.write(info, pkgs, bat, sto, perms, html_path)
            return (html_path, len(pkgs), perms)
        C.run_async(work, on_done)

    def on_done(res):
        ok, data = res
        if not ok:
            C.log(txt, "[!] " + data); return
        html_path, n, perms = data
        C.log(txt, "[+] التدقيق اكتمل — %d تطبيق، %d بصلاحيات حساسة" % (
            n, len(perms)))
        C.log(txt, "[+] التقرير: %s" % html_path)
        top = sorted(perms.items(), key=lambda kv: -len(kv[1]))[:10]
        for p, g in top:
            C.log(txt, "  %s [%s]" % (p, ", ".join(g[:6])))
        try:  # open report in default browser
            if sys.platform == "darwin":
                subprocess.Popen(["open", html_path])
        except Exception:
            pass

    C.action_button(root, "🧾 تدقيق شامل الآن", audit).pack(pady=4)
    C.footer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
