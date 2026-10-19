"""Screen GUI — screenshot + screenrecord (visible on-device notice)."""
import tkinter as tk

import adbkit
from gui import common as C


def main():
    root = tk.Tk()
    C.setup_window(root, "Screen", 640, 420)
    C.header(root, "الشاشة — لقطة وتسجيل",
             "إشعار التسجيل يظهر على شاشة الهاتف (شفافية كاملة)")
    bar, get_sel, _ = C.device_bar(root)
    txt = C.output_box(root)

    def shot():
        dev = get_sel()
        if not dev:
            C.log(txt, "⛔ اختر جهازاً."); return
        C.log(txt, "[*] لقطة شاشة…")

        def work():
            return adbkit.screenshot(dev, C.OUT)
        C.run_async(work, on_done)

    def rec(sec):
        dev = get_sel()
        if not dev:
            C.log(txt, "⛔ اختر جهازاً."); return
        C.log(txt, "[*] تسجيل %d ثانية — لا تفصل الكابل…" % sec)

        def work():
            return adbkit.screenrecord(dev, C.OUT, sec)
        C.run_async(work, on_done)

    def on_done(res):
        ok, p = res
        C.log(txt, ("[+] حُفظ: %s" % p) if ok and p else "[!] فشل: %s" % p)

    row = tk.Frame(root, bg=C.BG)
    row.pack(pady=4)
    C.action_button(row, "📸 لقطة", shot).pack(side="right", padx=6)
    C.action_button(row, "🎬 تسجيل 10ث", lambda: rec(10)).pack(side="right", padx=6)
    C.action_button(row, "🎬 تسجيل 30ث", lambda: rec(30)).pack(side="right", padx=6)
    C.footer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
