"""HTML report writer — device audit with Baran credit."""
import html
import os
from datetime import datetime

OWNER = ("Designed &amp; built by <b>Baran Avisat</b> (Professional Programmer) · "
         "baranavisat@gmail.com · +90 531 326 37 22 · "
         "<a href='https://wa.me/905313263722'>WhatsApp</a><br>"
         "Support: BTC <code>bc1q8dhtdrndxsl70e97t8grydfe6pjue37zrhzf6c</code>"
         " · USDT-TRC20 <code>TLWdTjqqogkXNEXGiPWsGdjFP6ioycxeWW</code><br>"
         "🏦 TRY <code>TR10 0001 0090 1008 4013 0050 01</code> · "
         "USD <code>TR80 0001 0090 1008 4013 0050 02</code>")


def _e(v):
    return html.escape("" if v is None else str(v))


def write(device_info, packages, battery, storage, perms, out_path):
    prows = "".join("<tr><td>%s</td><td>%s</td></tr>" % (_e(p),
                    ", ".join(sorted(perms.get(p, []))) or "—")
                    for p in packages)
    doc = """<!DOCTYPE html><html lang="ar" dir="rtl"><head><meta charset="utf-8">
<title>EagleSpyBaran — Device Audit</title>
<style>body{{font-family:Tahoma,sans-serif;max-width:1000px;margin:auto;
padding:20px;background:#0b0e17;color:#e3e9f5}}table{{border-collapse:collapse;
width:100%;font-size:12.5px}}td,th{{border:1px solid #2a3557;padding:6px;
text-align:right}}h1,h2{{color:#fff}}.foot{{color:#9aa0a6;font-size:12px;
border-top:1px solid #2a3557;margin-top:20px;padding-top:10px;line-height:2}}
code{{color:#7ef0c4}}</style></head><body>
<h1>🦅 EagleSpyBaran — جرد الجهاز</h1>
<p>الجهاز: <b>{model}</b> ({brand}) · Android {rel} · ترقيع أمني {sec}<br>
البطارية: {bat} · التخزين: {sto}<br>وقت التدقيق: {now}</p>
<h2>التطبيقات المثبتة ({n}) وصلاحياتها الحساسة</h2>
<table><tr><th>الحزمة</th><th>صلاحيات حساسة ممنوحة</th></tr>{rows}</table>
<p class="foot">{owner}<br>LEGAL: أداة فحص لأجهزتك أنت — التشغيل يتطلب
سلك USB وقبولك الظاهر على الشاشة. © Baran Avisat</p>
</body></html>""".format(
        model=_e(device_info.get("model")), brand=_e(device_info.get("brand")),
        rel=_e(device_info.get("release")), sec=_e(device_info.get("security_patch")),
        bat=_e(battery.get("level_%", "?")) + "% / " + _e(battery.get("temp_C", "?")) + "°C",
        sto=_e(str(storage.get("used", "?")) + " / " + str(storage.get("total", "?"))),
        now=datetime.now().strftime("%Y-%m-%d %H:%M"),
        n=len(packages), rows=prows, owner=OWNER)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(doc)
