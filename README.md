# 🦅 EagleSpyBaran — جرد وفحص أجهزتك عبر ADB

أداة مالك الجهاز: جرد التطبيقات، Find Name، لقطة وتسجيل الشاشة، فحص
الصلاحيات الحساسة، تقرير HTML — على أجهزتك أنت فقط.
Designed & built by **Baran Avisat** — [SUPPORT](SUPPORT.md)

## الحدود (هي سبب وجود الأداة)
- كل عملية تحتاج سلك USB + تفعيلك الظاهر على شاشة الهاتف — لا تخفي.
- لا دمج في تطبيقات، لا تجسس، لا وصول لأجهزة لا تملكها.
- نفس الوظائف التي طلبتها (Screen / Find Name / الجرد / الصلاحيات / تقرير).

## التشغيل

```bash
brew install android-platform-tools   # أو apt install adb
python3 selftest.py
python3 main.py devices               # فعّل USB debugging + اقبل النافذة
python3 main.py find bank -d SERIAL
python3 main.py shot -d SERIAL
python3 main.py record 15 -d SERIAL   # إشعار التسجيل يظهر على الهاتف
python3 main.py audit -d SERIAL       # out/audit_report.html + audit.json
```
