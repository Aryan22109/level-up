# Level Up (Android app)

Daily plan, gym log, DSA tracker, steps, quick calls and weekly review, in a dark
silver theme. Built with plain HTML/JS and wrapped as an Android app with Capacitor.
Reminders use native scheduled notifications, so they ring (with a custom chime)
even when the app is closed.

## Get the APK (easiest: GitHub builds it for you)
1. Create a GitHub repo and push this folder to the `main` branch.
2. Open the repo's **Actions** tab, pick **Build Android APK**, and run it
   (it also runs on every push). Wait 5-10 minutes.
3. Open the finished run and download the **level-up-apk** artifact (a zip with `app-debug.apk`).
4. Copy the APK to your phone, open it, and allow "install unknown apps" for your file manager.
5. Open the app and tap **Turn on reminders**, then allow notifications.

## Make reminders reliable on your phone
- Settings > Apps > Level Up > Battery: set to **Unrestricted** (or "No restrictions").
- Allow **Alarms & reminders** for the app if Android asks.
- Some brands (Xiaomi, Oppo, Vivo, Realme) need "Autostart" turned on for the app.

## Run locally (optional)
Needs Node 20, Java 17 and Android Studio.
```bash
npm install
npx cap add android
npx capacitor-assets generate --android
mkdir -p android/app/src/main/res/raw android/app/src/main/res/drawable
cp assets/chime.wav android/app/src/main/res/raw/chime.wav
cp assets/ic_stat_levelup.png android/app/src/main/res/drawable/
python3 scripts/add_permissions.py
npx cap sync android
npx cap open android      # then press Run in Android Studio
```

## Project layout
- `www/index.html`: the whole app (UI, logic, storage in localStorage)
- `assets/`: icon, splash screen, notification chime
- `capacitor.config.json`: app id, name, notification settings
- `.github/workflows/android.yml`: cloud APK build

## Notes
- This is a debug APK for personal use. Publishing to the Play Store needs a signed release build.
- Data is stored on the phone only. The AI planner needs the FastAPI backend (next step).
