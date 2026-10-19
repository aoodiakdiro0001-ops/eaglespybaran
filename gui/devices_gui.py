"""Devices GUI — list connected devices."""
import tkinter as tk

import adbkit
from gui import common as C


def main():
    root = tk.Tk()
    C.setup_window(root, "الأجهزة المتصلة", 560, 380)
    C.header(root, "الأجهزة المتصلة",
             "فعّل USB debugging واقبل النافذة على الهاتف")
    txt = C.output_box(root)

    def refresh():
        C.log(txt, "[*] جارٍ المسح…")
        C.run_async(adbkit.devices, on_done)

    def on_done(res):
        ok, data = res
        if not ok:
            C.log(txt, "[!] " + data)
            return
        if not data:
            C.log(txt, "لا يوجد جهاز متصل.")
            return
        for d in data:
            C.log(txt, "%-22s %s %s" % (d["serial"], "✅" if
                  d["state"] == "device" else "⛔", d["state"]))

    C.action_button(root, "⟳ مسح الآن", refresh).pack(pady=4)
    refresh()
    C.footer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
