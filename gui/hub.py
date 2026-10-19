"""Hub GUI — launches every EagleSpyBaran tool."""
import os
import subprocess
import sys
import tkinter as tk

from gui import common as C

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = [
    ("🖥️", "الأجهزة المتصلة", "devices_gui.py",
     "قائمة الأجهزة وحالة التصريح"),
    ("🔍", "Find Name", "find_gui.py",
     "بحث في التطبيقات المثبتة بالاسم أو الحزمة"),
    ("🖥", "الشاشة", "screen_gui.py",
     "لقطة شاشة + تسجيل الشاشة (إشعار ظاهر على الهاتف)"),
    ("🧾", "التدقيق الشامل", "audit_gui.py",
     "جرد كامل + صلاحيات حساسة + تقرير HTML"),
]


def main():
    root = tk.Tk()
    C.setup_window(root, "المشغل الرئيسي", 620, 470)
    C.header(root, "EagleSpyBaran — المشغل الرئيسي",
             "اختر الأداة — تعمل على أجهزتك أنت فقط، بشفافية كاملة")
    for icon, name, script, desc in TOOLS:
        row = tk.Frame(root, bg=C.PANEL, highlightthickness=1,
                       highlightbackground=C.LINE)
        row.pack(fill="x", padx=14, pady=6)
        tk.Label(row, text=icon, bg=C.PANEL, fg=C.GRN,
                 font=("Segoe UI", 16)).pack(side="right", padx=(4, 10), pady=8)
        tf = tk.Frame(row, bg=C.PANEL)
        tf.pack(side="right", fill="x", expand=True)
        tk.Label(tf, text=name, bg=C.PANEL, fg=C.TXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="e")
        tk.Label(tf, text=desc, bg=C.PANEL, fg=C.MUT,
                 font=("Segoe UI", 9), wraplength=380, justify="right"
                 ).pack(anchor="e")
        tk.Button(row, text="تشغيل ▶", bg=C.GRN, fg="#06281c",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12,
                  cursor="hand2",
                  command=lambda s=script: launch(s)).pack(side="left", padx=10)

    st = tk.Label(root, text="", bg=C.BG, fg=C.MUT, font=("Segoe UI", 9))
    st.pack(side="bottom", pady=(0, 40))

    def launch(script):
        py = sys.executable or "python3"
        subprocess.Popen([py, os.path.join(HERE, script)], cwd=HERE)
        st.configure(text="▶ تم فتح: " + name_of(script))

    def name_of(script):
        for _i, n, s, _d in TOOLS:
            if s == script:
                return n
        return script

    tk.Label(root, text="المتطلبات: adb مثبت + USB debugging مفعّل + قبول "
                        "النافذة على الهاتف", bg=C.BG, fg=C.MUT,
             font=("Segoe UI", 9)).pack(side="bottom", pady=2)
    C.footer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
