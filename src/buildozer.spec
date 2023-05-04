[app]

title = NETBRIGHT
package.name = netbright
package.domain = org.yebekhe

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ini
icon.filename = icon.png

version = 0.5
requirements = python3, kivy==master, requests, urllib3, charset_normalizer==2.1.1, idna, openssl, https://github.com/kivymd/KivyMD/archive/master.zip

orientation = portrait
fullscreen = 0

android.archs = armeabi-v7a
android.build_mode = release

presplash.filename = icon.png
presplash_color = FFFFFF

android.signing.key = netbright.keystore
android.signing.storepass = yebekheishere
android.signing.keypass = yebekheishere

android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE
android.broadcast = org.yebekhe.netbright.intent.action.MAIN
android.service = True

[buildozer]
log_level = 2
