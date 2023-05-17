[app]

title = NETBRIGHT
package.name = netbright
package.domain = org.yebekhe

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ini,ttf
icon.filename = icon.png

version = 1.0.0
requirements = python3, kivy==master, requests, urllib3, dnspython, charset_normalizer==2.1.1, idna, openssl, https://github.com/kivymd/KivyMD/archive/master.zip, python-resources, jnius, plyer

orientation = portrait
fullscreen = 0

android.archs = arm64-v8a
android.build_mode = release

presplash.filename = icon.png
android.presplash_color = #FFFFFF

android.permissions = INTERNET, WAKE_LOCK, FOREGROUND_SERVICE, REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, POST_NOTIFICATIONS

osx.python_version = 3.10
osx.kivy_version = 2.1.0

android.ndk = 25c
android.ndk_api = 21

android.release_artifact = apk

[buildozer]
log_level = 2
