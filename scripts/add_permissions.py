"""Adds the Android permissions needed for scheduled reminders."""
path = "android/app/src/main/AndroidManifest.xml"
perms = [
    "android.permission.POST_NOTIFICATIONS",
    "android.permission.SCHEDULE_EXACT_ALARM",
    "android.permission.RECEIVE_BOOT_COMPLETED",
    "android.permission.VIBRATE",
]
xml = open(path, encoding="utf-8").read()
lines = "".join(
    f'    <uses-permission android:name="{p}" />\n' for p in perms if p not in xml
)
xml = xml.replace("</manifest>", lines + "</manifest>")
open(path, "w", encoding="utf-8").write(xml)
print("permissions added")
