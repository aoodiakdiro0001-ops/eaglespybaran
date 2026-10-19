"""Shared GUI helpers: device picker, threaded actions, credit footer."""
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk

import adbkit

BG = "#0b0e17"
PANEL = "#141b31"
LINE = "#2a3557"
GRN = "#34d399"
TXT = "#e3e9f5"
MUT = "#8b98b8"
ADB = os.environ.get("ADB_PATH", "adb")
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")


def run_async(fn, on_done=None):
    def worker():
        try:
            res = ("ok", fn())
        except Exception as ex:
            res = ("err", str(ex))
        if on_done:
            on_done(res)
    threading.Thread(target=worker, daemon=True).start()


def setup_window(root, title, w=640, h=480):
    root.title("EagleSpyBaran — " + title)
    root.configure(bg=BG)
    root.geometry("%dx%d" % (w, h))
    root.minsize(w, h)


def header(root, title, subtitle=""):
    f = tk.Frame(root, bg=PANEL)
    f.pack(fill="x")
    tk.Label(f, text="🦅 " + title, bg=PANEL, fg=GRN,
             font=("Segoe UI", 15, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
    if subtitle:
        tk.Label(f, text=subtitle, bg=PANEL, fg=MUT,
                 font=("Segoe UI", 10)).pack(anchor="w", padx=12, pady=(0, 10))


def device_bar(root, on_device=None):
    """Serial dropdown + refresh. Returns (frame, get_selected, refresh_fn)."""
    f = tk.Frame(root, bg=BG)
    f.pack(fill="x", padx=12, pady=8)
    tk.Label(f, text="الجهاز:", bg=BG, fg=TXT,
             font=("Segoe UI", 10)).pack(side="right", padx=(0, 6))
    var = tk.StringVar(value="— اضغط تحديث —")
    box = ttk.Combobox(f, textvariable=var, width=28, state="readonly")
    box.pack(side="right")
    out = tk.Text(f, width=1, height=0, bg=BG, fg=BG, bd=0,
                  highlightthickness=0)  # spacer hack

    def refresh():
        def done(res):
            ok, data = res
            devs = data if ok else []
            serials = [d["serial"] for d in devs if d["state"] == "device"] or \
                      ["— لا يوجد جهاز —"]
            box["values"] = serials
            var.set(serials[0])
            if on_device:
                on_device(serials[0] if devs else None)
        run_async(lambda: adbkit.devices(), done)

    tk.Button(f, text="⟳ تحديث", command=refresh, bg=PANEL, fg=TXT,
              activebackground=LINE, activeforeground=GRN, relief="flat",
              padx=10).pack(side="left", padx=6)

    def get_sel():
        s = var.get()
        return None if s.startswith("—") else s
    refresh()
    return f, get_sel, refresh


def output_box(root):
    f = tk.Frame(root, bg=BG)
    f.pack(fill="both", expand=True, padx=12, pady=8)
    txt = tk.Text(f, bg=PANEL, fg=TXT, font=("Consolas", 11), relief="flat",
                  insertbackground=TXT)
    txt.pack(side="right", fill="both", expand=True)
    sb = tk.Scrollbar(f, command=txt.yview)
    sb.pack(side="left", fill="y")
    txt.configure(yscrollcommand=sb.set)
    return txt


def log(txt, line):
    txt.configure(state="normal")
    txt.insert("1.0", line + "\n")
    txt.configure(state="disabled")


def footer(root):
    f = tk.Frame(root, bg=BG)
    f.pack(fill="x", side="bottom")
    tk.Label(f, bg=BG, fg=MUT, justify="right", font=("Segoe UI", 9), text=(
        "Designed & built by Baran Avisat (Professional Programmer) · "
        "baranavisat@gmail.com · +90 531 326 37 22 · wa.me/905313263722\n"
        "BTC bc1q8dhtdrndxsl70e97t8grydfe6pjue37zrhzf6c · "
        "USDT TLWdTjqqogkXNEXGiPWsGdjFP6ioycxeWW · "
        "TRY TR10 0001 0090 1008 4013 0050 01 · USD TR80 0001 0090 1008 4013 0050 02"
    )).pack(anchor="e", padx=12, pady=6)


def action_button(root, text, cmd):
    return tk.Button(root, text=text, command=cmd, bg=GRN, fg="#06281c",
                     font=("Segoe UI", 11, "bold"), relief="flat", padx=16,
                     activebackground="#6ee7b7", cursor="hand2")
