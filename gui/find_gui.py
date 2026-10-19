"""Find Name GUI — search installed packages by name."""
import tkinter as tk

import adbkit
from gui import common as C


def main():
    root = tk.Tk()
    C.setup_window(root, "Find Name", 640, 520)
    C.header(root, "Find Name — البحث في التطبيقات",
             "ابحث باسم الحزمة أو جزء منها (مثل bank / whatsapp / game)")
    bar, get_sel, _refresh = C.device_bar(root)
    row = tk.Frame(root, bg=C.BG)
    row.pack(fill="x", padx=12)
    q = tk.StringVar()
    tk.Entry(row, textvariable=q, bg=C.PANEL, fg=C.TXT, relief="flat",
             font=("Consolas", 12), insertbackground=C.TXT).pack(
        side="right", fill="x", expand=True, ipady=6)
    txt = C.output_box(root)

    def go():
        dev = get_sel()
        needle = q.get().strip()
        if not dev:
            C.log(txt, "⛔ اختر جهازاً أولاً.")
            return
        if not needle:
            C.log(txt, "✏️ اكتب كلمة البحث.")
            return
        C.log(txt, "[*] بحث عن '%s'…" % needle)

        def work():
            return adbkit.find_name(dev, needle)
        C.run_async(work, on_done)

    def on_done(res):
        ok, hits = res
        if not ok:
            C.log(txt, "[!] " + hits)
            return
        C.log(txt, "النتائج: %d" % len(hits))
        for p in hits:
            C.log(txt, "  " + p)

    C.action_button(root, "🔍 بحث", go).pack(pady=4)
    root.bind("<Return>", lambda e: go())
    C.footer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
