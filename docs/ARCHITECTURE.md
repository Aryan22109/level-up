# Architecture notes

## 1. What Capacitor does
Capacitor is a native runtime that wraps a web app. The Android project contains a single `Activity` that hosts a `WebView`. My `www/` folder is copied into the app's assets by `npx cap sync` and served to the WebView from inside the app, so the app works offline.

When JavaScript calls a plugin (for example `LocalNotifications.schedule(...)`), Capacitor's **bridge** serialises the call to JSON, sends it to the native side, runs the matching Java/Kotlin method, and sends the result back to JavaScript as a promise. That bridge is what lets a web page do things a normal page cannot, such as set Android alarms.

`capacitor.config.json` holds the app id (`com.levelup.app`), the app name, the web folder, and plugin settings such as the notification icon and sound.

## 2. How reminders fire when the app is closed
A web page cannot run when it is closed, so the app does not rely on timers in JavaScript (those only exist for the web build). On Android it asks the **LocalNotifications** plugin to schedule real notifications:

1. On start, the app requests the notification permission (Android 13+) and creates a **notification channel** (`reminders`) with high importance, a vibration pattern and the custom sound `chime.wav`.
2. It cancels pending notifications and schedules one repeating notification per timetable block per weekday (Monday to Saturday; Sunday is a rest day). Each uses `schedule: { on: { weekday, hour, minute }, allowWhileIdle: true }`.
3. The plugin hands these to Android's **AlarmManager**. The operating system, not my app, wakes up at the set time and fires a broadcast that shows the notification, even if the app process is dead.
4. After a **reboot**, alarms are lost, so the plugin listens for the boot-completed broadcast and re-registers them. That is why the manifest needs `RECEIVE_BOOT_COMPLETED`.
5. **Exact alarms** (`SCHEDULE_EXACT_ALARM`) are needed for on-the-minute delivery on newer Android versions, and **Doze** and vendor battery savers can delay or kill alarms. That is why the README tells users to set battery use to Unrestricted.

(This is my understanding of the plugin; the source is in the `ionic-team/capacitor-plugins` repository if you want to verify details.)

## 3. What the GitHub Actions workflow does
On every push to `main` (and on version tags) it runs on a fresh Ubuntu machine:
1. **Checkout** the code.
2. **Set up Node 20 and Java 17**, which the Android toolchain needs.
3. **`npm install`** to fetch Capacitor and the plugin.
4. **`npx cap add android`** to generate the native Android project (the `android/` folder is not committed, so the build always starts clean).
5. **`capacitor-assets generate`** to create all icon and splash sizes from the source images.
6. **Custom step** to copy the chime into `res/raw`, add the small notification icon, and add the permissions to `AndroidManifest.xml`.
7. **`cap sync`** to copy `www/` and plugin code into the Android project.
8. **`./gradlew assembleDebug`** to compile the debug APK.
9. **Upload** the APK as an artifact, and on a `v*` tag **attach it to a GitHub Release**.

## 4. Design decisions and trade-offs
- **Vanilla JS in one file.** Fast to build and has no build step. The cost is that the file is large; the next step is splitting it into modules and adding tests.
- **`localStorage`.** Simple and private, but the data lives on one device and is lost if the app is uninstalled. The planned FastAPI backend adds accounts and sync.
- **Debug APK.** Good for personal use and sideloading. A different signing key per build means updates require an uninstall, so a stable signing key is on the roadmap.
- **Native alarms over push notifications.** Reminders are local and predictable, work offline, and need no server.

## 5. Likely interview questions
**Why Capacitor instead of native Android or React Native?**
I already had a working web app, and Capacitor let me ship it as an installable app without rewriting it, while still reaching native features through plugins. For a bigger app with heavy animations I would consider React Native or Kotlin.

**How do notifications survive the app being closed?**
They are scheduled with Android's AlarmManager through the plugin, so the OS fires them. They are re-registered after a reboot, and I request exact-alarm and notification permissions.

**What happens on a restart or when the battery saver is aggressive?**
The boot receiver restores alarms. Some vendors still kill background work, so users are told to disable battery optimisation for the app.

**How would you add sync?**
A FastAPI backend with JWT auth and a database, with the app calling it over HTTPS and keeping a local cache for offline use.

**How would you test it?**
Unit-test the pure logic (streaks, weekly stats) once extracted into modules, and test the reminder flow on a real device. The backend already has pytest tests.
